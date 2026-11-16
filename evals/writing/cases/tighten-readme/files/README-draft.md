# 🚀 Tidylog — Your Logs, Reimagined

In today's fast-paced development landscape, logs are more crucial than ever. **Tidylog** is a powerful, robust command-line tool that seamlessly transforms noisy log files into something you can actually read — and it's not just a formatter, it's a whole new way of thinking about your logs.

## ✨ Why Tidylog?

It's worth noting that most log viewers get in your way. Tidylog stays out of it. Whether you're debugging at 2am or doing a post-mortem, Tidylog has you covered, from startup to shutdown.

- **Fast:** Tidylog is significantly faster than `jq`-based pipelines, ensuring a smooth experience.
- **Smart:** It reads newline-delimited JSON (NDJSON) and groups repeated lines, collapsing any line that repeats more than 3 times within 10 seconds into a single line with a count.
- **Flexible:** Experts agree that filtering is key. Tidylog filters by level (`debug`, `info`, `warn`, `error`) and by time window.

## 📦 Installation

Getting started is effortless! Tidylog requires Node.js 20 or later. Simply run:

```
npm install -g tidylog@2
```

## 🛠 Usage

Let's delve into a quick example. The following command showcases the last 24 hours of warnings and errors:

```
tidylog --since 24h --level warn ./logs/app.ndjson
```

Additionally, Tidylog reads its grouping rules from `~/.config/tidylog/rules.toml`. If that file doesn't exist, it leverages the built-in defaults. It exits with code 2 when the input is not valid NDJSON, and it never modifies the input file.

## 🌟 The Future

Tidylog is just getting started. The future of log reading looks brighter than ever — stay tuned!
