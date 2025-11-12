# Daft Cloud SDK

## Usage

```sh
# Initialize a project
ev init

# Run a workflow
ev run my_module.py

# Configure a profile e.g. staging with endpoint overrides
ev configure
```

## Installation

The CLI is installed in the project's virtualenv. It can also be added to a project's `pyproject.toml` with `ev-sdk = { path = "../ev-cloud/ev-sdk", editable = true }`.
You can also run CLI with uv via `uv run ev <command>`.

```toml
dependencies = [ "ev-sdk" ]

[tool.uv.sources]
ev-sdk = { path = "../ev-cloud/ev-sdk", editable = true }
```

## Configuration

The configuration uses profiles and is located at `~/.ev/config.toml` (or `$EV_HOME/config.toml`).

```toml
[default]
profile = "default"

[profiles.default]
endpoint_url = "https://api.daft.ai"
dashboard_url = "https://cloud.daft.ai"

[profiles.development]
endpoint_url = "http://localhost:3000"
dashboard_url = "http://localhost:3003"

[profiles.staging]
endpoint_url = "https://staging.api.daft.ai"
dashboard_url = "https://staging.cloud.daft.ai"
```

### Configuration Fields

- `endpoint_url`: API endpoint URL (defaults to `https://api.daft.ai` if not specified)
- `dashboard_url`: Dashboard UI URL for run links (defaults to `https://cloud.daft.ai` if not specified)

### Manual Configuration

While `ev configure` sets up profile configuration, you can manually edit your config file to:
- Add custom `endpoint_url` and `dashboard_url` values for different environments
- Create multiple profiles for testing, staging, and production
- Switch between local development and hosted environments

## Commands

```sh
# Interactive configuration wizard
ev configure

# Initialize project in current repository
ev init [--template TEMPLATE]

# Run python scripts on Daft Cloud
ev run script.py                    # Python file
ev run module                       # Python module
ev run module:function --key=value  # Function with args

# List resources
ev list projects

# Use specific profile
ev --profile work run script.py
```

## Provider

The Daft Provider is a simple implementation of the Provider interface with
a set of known implementations that are resolved against our control plane.

We can move this into open source post launch, but it doesn't make a difference.

## Configuration

We inject these environment variables to trigger using the Daft Provider.

```sh
DAFT_PROVIDER="daft"
DAFT_PROVIDER_BASE_URL="https://...."
DAFT_PROVIDER_API_KEY="sk-..."
```

| Stage      | Endpoint                                           |
| ---------- | -------------------------------------------------- |
| Tilt       | n/a                                                |
| Staging    | https://ai-eventual-provider-staging.onrender.com/ |
| Production | n/a                                                |
