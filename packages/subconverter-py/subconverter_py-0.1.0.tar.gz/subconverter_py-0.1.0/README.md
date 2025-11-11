# py-subconverter

Python-based proxy subscription converter for Clash. Convert proxy subscriptions to Clash configuration format with full support for subconverter INI configurations.

## Features

- ✅ Convert proxy subscriptions to Clash YAML format
- ✅ Support for Shadowsocks, VMess, Trojan, VLESS protocols
- ✅ Full subconverter INI configuration support
- ✅ Custom proxy groups with regex matching
- ✅ Rule-based routing with automatic rule set downloading
- ✅ Filter unsupported rule types automatically
- ✅ No external services required - 100% local conversion

## Installation

```bash
pip install py-subconverter
```

## Quick Start

### Command Line Usage

Basic conversion:
```bash
py-sub-conv --output config.yaml
```

With environment variables (`.env` file):
```env
DLER_EMAIL=your@email.com
DLER_PASSWORD=yourpassword
RULE_URL=https://example.com/config.ini
```

Then run:
```bash
py-sub-conv --output config.yaml
```

### Python API Usage

```python
from py_subconverter import SubscriptionConverter

converter = SubscriptionConverter()

# Convert subscription
config = converter.convert(
    subscription_url="https://example.com/subscription",
    rule_url="https://example.com/config.ini",  # Optional INI config
    output_file="config.yaml"
)
```

## Supported Rule Types

py-subconverter automatically filters rules to only include types supported by standard Clash:

- ✅ `DOMAIN` - Match exact domain
- ✅ `DOMAIN-SUFFIX` - Match domain suffix
- ✅ `DOMAIN-KEYWORD` - Match domain keyword
- ✅ `IP-CIDR` - Match IPv4 CIDR
- ✅ `IP-CIDR6` - Match IPv6 CIDR
- ✅ `GEOIP` - Match GeoIP database
- ✅ `MATCH` - Match all (final rule)
- ✅ `PROCESS-NAME` - Match process name

Automatically filtered (Clash Meta only):
- ❌ `USER-AGENT`
- ❌ `URL-REGEX`

## INI Configuration Support

py-subconverter fully supports subconverter INI format:

```ini
[custom]
ruleset=🎯 Direct,https://example.com/rules/direct.list
ruleset=🚀 Proxy,https://example.com/rules/proxy.list
ruleset=🐟 Final,[]MATCH

custom_proxy_group=🚀 Proxy`select`[]♻️ Auto`[]🇭🇰 HK`[]DIRECT
custom_proxy_group=♻️ Auto`url-test`.*`http://www.gstatic.com/generate_204`300
custom_proxy_group=🇭🇰 HK`url-test`香港|HK`http://www.gstatic.com/generate_204`300
```

## CLI Options

```
py-sub-conv [OPTIONS]

Options:
  -o, --output FILE         Output YAML file path (default: config.yaml)
  -s, --subscription URL    Subscription URL (overrides .env)
  -r, --rule URL           Custom rule URL (overrides .env)
  -v, --verbose            Show detailed conversion process
  -h, --help               Show this help message
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/gencylee/py-subconverter.git
cd py-subconverter

# Install in development mode
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Build Package

```bash
python -m build
```

## Differences from Original Subconverter

py-subconverter is a pure Python implementation that:

1. **No External Services** - All conversion is done locally
2. **Better Performance** - Direct Python implementation without HTTP overhead
3. **Rule Filtering** - Automatically filters unsupported rule types
4. **Modern Python** - Clean, maintainable codebase with type hints

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- GitHub: https://github.com/gencylee/py-subconverter
- PyPI: https://pypi.org/project/py-subconverter/
- Issues: https://github.com/gencylee/py-subconverter/issues
