# Contributing to News Podcast Agent

Thank you for your interest in contributing to the News Podcast Agent project! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion for improvement:

1. Check if the issue already exists in the [GitHub Issues](https://github.com/yourusername/news-podcast-agent/issues)
2. If not, create a new issue with a descriptive title and detailed information about the problem or suggestion
3. Include steps to reproduce the issue, expected behavior, and actual behavior
4. Include your environment details (OS, Python version, etc.)

### Submitting Changes

1. Fork the repository
2. Create a new branch for your changes: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run tests to ensure your changes don't break existing functionality: `make test`
5. Run linting to ensure code quality: `make lint`
6. Commit your changes with a descriptive commit message
7. Push your branch to your fork: `git push origin feature/your-feature-name`
8. Submit a pull request to the main repository

### Pull Request Process

1. Ensure your code passes all tests and linting checks
2. Update documentation if necessary
3. Add tests for new functionality
4. Your pull request will be reviewed by maintainers, who may request changes
5. Once approved, your changes will be merged

## Development Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/news-podcast-agent.git
   cd news-podcast-agent
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. Set up environment variables:
   ```bash
   export NEWS_API_KEY="your_news_api_key"
   export GOOGLE_CLOUD_PROJECT="your_gcp_project_id"
   export GOOGLE_CLOUD_LOCATION="your_gcp_region"
   ```

5. Run tests to verify your setup:
   ```bash
   make test
   ```

## Project Structure

Please familiarize yourself with the project structure before contributing:

- `app/`: Core application code
  - `agent.py`: Main agent logic with podcast agent roles
  - `tools.py`: Custom tools for news API and text-to-speech
  - `config.py`: Configuration settings
  - `utils/`: Utility functions
- `tests/`: Unit and integration tests
- `deployment/`: Infrastructure and deployment scripts

## Testing

All new code should include appropriate tests. We use pytest for testing:

```bash
make test
```

## Code Style

We follow PEP 8 style guidelines for Python code. Use the provided linting tools to ensure your code meets these standards:

```bash
make lint
```

## Documentation

Please update documentation when making changes to the code. This includes:

- Code comments
- Function/method docstrings
- README.md updates for user-facing changes
- Any additional documentation in the docs directory

## License

By contributing to this project, you agree that your contributions will be licensed under the project's Apache 2.0 license.