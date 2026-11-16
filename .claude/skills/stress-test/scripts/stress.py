#!/usr/bin/env python3
"""Stress-test agent skills with independent headless Claude Code sessions.

For each test case the script runs a full conversation between two separate
`claude -p` processes: the agent under test, and a simulated user who plays a
persona with facts the agent has to find. It repeats the conversation for each
arm (the skill, no skill, and the previous version of the skill), grades every
run with fresh judge processes, compares arms blind, and writes a report.

No process shares context with another. Every process in one run uses the same
model. Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import shutil
import statistics
import subprocess
import sys
import threading
import time
import tomllib
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parent.parent
PROMPTS = TOOL_ROOT / "agents"
CLAUDE = os.environ.get("STRESS_CLAUDE_BIN", "claude")
END_MARK = "<<END>>"
DEFAULT_TOOLS = ["Read", "Write", "Edit", "Glob", "Grep", "WebSearch", "WebFetch"]
# Tools approved without a prompt. File tools are not listed on purpose: reads are
# allowed inside the working folders and edits inside the sandbox, and nowhere else.
DEFAULT_ALLOWED = ["WebSearch", "WebFetch"]
ARMS = ("skill", "none", "previous")
MAX_FILE_BYTES = 120_000

# Variables that tie a child process to the session that launched this script.
PARENT_SESSION_ENV = {
    "CLAUDECODE", "CLAUDE_PID", "CLAUDE_EFFORT", "CLAUDE_AGENT_SDK_VERSION",
    "CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_CHILD_SESSION", "CLAUDE_CODE_SESSION_ATTENDED",
    "CLAUDE_CODE_MESSAGING_SOCKET", "CLAUDE_CODE_MESSAGING_TOKEN", "CLAUDE_CODE_ENTRYPOINT",
    "CLAUDE_CODE_ARTIFACT", "CLAUDE_CODE_EMIT_SESSION_STATE_EVENTS",
}

# Check types the script runs itself, and the keys each one needs.
CHECK_TYPES = {
    "forbid_in_agent_turns": ("pattern",),
    "max_questions_per_turn": ("max",),
    "require_in_deliverable": ("pattern",),
    "forbid_in_deliverable": ("pattern",),
    "file_unchanged": ("path",),
    "shell": ("run",),
}

print_lock = threading.Lock()


def log(msg: str) -> None:
    with print_lock:
        print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def die(msg: str) -> None:
    sys.exit(f"error: {msg}")


# --------------------------------------------------------------------------
# Loading suites and cases
# --------------------------------------------------------------------------

def load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def skills_with_evals(evals_dir: Path) -> list[str]:
    if not evals_dir.is_dir():
        return []
    return sorted(p.parent.name for p in evals_dir.glob("*/skill.toml"))


def load_suite(skill: str, skills_dir: Path, evals_dir: Path) -> dict:
    suite_dir = evals_dir / skill
    if not (skills_dir / skill / "SKILL.md").is_file():
        die(f"no skill at {skills_dir / skill}")
    if not (suite_dir / "skill.toml").is_file():
        die(f"no test cases for '{skill}'. Expected {suite_dir / 'skill.toml'}")
    suite = load_toml(suite_dir / "skill.toml")
    suite["name"] = skill
    suite["cases"] = []
    for case_file in sorted(suite_dir.glob("cases/*/case.toml")):
        case = load_toml(case_file)
        case["id"] = case_file.parent.name
        case["dir"] = case_file.parent
        suite["cases"].append(case)
    if not suite["cases"]:
        die(f"'{skill}' has a skill.toml but no cases under {suite_dir / 'cases'}")
    return suite


def validate_suite(suite: dict) -> list[str]:
    problems = []
    where = f"evals/{suite['name']}"
    if "{opening}" not in suite.get("baseline_prompt", ""):
        problems.append(f"{where}/skill.toml: baseline_prompt must contain {{opening}}")
    def check_items(items, origin, need, seen):
        for item in items:
            for key in need:
                if key not in item:
                    problems.append(f"{origin}: an entry is missing '{key}'")
            if item.get("kind", "outcome") not in ("outcome", "behaviour"):
                problems.append(f"{origin}: {item.get('id')}: kind must be outcome or behaviour")
            if item.get("id") in seen:
                problems.append(f"{origin}: duplicate id '{item.get('id')}'")
            seen.add(item.get("id"))
            if "type" in need:
                wanted = CHECK_TYPES.get(item.get("type"))
                if wanted is None:
                    problems.append(f"{origin}: {item.get('id')}: unknown type '{item.get('type')}'")
                else:
                    for key in wanted:
                        if key not in item:
                            problems.append(f"{origin}: {item.get('id')}: missing '{key}'")
            if "pattern" in item:
                try:
                    re.compile(item["pattern"])
                except re.error as e:
                    problems.append(f"{origin}: {item.get('id')}: bad regex: {e}")

    shared = set()
    check_items(suite.get("assertions", []), f"{where}/skill.toml assertions", ("id", "text"), shared)
    check_items(suite.get("checks", []), f"{where}/skill.toml checks", ("id", "type"), shared)
    for case in suite["cases"]:
        origin = f"{where}/cases/{case['id']}/case.toml"
        for key in ("opening", "persona"):
            if key not in case:
                problems.append(f"{origin}: missing '{key}'")
        seen = set(shared)
        check_items(case.get("assertions", []), f"{origin} assertions", ("id", "text"), seen)
        check_items(case.get("checks", []), f"{origin} checks", ("id", "type"), seen)
        if case.get("setup") and not (case["dir"] / case["setup"]).is_file():
            problems.append(f"{origin}: setup script {case['setup']} not found")
    return problems


def skill_body(skill_md: Path) -> str:
    text = skill_md.read_text()
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    return text.strip()


# --------------------------------------------------------------------------
# Calling Claude Code
# --------------------------------------------------------------------------

def child_env() -> dict:
    return {k: v for k, v in os.environ.items()
            if k not in PARENT_SESSION_ENV and not k.startswith("ORCA_")}


class ClaudeError(RuntimeError):
    pass


def run_claude(prompt: str, *, model: str, cwd: Path, args: list[str], timeout: int,
               stream: bool = False) -> dict:
    """Run one headless turn. Returns text, ordered events, and the result record."""
    cmd = [CLAUDE, "-p", "--safe-mode", "--model", model, "--permission-prompts", "none"]
    cmd += ["--output-format", "stream-json", "--verbose"] if stream else ["--output-format", "json"]
    cmd += args
    last_error = ""
    for attempt in (1, 2):
        try:
            proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                                  cwd=cwd, timeout=timeout, env=child_env())
        except subprocess.TimeoutExpired:
            last_error = f"timed out after {timeout}s"
            break  # a retry would resume a session that may still be half-written
        out = proc.stdout.strip()
        try:
            parsed = parse_stream(out) if stream else parse_single(out)
        except (ValueError, KeyError) as e:
            last_error = f"unreadable output ({e}); stderr: {proc.stderr.strip()[:400]}"
        else:
            if not parsed["result"].get("is_error"):
                return parsed
            last_error = f"claude reported an error: {str(parsed['result'].get('result'))[:400]}"
        # Only the first turn of a new session is safe to retry as-is.
        if "--resume" in args or attempt == 2:
            break
        time.sleep(5)
        if "--session-id" in args:
            args = list(args)
            args[args.index("--session-id") + 1] = str(uuid.uuid4())
            cmd = cmd[:len(cmd) - len(args)] + args
    raise ClaudeError(last_error)


def parse_single(out: str) -> dict:
    data = json.loads(out)
    if isinstance(data, list):
        data = next(d for d in reversed(data) if d.get("type") == "result")
    return {"text": data.get("result") or "", "events": [], "result": data}


def parse_stream(out: str) -> dict:
    events, result = [], None
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant" and not ev.get("parent_tool_use_id"):
            for block in ev.get("message", {}).get("content", []):
                if block.get("type") == "text" and block.get("text", "").strip():
                    events.append({"type": "text", "text": block["text"].strip()})
                elif block.get("type") == "tool_use":
                    events.append({"type": "tool", "name": block.get("name", "?"),
                                   "input": block.get("input", {})})
        elif ev.get("type") == "result":
            result = ev
    if result is None:
        raise ValueError("no result event")
    for denial in result.get("permission_denials") or []:
        events.append({"type": "denied", "name": denial.get("tool_name", "?"),
                       "input": denial.get("tool_input", {})})
    text = "\n\n".join(e["text"] for e in events if e["type"] == "text")
    return {"text": text or (result.get("result") or ""), "events": events, "result": result}


def structured(parsed: dict) -> dict:
    """Pull the JSON object a judge was asked for out of a result record."""
    res = parsed["result"]
    if isinstance(res.get("structured_output"), dict):
        return res["structured_output"]
    text = parsed["text"]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ClaudeError(f"judge returned no JSON: {text[:300]}")
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError as e:
        raise ClaudeError(f"judge returned bad JSON: {e}")


def cost_of(parsed: dict) -> float:
    return float(parsed["result"].get("total_cost_usd") or 0.0)


class Budget:
    def __init__(self, limit: float | None):
        self.limit, self.spent, self.lock = limit, 0.0, threading.Lock()

    def add(self, usd: float) -> None:
        with self.lock:
            self.spent += usd

    def exhausted(self) -> bool:
        return self.limit is not None and self.spent >= self.limit


# --------------------------------------------------------------------------
# One conversation
# --------------------------------------------------------------------------

def first_message(arm: str, suite: dict, case: dict, skills_root: Path | None) -> str:
    opening = case["opening"].strip()
    if arm == "none":
        return suite["baseline_prompt"].replace("{opening}", opening).strip()
    skill_dir = skills_root / suite["name"]
    return (f"Base directory for this skill: {skill_dir}\n\n"
            f"{skill_body(skill_dir / 'SKILL.md')}\n\n"
            f"ARGUMENTS: {opening}")


def prepare_sandbox(sandbox: Path, case: dict) -> None:
    sandbox.mkdir(parents=True)
    files = case["dir"] / "files"
    if files.is_dir():
        shutil.copytree(files, sandbox, dirs_exist_ok=True)
    if case.get("setup"):
        proc = subprocess.run(["bash", str(case["dir"] / case["setup"])], cwd=sandbox,
                              capture_output=True, text=True, timeout=120)
        if proc.returncode != 0:
            raise ClaudeError(f"setup script failed: {proc.stderr.strip()[:400]}")


def snapshot_files(root: Path) -> dict[str, str]:
    files = {}
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if not p.is_file() or ".git" in rel.parts:
            continue
        if p.stat().st_size > MAX_FILE_BYTES:
            files[str(rel)] = f"(file of {p.stat().st_size} bytes, not shown)"
            continue
        try:
            files[str(rel)] = p.read_text()
        except UnicodeDecodeError:
            files[str(rel)] = "(binary file, not shown)"
    return files


def converse(spec: dict, cfg: dict, budget: Budget) -> dict:
    suite, case, arm = spec["suite"], spec["case"], spec["arm"]
    out_dir: Path = spec["out_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    sandbox: Path = spec["sandbox"]
    sim_cwd = spec["sandbox"].parent / (spec["sandbox"].name + "-user")
    sim_cwd.mkdir(parents=True)
    started = time.time()
    meta = {"skill": suite["name"], "case": case["id"], "arm": arm, "repeat": spec["repeat"],
            "sandbox": str(sandbox), "model": cfg["model"], "status": "ok", "ended": None,
            "cost_usd": 0.0, "error": None}
    turns: list[dict] = []
    before: dict[str, str] = {}
    changed: dict[str, str] = {}
    try:
        prepare_sandbox(sandbox, case)
        before = snapshot_files(sandbox)

        tools = DEFAULT_TOOLS + case.get("extra_tools", suite.get("extra_tools", []))
        allowed = DEFAULT_ALLOWED + case.get("allowed_tools", suite.get("allowed_tools", []))
        agent_args = ["--permission-mode", "acceptEdits",
                      "--tools", ",".join(tools), "--allowedTools", ",".join(allowed)]
        if arm != "none":
            agent_args += ["--add-dir", str(spec["skills_root"])]
        agent_sid, user_sid = str(uuid.uuid4()), str(uuid.uuid4())
        persona_prompt = (PROMPTS / "simulated-user.md").read_text() \
            .replace("{persona}", case["persona"].strip()) \
            .replace("{opening}", case["opening"].strip() or "(you invoked the tool with no message)") \
            .replace("{hidden_facts}", numbered(case.get("hidden_facts", [])) or "(none)")

        def agent_turn(message: str, first: bool) -> dict:
            session = ["--session-id", agent_sid] if first else ["--resume", agent_sid]
            parsed = run_claude(message, model=cfg["model"], cwd=sandbox, stream=True,
                                args=agent_args + session, timeout=cfg["turn_timeout"])
            budget.add(cost_of(parsed))
            meta["cost_usd"] += cost_of(parsed)
            meta.setdefault("model_ids", sorted((parsed["result"].get("modelUsage") or {}).keys()))
            return {"role": "agent", "text": parsed["text"], "events": parsed["events"]}

        def user_turn(message: str, first: bool) -> str:
            session = ["--session-id", user_sid] if first else ["--resume", user_sid]
            parsed = run_claude(message or "(the agent sent no message)", model=cfg["model"],
                                cwd=sim_cwd, timeout=cfg["turn_timeout"],
                                args=["--tools", "", "--system-prompt", persona_prompt] + session)
            budget.add(cost_of(parsed))
            meta["cost_usd"] += cost_of(parsed)
            return parsed["text"].strip()

        turns.append({"role": "user", "text": case["opening"].strip() or f"(invoked {suite['name']})"})
        reply = agent_turn(first_message(arm, suite, case, spec.get("skills_root")), first=True)
        turns.append(reply)
        max_turns = cfg["max_turns"] or case.get("max_user_turns", suite.get("max_user_turns", 12))
        meta["ended"] = "turn_cap"
        for n in range(max_turns):
            said = user_turn(reply["text"], first=(n == 0))
            ending = END_MARK in said
            said = said.replace(END_MARK, "").strip()
            if not said:
                meta["ended"] = "user_ended"
                break
            turns.append({"role": "user", "text": said})
            reply = agent_turn(said, first=False)
            turns.append(reply)
            if ending:
                meta["ended"] = "user_ended"
                break
        after = snapshot_files(sandbox)
        changed = {p: c for p, c in after.items() if before.get(p) != c}
        for command in case.get("capture", suite.get("capture", [])):
            proc = subprocess.run(["bash", "-c", command], cwd=sandbox, capture_output=True,
                                  text=True, timeout=60)
            changed[f"(output of `{command}` after the session)"] = \
                (proc.stdout + proc.stderr).strip()[:MAX_FILE_BYTES]
        meta["user_turns"] = sum(1 for t in turns if t["role"] == "user")
    except Exception as e:  # one broken run must not stop the others
        meta["status"], meta["error"] = "error", f"{type(e).__name__}: {e}"
    meta["seconds"] = round(time.time() - started)
    scrub = [str(spec["skills_root"])] if spec.get("skills_root") else []
    record = {"meta": meta, "turns": turns, "files_before": before, "files_changed": changed,
              "transcript": render_transcript(turns, sandbox, scrub)}
    (out_dir / "transcript.md").write_text(record["transcript"])
    (out_dir / "run.json").write_text(json.dumps(record, indent=2))
    log(f"conversation done  {suite['name']}/{case['id']}/{arm}-{spec['repeat']}  "
        f"{meta['status']}  ended={meta['ended']}  turns={meta.get('user_turns')}  "
        f"${meta['cost_usd']:.2f}  {meta['seconds']}s"
        + (f"  {meta['error']}" if meta["error"] else ""))
    return record


def numbered(items: list[str]) -> str:
    return "\n".join(f"{i}. {s}" for i, s in enumerate(items, 1))


def tool_line(event: dict, sandbox: Path, scrub: list[str]) -> str | None:
    inp = event.get("input") or {}
    detail = ""
    for key in ("query", "url", "file_path", "path", "pattern", "command", "prompt", "description"):
        if inp.get(key):
            detail = str(inp[key])
            break
    # A path into the skill's own folder would tell a judge which arm this is.
    if any(root in json.dumps(inp) for root in scrub):
        return None
    detail = detail.replace(str(sandbox) + "/", "").replace(str(sandbox), ".")
    detail = " ".join(detail.split())
    label = "tool" if event["type"] == "tool" else "refused by the test harness"
    return f"[{label}: {event['name']} {detail[:160]}]".replace(" ]", "]")


def render_transcript(turns: list[dict], sandbox: Path, scrub: list[str]) -> str:
    """The conversation as a reader sees it, with nothing that reveals the arm."""
    parts, n = [], 0
    for turn in turns:
        if turn["role"] == "user":
            n += 1
            parts.append(f"### User, turn {n}\n\n{turn['text']}")
            continue
        lines = []
        for ev in turn.get("events", []):
            if ev["type"] == "text":
                lines.append(ev["text"])
            else:
                line = tool_line(ev, sandbox, scrub)
                if line:
                    lines.append(line)
        body = "\n\n".join(lines) or turn.get("text") or "(no message)"
        body = body.replace(str(sandbox) + "/", "").replace(str(sandbox), ".")
        for root in scrub:
            body = body.replace(root, "<skills>")
        parts.append(f"### Agent, turn {n}\n\n{body}")
    return "\n\n".join(parts) + "\n"


# --------------------------------------------------------------------------
# Grading one run
# --------------------------------------------------------------------------

def strip_code(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return "\n".join(l for l in text.splitlines() if not l.lstrip().startswith(">"))


def mechanical_checks(record: dict, suite: dict, case: dict) -> list[dict]:
    results = []
    agent_texts = [t["text"] for t in record["turns"] if t["role"] == "agent"]
    deliverable = case.get("deliverable", suite.get("deliverable"))
    content = record["files_changed"].get(deliverable) if deliverable else None

    def add(check, verdict, evidence=""):
        results.append({"id": check["id"], "kind": check.get("kind", "outcome"),
                        "source": "check", "text": check.get("why", check["id"]),
                        "verdict": verdict, "evidence": evidence})

    if deliverable:
        add({"id": "deliverable-written", "why": f"The session wrote or changed {deliverable}."},
            "pass" if content is not None else "fail",
            "" if content is not None else f"{deliverable} was not written or not changed")
    if record["meta"]["ended"] == "turn_cap":
        add({"id": "finished-within-turn-limit",
             "why": "The session finished before the turn limit."}, "fail",
            f"still going after {record['meta'].get('user_turns')} user turns")
    else:
        add({"id": "finished-within-turn-limit",
             "why": "The session finished before the turn limit."}, "pass")

    for check in suite.get("checks", []) + case.get("checks", []):
        kind = check["type"]
        if kind == "forbid_in_agent_turns":
            rx = re.compile(check["pattern"])
            hits = [m.group(0).strip() for t in agent_texts for m in rx.finditer(strip_code(t))]
            add(check, "fail" if hits else "pass",
                f"{len(hits)} match(es), for example: " + " | ".join(hits[:4]) if hits else "")
        elif kind == "max_questions_per_turn":
            limit, share = check["max"], check.get("allowed_share", 0.25)
            counts = [strip_code(t).count("?") for t in agent_texts]
            over = [c for c in counts if c > limit]
            bad = bool(counts) and len(over) / len(counts) > share
            add(check, "fail" if bad else "pass",
                f"question marks per agent turn: {counts}; {len(over)} of {len(counts)} over {limit}")
        elif kind in ("require_in_deliverable", "forbid_in_deliverable"):
            if content is None:
                add(check, "na", "no deliverable")
                continue
            found = re.findall(check["pattern"], content)
            if kind.startswith("require"):
                add(check, "pass" if found else "fail", "" if found else "pattern not found")
            else:
                add(check, "fail" if found else "pass",
                    f"{len(found)} match(es): " + " | ".join(map(str, found[:5])) if found else "")
        elif kind == "file_unchanged":
            touched = check["path"] in record["files_changed"] \
                or check["path"] not in snapshot_files(Path(record["meta"]["sandbox"]))
            add(check, "fail" if touched else "pass",
                f"{check['path']} was changed or removed" if touched else "")
        elif kind == "shell":
            proc = subprocess.run(["bash", "-c", check["run"]], cwd=record["meta"]["sandbox"],
                                  capture_output=True, text=True, timeout=60)
            add(check, "pass" if proc.returncode == 0 else "fail",
                (proc.stdout + proc.stderr).strip()[:300])
        else:
            add(check, "na", f"unknown check type {kind}")
    return results


def files_block(files: dict[str, str], empty: str) -> str:
    if not files:
        return empty
    return "\n\n".join(f"<file path=\"{p}\">\n{c}\n</file>" for p, c in files.items())


JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "assertions": {"type": "array", "items": {"type": "object", "properties": {
            "id": {"type": "string"},
            "verdict": {"type": "string", "enum": ["pass", "fail", "na"]},
            "evidence": {"type": "string"}}, "required": ["id", "verdict", "evidence"]}},
        "hidden_facts": {"type": "array", "items": {"type": "object", "properties": {
            "n": {"type": "integer"},
            "came_up_in_conversation": {"type": "boolean"},
            "recorded_in_output": {"type": "boolean"},
            "evidence": {"type": "string"}},
            "required": ["n", "came_up_in_conversation", "recorded_in_output", "evidence"]}},
        "observations": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["assertions", "hidden_facts", "observations"],
}
READER_SCHEMA = {"type": "object", "properties": {
    "questions": {"type": "array", "items": {"type": "string"}}}, "required": ["questions"]}
COMPARE_SCHEMA = {"type": "object", "properties": {
    "output_winner": {"type": "string", "enum": ["A", "B", "tie"]},
    "conversation_winner": {"type": "string", "enum": ["A", "B", "tie"]},
    "why_output": {"type": "string"},
    "why_conversation": {"type": "string"},
    "what_the_loser_did_better": {"type": "string"}},
    "required": ["output_winner", "conversation_winner", "why_output", "why_conversation",
                 "what_the_loser_did_better"]}


def ask_judge(prompt_file: str, payload: str, schema: dict, cfg: dict, budget: Budget,
              scratch: Path) -> dict:
    scratch.mkdir(parents=True, exist_ok=True)
    parsed = run_claude(payload, model=cfg["judge_model"], cwd=scratch, timeout=cfg["turn_timeout"],
                        args=["--tools", "", "--no-session-persistence",
                              "--system-prompt", (PROMPTS / prompt_file).read_text(),
                              "--json-schema", json.dumps(schema)])
    budget.add(cost_of(parsed))
    return structured(parsed)


def grade(record: dict, spec: dict, cfg: dict, budget: Budget) -> dict:
    suite, case = spec["suite"], spec["case"]
    out_dir: Path = spec["out_dir"]
    results = mechanical_checks(record, suite, case)
    assertions = suite.get("assertions", []) + case.get("assertions", [])
    hidden = case.get("hidden_facts", [])
    graded = {"results": results, "hidden_facts": [], "observations": [], "reader_questions": None,
              "errors": []}
    payload = "\n\n".join([
        "## What the user was told to be (the agent never saw this)\n\n" + case["persona"].strip(),
        "## Facts the user held back unless asked\n\n" + (numbered(hidden) or "(none)"),
        "## Files in the working folder before the session\n\n"
        + files_block(record["files_before"], "(none)"),
        "## The conversation\n\n" + record["transcript"],
        "## Files the session wrote or changed\n\n"
        + files_block(record["files_changed"], "(none)"),
        "## Assertions to judge\n\n"
        + "\n".join(f"- id `{a['id']}`: {a['text']}" for a in assertions),
    ])
    try:
        verdicts = ask_judge("judge.md", payload, JUDGE_SCHEMA, cfg, budget, out_dir / "judge-cwd")
        by_id = {v["id"]: v for v in verdicts.get("assertions", [])}
        for a in assertions:
            v = by_id.get(a["id"], {"verdict": "na", "evidence": "the judge returned no verdict"})
            results.append({"id": a["id"], "kind": a.get("kind", "outcome"), "source": "judge",
                            "text": a["text"], "verdict": v["verdict"], "evidence": v["evidence"]})
        facts = {f["n"]: f for f in verdicts.get("hidden_facts", [])}
        for i, text in enumerate(hidden, 1):
            f = facts.get(i, {})
            graded["hidden_facts"].append({
                "n": i, "text": text,
                "came_up": bool(f.get("came_up_in_conversation")),
                "recorded": bool(f.get("recorded_in_output")),
                "evidence": f.get("evidence", "the judge returned no verdict")})
        graded["observations"] = verdicts.get("observations", [])
    except ClaudeError as e:
        graded["errors"].append(f"judge: {e}")

    deliverable = case.get("deliverable", suite.get("deliverable"))
    reader_task = case.get("reader_task", suite.get("reader_task"))
    if reader_task and deliverable and deliverable in record["files_changed"]:
        payload = (f"## Your task\n\n{reader_task.strip()}\n\n"
                   f"## The file\n\n{record['files_changed'][deliverable]}")
        try:
            got = ask_judge("reader.md", payload, READER_SCHEMA, cfg, budget, out_dir / "judge-cwd")
            graded["reader_questions"] = got.get("questions", [])
        except ClaudeError as e:
            graded["errors"].append(f"reader: {e}")
    (out_dir / "grade.json").write_text(json.dumps(graded, indent=2))
    return graded


def compare(case: dict, suite: dict, left: dict, right: dict, cfg: dict, budget: Budget,
            out_file: Path) -> dict:
    """Blind comparison of two runs of one case. `left` is always the skill arm."""
    seed = hashlib.sha256(str(out_file).encode()).digest()
    skill_is_a = random.Random(seed).random() < 0.5
    a, b = (left, right) if skill_is_a else (right, left)

    def side(label, rec):
        return (f"## Session {label}: the conversation\n\n{rec['transcript']}\n\n"
                f"## Session {label}: files written or changed\n\n"
                + files_block(rec["files_changed"], "(none)"))

    payload = "\n\n".join([
        "## Who the user was (neither agent saw this)\n\n" + case["persona"].strip(),
        "## Facts the user held back unless asked\n\n"
        + (numbered(case.get("hidden_facts", [])) or "(none)"),
        "## What the session was for\n\n" + suite.get("purpose", "").strip(),
        side("A", a), side("B", b)])
    verdict = ask_judge("comparator.md", payload, COMPARE_SCHEMA, cfg, budget,
                        out_file.parent / "cwd")

    def translate(winner):
        if winner == "tie":
            return "tie"
        return "skill" if (winner == "A") == skill_is_a else "other"

    result = {"case": case["id"], "against": right["meta"]["arm"],
              "repeat": left["meta"]["repeat"], "skill_was": "A" if skill_is_a else "B",
              "output": translate(verdict["output_winner"]),
              "conversation": translate(verdict["conversation_winner"]),
              "why_output": verdict["why_output"],
              "why_conversation": verdict["why_conversation"],
              "what_the_loser_did_better": verdict["what_the_loser_did_better"]}
    out_file.write_text(json.dumps(result, indent=2))
    return result


# --------------------------------------------------------------------------
# Arms and snapshots
# --------------------------------------------------------------------------

def skill_hash(skills_root: Path, skill: str) -> str:
    """Hash a skill's folder and the neighbouring skills its SKILL.md reads."""
    text = (skills_root / skill / "SKILL.md").read_text()
    folders = sorted({skill, *re.findall(r"\.\./([A-Za-z0-9_-]+)/", text)})
    h = hashlib.sha256()
    for folder in folders:
        for p in sorted((skills_root / folder).rglob("*")):
            if p.is_file():
                h.update(str(p.relative_to(skills_root)).encode())
                h.update(p.read_bytes())
    return h.hexdigest()


