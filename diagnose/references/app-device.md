# App And Device Adapters

Use this reference for live app evidence on mobile, device, desktop, TV, or React Native targets.

These adapters are optional helpers. If neither is installed, continue with tests, logs, browser tooling, command-line repros, or user-provided artifacts where possible.

## Detect Tools

Check availability before suggesting installation:

```bash
command -v argent
command -v agent-device
```

Do not silently install tools. If a preferred adapter is missing, suggest the relevant command and wait for the user to install or approve.

## Defaults

| Target | Preferred adapter |
| --- | --- |
| iOS Simulator | Argent |
| iOS device | agent-device |
| Android Emulator | Argent |
| Android device | agent-device |
| React Native macOS app | agent-device |
| TV app | agent-device |
| Desktop app | agent-device |

## Argent

Prefer Argent when MCP tools are available and the target is an iOS Simulator or Android Emulator, especially for React Native work that needs:

- Metro/CDP logs
- React component tree inspection
- JS evaluation in the app runtime
- profiling
- launch, reload, deep link, or simulator/emulator gestures

Before using Argent, inspect the current environment and current tool docs:

```bash
argent --help
argent tools
```

If Argent is not installed, suggest:

```bash
npx @swmansion/argent init
```

or:

```bash
npm install -g @swmansion/argent
argent init
```

## agent-device

Prefer agent-device for physical devices, macOS, TV, desktop, replayable flows, CI evidence, screenshots/videos, network/log/perf capture, and broad CLI-driven app automation.

Before planning commands, read the installed version's workflow help:

```bash
agent-device --version
agent-device help workflow
```

Escalate to narrower help when relevant:

```bash
agent-device help debugging
agent-device help react-native
agent-device help react-devtools
agent-device help macos
```

If agent-device is not installed, suggest:

```bash
npm install -g agent-device@latest
agent-device help workflow
```

## Tool Choice Notes

- For React Native iOS/Android simulator or emulator diagnosis, start with Argent if its MCP tools are present.
- For physical iOS or Android devices, start with agent-device.
- For React Native macOS apps, start with agent-device.
- For React Native Web or React DOM apps, use browser tooling first. See [browser-react.md](browser-react.md).
