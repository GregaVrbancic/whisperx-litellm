# Contributing Guidelines

We welcome contributions! This document outlines how to contribute to the WhisperX LiteLLM Wrapper project.

## Code of Conduct

Be respectful and inclusive. We're building a community tool for everyone.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/whisperx-litellm-wrapper.git
   cd whisperx-litellm-wrapper
   ```
3. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Set up development environment**:
   ```bash
   uv sync --all-extras
   ```

## Development Workflow

### Making Changes

1. **Write tests** for new functionality
2. **Make code changes** that pass your tests
3. **Ensure code quality**:
   ```bash
   uv run ruff check app.py tests/
   uv run ruff format app.py tests/
   uv run pytest tests/ -v
   ```
4. **Commit with clear messages**:
   ```bash
   git commit -m "feat: add support for custom parameters"
   ```

### Commit Message Format

Use conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that don't affect code meaning (formatting, etc.)
- `refactor`: Code refactoring without feature changes
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Changes to build process, dependencies, etc.

**Examples:**
```
feat(api): add support for custom batch sizes
fix(docker): correct GPU device mapping
docs(readme): update installation instructions
test: add integration tests for diarization
```

### Testing

All changes must include tests:

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test
uv run pytest tests/test_app.py::TestHealthEndpoint -v

# Check coverage
uv run pytest tests/ --cov=app --cov-report=html
```

New features should have corresponding test cases in `tests/test_app.py`.

## Pull Request Process

1. **Push your branch** to your fork
2. **Create a Pull Request** to the main repository
3. **Fill out the PR template** with:
   - Description of changes
   - Related issues (#123)
   - Type of change (feature/fix/docs)
   - Checklist completion

4. **Wait for CI/CD checks** to pass:
   - Tests must pass on Python 3.11 and 3.12
   - Linting must pass
   - Docker build must succeed

5. **Address review feedback** if needed

6. **Squash commits** if requested (keep history clean)

7. **Merge** once approved

## Code Style

### Python

- Follow PEP 8 standards
- Use type hints for functions
- Keep lines under 88 characters (line-length from Ruff config)
- Use `from __future__ import annotations` at the top of files

Example:
```python
def transcribe_audio(
    file: UploadFile,
    model: str = "large-v3",
    diarize: bool = True,
) -> dict[str, Any]:
    """Transcribe audio file.
    
    Args:
        file: Audio file to transcribe
        model: WhisperX model size
        diarize: Enable speaker diarization
    
    Returns:
        Dictionary with transcription results
    """
    # Implementation
    pass
```

### Documentation

- Use Markdown for all documentation
- Check links are valid and relative paths work
- Update main docs when adding features
- Include code examples in docstrings

## Version Management

See [VERSIONING.md](./VERSIONING.md) for how we manage versions that track WhisperX.

## Reporting Issues

### Bug Reports

Include:
1. Python version and OS
2. Minimal code to reproduce
3. Expected behavior
4. Actual behavior
5. Relevant logs/error messages
6. Environment variables used

### Feature Requests

Include:
1. Clear description of the feature
2. Why it would be useful
3. Example usage
4. Any related issues or discussions

## Documentation Improvements

Documentation improvements are always welcome! This includes:
- Fixing typos
- Clarifying instructions
- Adding examples
- Translating to other languages
- Creating diagrams or visual guides

## Performance Improvements

If you're optimizing performance:
1. Provide benchmarks showing the improvement
2. Ensure tests still pass
3. Document the change if it affects behavior

## Adding Dependencies

If you need to add a new dependency:
1. Justify why it's needed
2. Check for size and compatibility
3. Propose in an issue first if possible
4. Update `pyproject.toml` and `uv.lock`

## Development Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [WhisperX Documentation](https://github.com/m-bain/whisperx)
- [OpenAI Audio API Documentation](https://platform.openai.com/docs/api-reference/audio)
- [LiteLLM Documentation](https://docs.litellm.ai/)

## Questions?

Feel free to:
- Open an issue to discuss
- Start a discussion in GitHub Discussions
- Reach out to maintainers

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- GitHub contributors page

Thank you for helping improve this project! 🚀