def snapshot_previous(previous: str, repo: Path, skills_dir: Path, dest: Path) -> Path | None:
    """Put the previous version of the skills tree in dest. Returns its skills root."""
    if previous == "none":
        return None
    as_dir = Path(previous).expanduser()
    if as_dir.is_dir():
        shutil.copytree(as_dir, dest / "skills")
        return dest / "skills"
    rel = skills_dir.resolve().relative_to(repo.resolve())
    dest.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(["git", "-C", str(repo), "archive", previous, str(rel)],
                             capture_output=True)
    if archive.returncode != 0:
        log(f"no previous arm: git archive {previous} failed: "
            f"{archive.stderr.decode().strip()[:200]}")
        return None
    subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout, check=True)
    return dest / rel


# --------------------------------------------------------------------------
# Aggregating and reporting
# --------------------------------------------------------------------------

def rate(passed: int, total: int) -> str:
    return "n/a" if total == 0 else f"{passed}/{total} ({100 * passed / total:.0f}%)"


def mean(values: list[float]) -> str:
    return "n/a" if not values else f"{statistics.mean(values):.1f}"


def summarise(skill: str, runs: list[dict], comparisons: list[dict]) -> dict:
    arms = {}
    for arm in ARMS:
        mine = [r for r in runs if r["record"]["meta"]["arm"] == arm]
        if not mine:
            continue
        ok = [r for r in mine if r["record"]["meta"]["status"] == "ok"]
        results = [x for r in ok for x in r["grade"]["results"]]

        def tally(kind):
            sel = [x for x in results if x["kind"] == kind and x["verdict"] in ("pass", "fail")]
            return sum(x["verdict"] == "pass" for x in sel), len(sel)

        facts = [f for r in ok for f in r["grade"]["hidden_facts"]]
        reader = [len(r["grade"]["reader_questions"]) for r in ok
                  if r["grade"]["reader_questions"] is not None]
        arms[arm] = {
            "runs": len(mine), "errors": len(mine) - len(ok),
            "outcome": tally("outcome"), "behaviour": tally("behaviour"),
            "facts_recorded": (sum(f["recorded"] for f in facts), len(facts)),
            "facts_came_up": (sum(f["came_up"] for f in facts), len(facts)),
            "reader_questions": reader,
            "user_turns": [r["record"]["meta"].get("user_turns", 0) for r in ok],
            "turn_cap": sum(r["record"]["meta"]["ended"] == "turn_cap" for r in ok),
            "cost": [r["record"]["meta"]["cost_usd"] for r in ok],
            "seconds": [r["record"]["meta"]["seconds"] for r in ok],
        }

    def by_assertion(arm):
        table = {}
        for r in runs:
            m = r["record"]["meta"]
            if m["arm"] != arm or m["status"] != "ok":
                continue
            for x in r["grade"]["results"]:
                if x["verdict"] == "na":
                    continue
                row = table.setdefault(x["id"], {"text": x["text"], "kind": x["kind"],
                                                 "pass": 0, "total": 0, "fails": []})
                row["total"] += 1
                if x["verdict"] == "pass":
                    row["pass"] += 1
                else:
                    row["fails"].append({"case": m["case"], "repeat": m["repeat"],
                                         "evidence": x["evidence"], "dir": r["dir"]})
        return table

    wins = {}
    for c in comparisons:
        w = wins.setdefault(c["against"], {"output": {"skill": 0, "other": 0, "tie": 0},
                                           "conversation": {"skill": 0, "other": 0, "tie": 0}})
        w["output"][c["output"]] += 1
        w["conversation"][c["conversation"]] += 1
    return {"skill": skill, "arms": arms, "wins": wins,
            "assertions": {arm: by_assertion(arm) for arm in arms}}


