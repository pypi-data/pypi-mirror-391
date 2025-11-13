# Onehouse CLI

A command-line tool for executing SQL commands against the Onehouse API with synchronous responses.

## Installation

```bash
pip install onehouse-cli
```

## Setup

**Configure credentials:**
```bash
onehouse-cli-configure
```

This will prompt you for:
- Profile name
- Account UID
- Project UID
- API Key
- API Secret
- Project Region
- User ID
- Request ID
- Environment (production or staging)

**Credentials are stored in:** `~/.onehouse/credentials`

## Usage

**Execute SQL commands:**
```bash
onehouse-cli --command "SHOW LAKES" --profile myprofile
```

**List available profiles:**
```bash
onehouse-cli --list-profiles
```

**Custom timeout (default: 10 minutes):**
```bash
onehouse-cli --command "ALTER OCU SET LIMIT = '3'" --profile myprofile --timeout 5
```

## Features

- **Synchronous execution**: Automatically polls for completion (1s intervals)
- **Multiple profiles**: Store and switch between different API credentials
- **Error handling**: Clear error messages with headers and response details
- **Timeout control**: Configurable wait time for long-running operations
- **Status checking**: Check the status of an existing request by providing its request ID

## Examples

```bash
# Configure first profile
onehouse-cli-configure

# Execute queries
onehouse-cli --command "SHOW LAKES" --profile apex
onehouse-cli --command "DELETE CLUSTER managed_cluster_retail" --profile apex

# Manage profiles
onehouse-cli --list-profiles

# Check status of an existing request
onehouse-cli --check-status "<REQUEST_ID>" --profile myprofile
```