# Rohkun CLI

Rohkun is a code analysis tool for detecting endpoints, API calls, and connections in your codebase.

## Installation

```bash
pip install rohkun
```

## Quick Start

1. **Login:**
   ```bash
   rohkun login --token <your-api-token>
   ```

2. **Analyze a project:**
   ```bash
   rohkun run ./your-project
   ```

## Features

- 🔍 **Endpoint Detection**: Automatically detects backend endpoints
- 📡 **API Call Analysis**: Identifies frontend API calls
- 🔗 **Connection Mapping**: Maps frontend calls to backend endpoints
- 💥 **Blast Radius Analysis**: Understand impact of code changes
- 🔒 **Security Scanning**: Detects common security issues
- 📊 **Confidence Levels**: Shows detection confidence (CERTAIN, HIGH, MEDIUM, LOW)

## Usage

```bash
# Analyze current directory
rohkun run

# Analyze specific directory
rohkun run ./path/to/project

# Use different output formats
rohkun run ./project --format rich    # Colored output (default)
rohkun run ./project --format plain   # Plain text
rohkun run ./project --format json    # JSON output

# Don't copy report to clipboard
rohkun run ./project --no-copy
```

## Authentication

Get your API token from [https://rohkun.com](https://rohkun.com) and login:

```bash
rohkun login --token rk_live_...
```

Or use interactive login:

```bash
rohkun login
```

## Configuration

Set environment variables to customize behavior:

- `ROHKUN_API_URL`: API server URL (default: `https://rohkun.com`)
- `ROHKUN_LOG_LEVEL`: Logging level (default: `INFO`)
- `ROHKUN_MAX_DEPTH`: Max directory depth (default: `50`)
- `ROHKUN_MAX_FILE_SIZE_MB`: Max file size in MB (default: `100`)
- `ROHKUN_MAX_FILES`: Max files to analyze (default: `10000`)

## Output Formats

- **rich** (default): Colored terminal output with Rich markup
- **plain**: Plain text output, no colors
- **json**: Machine-readable JSON format

## Requirements

- Python 3.8+
- Valid API token from rohkun.com

## License

MIT

## Support

For issues and questions, visit [https://rohkun.com](https://rohkun.com)

