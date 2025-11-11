# Strayl Lint

> AI-powered API validation tool - never fear API updates again.

Strayl Lint automatically checks if your API integrations match their latest documentation, catching breaking changes before they hit production.

## Quick Start

### 1. Install

```bash
pip install strayl-lint
```

### 2. Get API Key

Visit [strayl.dev/dashboard](https://strayl.dev/dashboard) and generate your API key.

### 3. Annotate Your Code

Add `strayl:doc` comments above API calls:

```python
# strayl:doc https://api.stripe.com/v1/openapi.json
response = requests.post(
    "https://api.stripe.com/v1/charges",
    json={"amount": 2000, "currency": "usd"}
)
```

```javascript
// strayl:doc https://api.github.com/openapi.json
fetch('https://api.github.com/repos/owner/repo', {
  method: 'GET'
})
```

### 4. Run Check

```bash
export STRAYL_API_KEY=sk_live_xxxxx
strayl-lint check
```

## Features

- ✅ **Always Up-to-Date** - Checks against live documentation
- 🤖 **AI-Powered** - Understands APIs like a human developer
- 🚀 **CI/CD Ready** - Perfect for pre-commit hooks and pipelines
- 📝 **Multiple Languages** - Python, JavaScript, TypeScript, Go, and more
- 🔒 **Secure** - Only sends API endpoints, never your code

## Usage

### Check Current Directory

```bash
strayl-lint check
```

### Check Specific Path

```bash
strayl-lint check src/
```

### Filter by File Extension

```bash
strayl-lint check --ext .py,.js
```

### Initialize Config File

```bash
strayl-lint init sk_live_xxxxx
# Creates .strayl config file
```

## Configuration

### Environment Variable

```bash
export STRAYL_API_KEY=sk_live_xxxxx
```

### Config File

Create `.strayl` in your project root:

```
api_key=sk_live_xxxxx
```

**Important:** Add `.strayl` to your `.gitignore`!

## CI/CD Integration

### GitHub Actions

```yaml
name: API Check

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install strayl-lint
      - run: strayl-lint check
        env:
          STRAYL_API_KEY: ${{ secrets.STRAYL_API_KEY }}
```

### Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: strayl-lint
        name: Strayl API Check
        entry: strayl-lint check
        language: system
        pass_filenames: false
```

## How It Works

1. **Scan** - Finds `strayl:doc` annotations in your codebase
2. **Extract** - Identifies HTTP methods, endpoints, and parameters
3. **Validate** - Sends to Strayl Cloud for AI-powered validation
4. **Report** - Shows you exactly what changed in the API

## Supported Documentation Formats

- OpenAPI / Swagger (JSON, YAML)
- HTML documentation pages
- Markdown docs
- API reference sites

## Privacy & Security

- ✅ Only API endpoints and HTTP methods are sent
- ✅ No source code is transmitted
- ✅ No sensitive data leaves your machine
- ✅ Documentation URLs must be publicly accessible

## Examples

### Yookassa Integration

```python
# strayl:doc https://yookassa.ru/developers/api
import requests

# Watchdog will detect if 'sum' was renamed to 'amount'
response = requests.post(
    "https://api.yookassa.ru/v3/payments",
    json={"sum": 1000}  # ⚠️  Warning: field 'sum' renamed to 'amount'
)
```

### Stripe Integration

```javascript
// strayl:doc https://stripe.com/docs/api
const payment = await stripe.paymentIntents.create({
  amount: 2000,
  currency: 'usd',
  // ✅ All fields match current API
});
```

## Commands

### `check`

Check API calls against documentation.

```bash
strayl-lint check [PATH] [OPTIONS]
```

**Options:**
- `--api-key, -k TEXT` - API key (or use STRAYL_API_KEY env var)
- `--ext, -e TEXT` - Comma-separated file extensions
- `--verbose, -v` - Show detailed output
- `--help` - Show help message

### `init`

Initialize configuration file.

```bash
strayl-lint init <API_KEY>
```

### `version`

Show version information.

```bash
strayl-lint version
```

## Troubleshooting

### "No API key found"

Make sure you've set your API key via:
- Environment: `export STRAYL_API_KEY=sk_live_xxx`
- Config file: `echo 'api_key=sk_live_xxx' > .strayl`
- CLI flag: `strayl-lint check --api-key sk_live_xxx`

### "No API calls found"

Make sure you've added `strayl:doc` annotations:

```python
# strayl:doc https://api.example.com/docs
requests.post(url, json=data)
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- 🌐 Website: [strayl.dev](https://strayl.dev)
- 📖 Documentation: [docs.strayl.dev](https://docs.strayl.dev)
- 💬 Discord: [discord.gg/strayl](https://discord.gg/strayl)
- 🐛 Issues: [github.com/strayl/strayl-lint/issues](https://github.com/strayl/strayl-lint/issues)

---

**Never fear API updates again.** 🐕
