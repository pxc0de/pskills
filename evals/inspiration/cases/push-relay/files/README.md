# Hearth

Hearth is a self-hosted home automation hub. You run the server on a machine at home, and it talks to your lights, locks and sensors over Zigbee and Matter.

- The server is a single Go binary with a SQLite database.
- The iOS app is published by the Hearth project in the App Store. Every user installs the same app and points it at their own server.
- There are no Hearth accounts and no Hearth cloud. The app reaches the server over the home network or the user's own VPN.

## Status

The app can show state and send commands. It cannot yet notify you when something happens, such as a door opening while you are away.
