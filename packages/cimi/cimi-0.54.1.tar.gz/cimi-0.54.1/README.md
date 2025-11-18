# CIMI (Kimi CLI Clone)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.13%2B-blue)](https://www.python.org/)

**Cimi** is a CLI agent for software engineering tasks, forked from [kimi-cli](https://github.com/MoonshotAI/kimi-cli).

> **Note**: This is a fork of the original Kimi CLI project, renamed and adapted for separate distribution.

## Key features

- Shell-like UI and shell command execution
- Zsh integration
- [Agent Client Protocol] support
- MCP support
- And more to come...

[Agent Client Protocol]: https://github.com/agentclientprotocol/agent-client-protocol

## Installation

Cimi is published as a Python package on PyPI. We highly recommend installing it with [uv](https://docs.astral.sh/uv/). If you have not installed uv yet, please follow the instructions [here](https://docs.astral.sh/uv/getting-started/installation/) to install it first.

Once uv is installed, you can install Cimi with:

```sh
uv tool install --python 3.13 cimi
```

Run `cimi --help` to check if CIMI is installed successfully.

> **Note**: Due to the security checks on macOS, the first time you run `cimi` command may take 10 seconds or more depending on your system environment.

## Upgrading

Upgrade cimi to the latest version with:

```sh
uv tool upgrade cimi --no-cache
```

## Usage

Run `cimi` command in the directory you want to work on, then send `/setup` to setup Cimi:

After setup, Cimi will be ready to use. You can send `/help` to get more information.

## Differences from kimi-cli

This fork maintains feature parity with the original kim-cli project. The only differences are:

- **Package name**: `cimi` instead of `kimi-cli`
- **Command name**: `cimi` instead of `kimi`
- **Source repository**: Independent fork for separate development

All functionality and features remain the same as the original project.

## Features

### Shell mode

Kimi CLI is not only a coding agent, but also a shell. You can switch the mode by pressing `Ctrl-X`. In shell mode, you can directly run shell commands without leaving Kimi CLI.

> [!NOTE]
> Built-in shell commands like `cd` are not supported yet.

### Zsh integration

You can use Cimi together with Zsh, to empower your shell experience with AI agent capabilities. Please refer to the [zsh-kimi-cli](https://github.com/MoonshotAI/zsh-kimi-cli) plugin for integration instructions.

> **Note**: The zsh plugin is designed for the original kimi-cli but should work with cimi with minimal modifications.

### ACP support

Cimi supports [Agent Client Protocol] out of the box. You can use it together with any ACP-compatible editor or IDE.

For example, to use Cimi with [Zed](https://zed.dev/), add the following configuration to your `~/.config/zed/settings.json`:

```json
{
  "agent_servers": {
    "Cimi": {
      "command": "cimi",
      "args": ["--acp"],
      "env": {}
    }
  }
}
```

Then you can create Cimi threads in Zed's agent panel.

### Using MCP tools

Kimi CLI supports the well-established MCP config convention. For example:

```json
{
  "mcpServers": {
    "context7": {
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "YOUR_API_KEY"
      }
    },
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

Run `cimi` with `--mcp-config-file` option to connect to the specified MCP servers:

```sh
cimi --mcp-config-file /path/to/mcp.json
```

## Development

To develop Cimi, run:

```sh
git clone https://github.com/yourusername/cimi.git
cd cimi

make prepare  # prepare the development environment
```

Then you can start working on Cimi.

Refer to the following commands after you make changes:

```sh
uv run cimi  # run CIMI

make format  # format code
make check   # run linting and type checking
make test    # run tests
make help    # show all make targets
```

## Contributing

We welcome contributions to Cimi! Please fork the repository and submit pull requests.

## Origin and License

Cimi is a fork of [kimi-cli](https://github.com/MoonshotAI/kimi-cli) by Moonshot AI, licensed under the Apache License 2.0.

## LICENSE

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