def verdict_line(summary: dict) -> str:
    arms, wins = summary["arms"], summary["wins"]
    if "skill" not in arms:
        return "The skill arm did not run."
    lines = []
    for other, label in (("none", "no skill"), ("previous", "the previous version")):
        if other not in arms:
            continue
        s, o = arms["skill"]["outcome"], arms[other]["outcome"]
        sr = s[0] / s[1] if s[1] else 0
        orr = o[0] / o[1] if o[1] else 0
        w = wins.get(other, {}).get("output", {"skill": 0, "other": 0, "tie": 0})
        # A gap under ten points, or an even split of comparisons, counts as no difference.
        checks = (sr - orr >= 0.10) - (orr - sr >= 0.10)
        blind = (w["skill"] > w["other"]) - (w["skill"] < w["other"])
        word = {2: "better", 1: "probably better", 0: "not clearly different",
                -1: "probably worse", -2: "worse"}[checks + blind]
        if checks * blind < 0:
            word = "mixed (the checks and the blind comparisons disagree)"
        lines.append(f"Against {label}, the skill is **{word}** on this run: outcome checks "
                     f"{rate(*s)} against {rate(*o)}, and blind output comparisons "
                     f"{w['skill']} won, {w['other']} lost, {w['tie']} tied.")
    n = arms["skill"]["runs"]
    lines.append(f"This rests on {n} run(s) of the skill. Treat a difference of one or two "
                 f"runs as noise.")
    return " ".join(lines)


