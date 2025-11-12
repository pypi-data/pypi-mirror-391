# BugBountyCrawler

A production-ready, legal, modular BugBountyCrawler for ethical bug bounty hunting. This tool prioritizes safety, accuracy, and responsible disclosure while providing comprehensive reconnaissance and scanning capabilities.

## ⚠️ Legal Disclaimer

**IMPORTANT**: This tool is designed for authorized security testing only. Users must:

- Only test targets they own or have explicit written permission to test
- Comply with all applicable laws and regulations
- Respect rate limits and terms of service
- Follow responsible disclosure practices
- Never use this tool for malicious purposes

The authors are not responsible for any misuse of this tool.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (for testing)
- Valid bug bounty program scope

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/bugbountycrawler.git
cd bugbountycrawler

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .

# Initialize the database
bugbounty init-db
```

### Basic Usage

1. **Create a scope file** (see `examples/scope-example.yaml`):
```yaml
program_name: "Example Bug Bounty Program"
domains:
  - "example.com"
  - "*.example.com"
endpoints:
  - "https://api.example.com/v1/*"
exclusions:
  - "staging.example.com"
  - "dev.example.com"
```

2. **Start a scan**:
```bash
bugbounty scan --scope examples/scope-example.yaml --target example.com
```

3. **Review findings** in the web UI:
```bash
bugbounty web-ui
```

### Docker Usage

```bash
# Start with OWASP Juice Shop for testing
docker-compose up -d

# Access the web UI
open http://localhost:8000

# Test against Juice Shop
bugbounty scan --scope examples/scope-example.yaml --target http://localhost:3000
```

## 🏗️ Architecture

### Core Components

- **Scope Validator**: Ensures all targets are within authorized scope
- **Asset Discovery**: Passive OSINT and active subdomain enumeration
- **URL Crawler**: Robust crawler with JavaScript support
- **Safe Scanners**: Non-destructive security checks
- **Report Generator**: HackerOne/Bugcrowd-ready reports
- **Web UI**: React-based interface for finding review

### Safety Features

- **No Automated Exploitation**: Only passive and non-destructive checks
- **Human-in-the-Loop**: Manual approval required for all findings
- **Rate Limiting**: Configurable delays and concurrency controls
- **Scope Enforcement**: Strict validation against program scope
- **Responsible Disclosure**: Built-in workflow for ethical reporting

## 📁 Project Structure

```
bugbountycrawler/
├── bugbountycrawler/          # Main package
│   ├── core/                  # Core functionality
│   ├── scanners/              # Security scanners
│   ├── crawlers/              # Web crawlers
│   ├── models/                # Data models
│   ├── api/                   # FastAPI endpoints
│   ├── cli/                   # CLI interface
│   └── web/                   # React frontend
├── tests/                     # Test suite
├── examples/                  # Example configurations
├── docs/                      # Documentation
└── docker/                    # Docker configurations
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///./bugbounty.db

# Security
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key

# Rate Limiting
DEFAULT_RATE_LIMIT=10  # requests per second
MAX_CONCURRENT=5       # concurrent requests

# Optional: Remote storage
S3_BUCKET=your-bucket
S3_ACCESS_KEY=your-key
S3_SECRET_KEY=your-secret
```

### Scope File Format

See `examples/scope-example.yaml` for detailed scope configuration options.

## 🧪 Testing

### Local Testing with OWASP Juice Shop

```bash
# Start test environment
docker-compose up -d

# Run tests
pytest

# Run with coverage
pytest --cov=bugbountycrawler
```

### Integration Tests

```bash
# Test against Juice Shop
pytest tests/integration/ -v
```

## 📊 Reports

The tool generates reports in multiple formats:

- **Markdown**: Human-readable format
- **PDF**: Professional reports
- **HackerOne**: Direct submission format
- **Bugcrowd**: Direct submission format

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/your-org/bugbountycrawler/issues)
- Security: security@bugbountycrawler.dev

## 🎓 Learning Resources

- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Bug Bounty Methodology](https://github.com/OWASP/OWASP-WebSecurityTestingGuide)
- [Responsible Disclosure](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerability_Disclosure_Cheat_Sheet.html)
