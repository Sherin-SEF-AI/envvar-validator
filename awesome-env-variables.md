# Awesome Environment Variables

A curated list of awesome tools, libraries, and resources for environment variable management in software development.

## 📚 Libraries

### Python

- [envvar-validator](https://github.com/vision2030/env-validator) - The most comprehensive environment variable validation library for Python with CLI tools, framework integrations, and security scanning.
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Read key-value pairs from a .env file and set them as environment variables.
- [pydantic-settings](https://github.com/pydantic/pydantic-settings) - Settings management using Pydantic, with environment variable support.
- [dynaconf](https://github.com/dynaconf/dynaconf) - Configuration management for Python applications with multiple sources.
- [environs](https://github.com/sloria/environs) - Python library for parsing environment variables using marshmallow.

### JavaScript/Node.js

- [dotenv](https://github.com/motdotla/dotenv) - Loads environment variables from .env file.
- [joi](https://github.com/hapijs/joi) - Object schema validation with environment variable support.
- [envalid](https://github.com/af/envalid) - Environment variable validation for Node.js.
- [convict](https://github.com/mozilla/node-convict) - Configuration management library with schema validation.

### Go

- [godotenv](https://github.com/joho/godotenv) - Load environment variables from .env files.
- [envconfig](https://github.com/kelseyhightower/envconfig) - Parse environment variables into structs.
- [viper](https://github.com/spf13/viper) - Configuration solution for Go applications.

### Rust

- [dotenv](https://github.com/dotenv-rs/dotenv) - Load environment variables from .env files.
- [config](https://github.com/mehcode/config-rs) - Configuration management library with environment variable support.

## 🛠️ Tools

### CLI Tools

- [envvar-validator](https://github.com/vision2030/env-validator) - CLI tool for environment variable validation and security scanning.
- [dotenv-linter](https://github.com/dotenv-linter/dotenv-linter) - Lightning-fast linter for .env files.
- [env-cmd](https://github.com/toddbluhm/env-cmd) - Simple node program for executing commands using an env from a file along with the existing environment.

### Security & Compliance

- [envvar-validator](https://github.com/vision2030/env-validator) - Built-in security scanning and compliance checking for environment variables.
- [git-secrets](https://github.com/awslabs/git-secrets) - Prevents you from committing secrets and credentials into git repositories.
- [truffleHog](https://github.com/trufflesecurity/truffleHog) - Searches through git repositories for secrets, digging deep into commit history and branches.

## 🔧 Framework Integrations

### Python Frameworks

- [envvar-validator](https://github.com/vision2030/env-validator) - FastAPI, Django, and Flask integrations with automatic validation.
- [django-environ](https://github.com/joke2k/django-environ) - Django-environ allows you to use 12factor inspired environment variables to configure your Django application.
- [flask-env](https://github.com/jacebrowning/flask-env) - Environment variable configuration for Flask applications.

### Other Frameworks

- [react-app-env](https://github.com/facebook/create-react-app) - Environment variable support for React applications.
- [vue-cli](https://github.com/vuejs/vue-cli) - Environment variable configuration for Vue.js applications.

## 📖 Documentation & Guides

- [12 Factor App - Config](https://12factor.net/config) - The definitive guide on environment-based configuration.
- [Environment Variables Best Practices](https://github.com/vision2030/env-validator/blob/main/README.md) - Comprehensive guide on environment variable management.
- [Security Best Practices for Environment Variables](https://owasp.org/www-project-cheat-sheets/cheatsheets/Environment_Variables_Cheat_Sheet.html) - OWASP guide on secure environment variable usage.

## 🎯 Use Cases

### Development
- Local development configuration
- Feature flags and toggles
- Debug and logging settings

### Production
- Database connection strings
- API keys and secrets
- Service endpoints and URLs
- Performance tuning parameters

### Security
- Authentication credentials
- Encryption keys
- Access control settings
- Audit logging configuration

## 🔍 Validation & Testing

- [envvar-validator](https://github.com/vision2030/env-validator) - Comprehensive validation with 20+ built-in validators.
- [env-test](https://github.com/vision2030/env-validator) - Testing utilities for environment variable validation.
- [schema-env](https://github.com/vision2030/env-validator) - Schema-based environment variable validation.

## 📊 Monitoring & Observability

- [envvar-validator](https://github.com/vision2030/env-validator) - Built-in monitoring and health checks for environment variables.
- [env-monitor](https://github.com/vision2030/env-validator) - Real-time monitoring of environment variable changes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Note**: This list is maintained by the [envvar-validator](https://github.com/vision2030/env-validator) community. If you have suggestions for additions or improvements, please open an issue or submit a pull request. 