def write_report(run_dir: Path, cfg: dict, summaries: list[dict], all_runs: dict,
                 all_comparisons: dict, budget: Budget, started: float) -> Path:
    L = [f"# Stress test report", "",
         f"- Run folder: `{run_dir}`. Paths below are relative to it.",
         f"- Model for every agent, simulated user and judge: `{cfg['model']}`"
         + (f" (judges: `{cfg['judge_model']}`)" if cfg["judge_model"] != cfg["model"] else "")
         + (f", resolved to {', '.join(cfg['model_ids'])}" if cfg.get("model_ids") else ""),
         f"- Repeats per case and arm: {cfg['repeats']}",
         f"- Cost: ${budget.spent:.2f}. Time: {round((time.time() - started) / 60)} min.", ""]
    for s in summaries:
        skill, arms = s["skill"], s["arms"]
        runs, comps = all_runs[skill], all_comparisons[skill]
        L += [f"## {skill}", "", verdict_line(s), "", "### Scoreboard", ""]
        names = {"skill": "skill", "none": "no skill", "previous": "previous version"}
        cols = [a for a in ARMS if a in arms]
        L.append("| | " + " | ".join(names[a] for a in cols) + " |")
        L.append("| --- | " + " | ".join("---" for _ in cols) + " |")
        rows = [
            ("Runs (errors)", lambda a: f"{a['runs']} ({a['errors']})"),
            ("Outcome checks passed", lambda a: rate(*a["outcome"])),
            ("Hidden facts recorded in the output", lambda a: rate(*a["facts_recorded"])),
            ("Hidden facts that came up at all", lambda a: rate(*a["facts_came_up"])),
            ("Questions a reader still had (mean, lower is better)",
             lambda a: mean(a["reader_questions"])),
            ("Behaviour checks passed (the skill's own rules)", lambda a: rate(*a["behaviour"])),
            ("User turns (mean)", lambda a: mean(a["user_turns"])),
            ("Runs that hit the turn limit", lambda a: str(a["turn_cap"])),
            ("Cost per run (mean, USD)",
             lambda a: "n/a" if not a["cost"] else f"{statistics.mean(a['cost']):.2f}"),
            ("Minutes per run (mean)", lambda a: mean([x / 60 for x in a["seconds"]])),
        ]
        for label, fn in rows:
            L.append(f"| {label} | " + " | ".join(fn(arms[a]) for a in cols) + " |")
        L.append("")
        L.append("Outcome checks apply to any agent doing this job. Behaviour checks test rules "
                 "only the skill states, so the other arms are expected to fail them.")
        L.append("")

        if s["wins"]:
            L += ["### Blind comparisons", "",
                  "A judge saw two sessions of the same case without knowing which used the skill.",
                  "", "| Skill against | Output: won / lost / tied | Conversation: won / lost / tied |",
                  "| --- | --- | --- |"]
            for other, w in s["wins"].items():
                o, c = w["output"], w["conversation"]
                L.append(f"| {names[other]} | {o['skill']} / {o['other']} / {o['tie']} "
                         f"| {c['skill']} / {c['other']} / {c['tie']} |")
            L.append("")
            lost = [c for c in comps if "other" in (c["output"], c["conversation"])]
            if lost:
                L += ["Where the skill lost:", ""]
                for c in lost:
                    what = [k for k in ("output", "conversation") if c[k] == "other"]
                    L.append(f"- **{c['case']}**, repeat {c['repeat']}, against {names[c['against']]} "
                             f"({' and '.join(what)}): "
                             + " ".join(c[f"why_{k}"] for k in what))
                L.append("")
            better = [c for c in comps if c["what_the_loser_did_better"].strip()
                      and c["output"] == "skill"]
            if better:
                L += ["What the other arm did better even when the skill won:", ""]
                L += [f"- **{c['case']}**, against {names[c['against']]}: "
                      f"{c['what_the_loser_did_better']}" for c in better]
                L.append("")

        table = s["assertions"].get("skill", {})
        failing = sorted((r for r in table.items() if r[1]["pass"] < r[1]["total"]),
                         key=lambda r: r[1]["pass"] / r[1]["total"])
        L += ["### What the skill failed", ""]
        if not failing:
            L += ["Nothing. Every check passed in every run.", ""]
        for aid, row in failing:
            L.append(f"**`{aid}`** ({row['kind']}) failed {row['total'] - row['pass']} of "
                     f"{row['total']} runs. {row['text']}")
            L.append("")
            for f in row["fails"]:
                L.append(f"- {f['case']}, repeat {f['repeat']}: {f['evidence']} "
                         f"(`{Path(f['dir']).relative_to(run_dir)}/transcript.md`)")
            L.append("")

        for other in ("none", "previous"):
            other_table = s["assertions"].get(other)
            if not other_table:
                continue
            worse, same = [], []
            for aid, row in table.items():
                o = other_table.get(aid)
                if not o or not o["total"] or not row["total"]:
                    continue
                sr, orr = row["pass"] / row["total"], o["pass"] / o["total"]
                if sr < orr:
                    worse.append(f"`{aid}` ({rate(row['pass'], row['total'])} against "
                                 f"{rate(o['pass'], o['total'])})")
                elif sr == orr == 1 and other == "none":
                    same.append(f"`{aid}`")
            if worse:
                L += [f"### Checks where the skill did worse than {names[other]}", "",
                      ", ".join(worse), ""]
            if same:
                L += ["### Checks that no skill also passed every time", "",
                      "These do not show the skill adding anything. Either the check is too easy "
                      "or the instruction behind it is not needed.", "", ", ".join(same), ""]

        missed = {}
        for r in runs:
            m = r["record"]["meta"]
            if m["arm"] != "skill" or m["status"] != "ok":
                continue
            for f in r["grade"]["hidden_facts"]:
                if not f["recorded"]:
                    missed.setdefault((m["case"], f["n"], f["text"]), []).append(
                        ("came up but was not written down" if f["came_up"] else "never came up",
                         m["repeat"]))
        if missed:
            L += ["### Hidden facts the skill missed", ""]
            for (case_id, n, text), hits in missed.items():
                L.append(f"- **{case_id}**, fact {n}: {text} "
                         + "; ".join(f"repeat {rep}: {what}" for what, rep in hits))
            L.append("")

        notes = [(r, o) for r in runs if r["record"]["meta"]["arm"] == "skill"
                 for o in r["grade"]["observations"]]
        if notes:
            L += ["### What the judges noticed beyond the checks", ""]
            L += [f"- {r['record']['meta']['case']}, repeat {r['record']['meta']['repeat']}: {o}"
                  for r, o in notes]
            L.append("")

        problems = [(r, r["record"]["meta"]["error"]) for r in runs
                    if r["record"]["meta"]["status"] != "ok"]
        problems += [(r, e) for r in runs for e in r["grade"]["errors"]]
        if problems:
            L += ["### Runs that broke", "",
                  "These are faults in the test run, not in the skill. They are left out of "
                  "the numbers above.", ""]
            L += [f"- {r['record']['meta']['case']}/{r['record']['meta']['arm']}-"
                  f"{r['record']['meta']['repeat']}: {e}" for r, e in problems]
            L.append("")

        L += ["### Transcripts", ""]
        L += [f"- {r['record']['meta']['case']} / {names[r['record']['meta']['arm']]} / repeat "
              f"{r['record']['meta']['repeat']}: "
              f"`{Path(r['dir']).relative_to(run_dir)}/transcript.md`" for r in runs]
        L.append("")
    report = run_dir / "report.md"
    report.write_text("\n".join(L))
    return report


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------

def cmd_list(args) -> None:
    repo = Path(args.repo).resolve()
    skills_dir, evals_dir = repo / args.skills_dir, repo / args.evals_dir
    have = set(skills_with_evals(evals_dir))
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        name = skill_md.parent.name
        if name in have:
            suite = load_suite(name, skills_dir, evals_dir)
            cases = ", ".join(c["id"] for c in suite["cases"])
            print(f"{name}: {len(suite['cases'])} case(s): {cases}")
        else:
            print(f"{name}: no cases yet")


def cmd_check(args) -> None:
    repo = Path(args.repo).resolve()
    skills_dir, evals_dir = repo / args.skills_dir, repo / args.evals_dir
    problems = []
    for name in skills_with_evals(evals_dir):
        problems += validate_suite(load_suite(name, skills_dir, evals_dir))
    if problems:
        print("\n".join(problems))
        sys.exit(1)
    print("all case files are valid")


def cmd_run(args) -> None:
    repo = Path(args.repo).resolve()
    skills_dir, evals_dir = repo / args.skills_dir, repo / args.evals_dir
    names = skills_with_evals(evals_dir) if args.all or not args.skills else args.skills
    if not names:
        die(f"no test cases found under {evals_dir}")
    suites = [load_suite(n, skills_dir, evals_dir) for n in names]
    problems = [p for s in suites for p in validate_suite(s)]
    if problems:
        die("case files are not valid:\n" + "\n".join(problems))
    want_cases = set(args.cases.split(",")) if args.cases else None
    want_arms = args.arms.split(",") if args.arms else list(ARMS)
    for arm in want_arms:
        if arm not in ARMS:
            die(f"unknown arm '{arm}'. Choose from {', '.join(ARMS)}")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    label = "all" if len(names) > 1 else names[0]
    run_dir = Path(args.runs_dir).expanduser() / f"{stamp}-{label}"
    cfg = {"model": args.model, "judge_model": args.judge_model or args.model,
           "repeats": args.repeats, "turn_timeout": args.turn_timeout,
           "max_turns": args.max_turns}

    # Freeze the skills under test, so an edit during the run cannot change them.
    current_root = run_dir / "snap" / "current" / "skills"
    previous_root = None
    if not args.dry_run:
        shutil.copytree(skills_dir, current_root)
        if "previous" in want_arms:
            previous_root = snapshot_previous(args.previous, repo, skills_dir,
                                              run_dir / "snap" / "previous")

    specs = []
    for suite in suites:
        arms = [a for a in want_arms if a != "previous"]
        if "previous" in want_arms and previous_root is not None:
            prev_skill = previous_root / suite["name"]
            if not (prev_skill / "SKILL.md").is_file():
                log(f"{suite['name']}: no previous version at '{args.previous}', skipping that arm")
            elif skill_hash(previous_root, suite["name"]) == skill_hash(current_root, suite["name"]):
                log(f"{suite['name']}: previous version is identical, skipping that arm")
            else:
                arms.append("previous")
        elif "previous" in want_arms and args.dry_run and args.previous != "none":
            arms.append("previous")
        suite["arms"] = arms
        for case in suite["cases"]:
            if want_cases and case["id"] not in want_cases:
                continue
            for arm in arms:
                for rep in range(1, args.repeats + 1):
                    specs.append({
                        "suite": suite, "case": case, "arm": arm, "repeat": rep,
                        "skills_root": {"skill": current_root, "previous": previous_root}.get(arm),
                        "sandbox": run_dir / "sandboxes" / uuid.uuid4().hex[:10],
                        "out_dir": run_dir / "runs" / suite["name"] / case["id"] / f"{arm}-{rep}"})
    if not specs:
        die("nothing to run. Check --cases and --arms")

    print(f"Plan: {len(specs)} conversation(s) on model '{cfg['model']}', "
          f"{args.parallel} at a time.")
    for suite in suites:
        mine = [s for s in specs if s["suite"] is suite]
        cases = sorted({s["case"]["id"] for s in mine})
        print(f"  {suite['name']}: cases {', '.join(cases)}; arms {', '.join(suite['arms'])}; "
              f"{args.repeats} repeat(s)")
    print(f"Run folder: {run_dir}", flush=True)
    if args.dry_run:
        return

    started = time.time()
    budget = Budget(args.max_cost)
    done: list[dict] = []

    def one(spec):
        if budget.exhausted():
            log(f"skipped {spec['out_dir'].name}: cost limit of ${args.max_cost} reached")
            return None
        record = converse(spec, cfg, budget)
        graded = {"results": [], "hidden_facts": [], "observations": [],
                  "reader_questions": None, "errors": []}
        if record["meta"]["status"] == "ok":
            try:
                graded = grade(record, spec, cfg, budget)
            except Exception as e:
                graded["errors"].append(f"grading: {type(e).__name__}: {e}")
        return {"spec": spec, "record": record, "grade": graded, "dir": str(spec["out_dir"])}

    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        for fut in as_completed([pool.submit(one, s) for s in specs]):
            got = fut.result()
            if got:
                done.append(got)
    done.sort(key=lambda r: r["dir"])

    # Blind comparisons: the skill arm against each other arm, same case, same repeat.
    pairs = []
    index = {(r["record"]["meta"]["skill"], r["record"]["meta"]["case"],
              r["record"]["meta"]["arm"], r["record"]["meta"]["repeat"]): r
             for r in done if r["record"]["meta"]["status"] == "ok"}
    for (skill, case_id, arm, rep), run in index.items():
        if arm != "skill":
            continue
        for other in ("none", "previous"):
            if (skill, case_id, other, rep) in index:
                pairs.append((run, index[(skill, case_id, other, rep)]))
    comparisons = {s["name"]: [] for s in suites}

    def one_pair(pair):
        left, right = pair
        m = left["record"]["meta"]
        out = run_dir / "comparisons" / m["skill"] / \
            f"{m['case']}-vs-{right['record']['meta']['arm']}-{m['repeat']}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            return m["skill"], compare(left["spec"]["case"], left["spec"]["suite"],
                                       left["record"], right["record"], cfg, budget, out)
        except ClaudeError as e:
            log(f"comparison failed for {out.name}: {e}")
            return m["skill"], None

    if pairs and not budget.exhausted():
        log(f"running {len(pairs)} blind comparison(s)")
        with ThreadPoolExecutor(max_workers=args.parallel) as pool:
            for skill, result in pool.map(one_pair, pairs):
                if result:
                    comparisons[skill].append(result)

    all_runs = {s["name"]: [r for r in done if r["record"]["meta"]["skill"] == s["name"]]
                for s in suites}
    summaries = [summarise(s["name"], all_runs[s["name"]], comparisons[s["name"]]) for s in suites]
    cfg["model_ids"] = sorted({m for r in done for m in r["record"]["meta"].get("model_ids", [])})
    report = write_report(run_dir, cfg, summaries, all_runs, comparisons, budget, started)
    (run_dir / "results.json").write_text(json.dumps({
        "config": {k: v for k, v in cfg.items()}, "cost_usd": budget.spent,
        "summaries": summaries, "comparisons": comparisons,
        "runs": [{"dir": r["dir"], "meta": r["record"]["meta"], "grade": r["grade"]}
                 for r in done]}, indent=2, default=str))
    latest = run_dir.parent / "latest"
    if latest.is_symlink() or latest.exists():
        latest.unlink()
    latest.symlink_to(run_dir.name)
    print(f"\nCost: ${budget.spent:.2f}")
    print(f"Report: {report}")
    print(f"Skills as tested (use as --previous for the next round): {current_root}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", default=".", help="repository root (default: current folder)")
    ap.add_argument("--skills-dir", default="skills", help="skills folder, relative to the repo")
    ap.add_argument("--evals-dir", default="evals", help="test case folder, relative to the repo")
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="list skills and their cases").set_defaults(fn=cmd_list)
    sub.add_parser("check", help="validate every case file").set_defaults(fn=cmd_check)

    run = sub.add_parser("run", help="run the stress test")
    run.add_argument("skills", nargs="*", help="skills to test (default: every skill with cases)")
    run.add_argument("--all", action="store_true", help="test every skill that has cases")
    run.add_argument("--model", default="sonnet",
                     help="one model for every agent, simulated user and judge (default: sonnet)")
    run.add_argument("--judge-model", help="a different model for judges (default: same as --model)")
    run.add_argument("--repeats", type=int, default=2, help="runs per case and arm (default: 2)")
    run.add_argument("--parallel", type=int, default=4, help="conversations at once (default: 4)")
    run.add_argument("--cases", help="comma-separated case ids to run (default: all)")
    run.add_argument("--arms", help="comma-separated arms: skill, none, previous (default: all)")
    run.add_argument("--previous", default="HEAD",
                     help="previous version to compare with: a git ref, a folder holding a "
                          "skills tree, or 'none' (default: HEAD)")
    run.add_argument("--max-turns", type=int, default=0,
                     help="override the user-turn limit from the case files")
    run.add_argument("--turn-timeout", type=int, default=900, help="seconds per turn (default: 900)")
    run.add_argument("--max-cost", type=float, help="stop starting new work past this many USD")
    run.add_argument("--runs-dir", default="~/.cache/skill-stress-test",
                     help="where run folders go; keep it outside the repo")
    run.add_argument("--dry-run", action="store_true", help="print the plan and stop")
    run.set_defaults(fn=cmd_run)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
