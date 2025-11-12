# Custom Slash Commands

This directory contains custom slash commands for the pypi-workflow-generator project.

## Gemini Workflow Commands

These commands leverage the `gemini-workflow` MCP server, which provides access to Gemini's 2M token context window for codebase-wide analysis.

### Available Commands

| Command | Purpose | Best For |
|---------|---------|----------|
| `/gemini-spec` | Create technical specifications | Planning new features or changes |
| `/gemini-analyze` | Deep codebase analysis | Understanding architecture, finding patterns |
| `/gemini-review` | Comprehensive code review | PR reviews, security audits, quality checks |
| `/gemini-doc` | Generate documentation | API docs, architecture docs, guides |
| `/gemini` | General-purpose AI queries | Any question with full codebase context |

### When to Use Which Command

**Use `/gemini-spec`** when:
- Planning a new feature implementation
- Need detailed technical specifications
- Want to ensure comprehensive coverage of requirements

**Use `/gemini-analyze`** when:
- Learning a new codebase
- Investigating how something works across multiple files
- Looking for patterns, anti-patterns, or technical debt

**Use `/gemini-review`** when:
- Reviewing pull requests
- Security auditing code
- Checking code against specifications
- Looking for bugs or quality issues

**Use `/gemini-doc`** when:
- Need to document APIs or systems
- Creating onboarding documentation
- Generating architecture overviews

**Use `/gemini`** when:
- Have a general question about the codebase
- Need broader analysis that doesn't fit other categories
- Want AI assistance with full project context

## Usage Tips

1. **Be specific**: The more specific your prompt, the better the results
2. **Combine commands**: Use `/gemini-analyze` first, then `/gemini-spec` with the context
3. **Reuse context**: Use `context_id` to avoid reloading the full codebase
4. **Check output**: These tools may save files - check the specified output paths

## Examples

```bash
# Create a spec for a new feature
/gemini-spec Add OAuth2 authentication support

# Analyze how testing is structured
/gemini-analyze Explain the testing strategy and coverage

# Review recent changes
/gemini-review Review src/auth.py for security vulnerabilities

# Generate API documentation
/gemini-doc Create API reference for all public endpoints

# General question
/gemini What would be the impact of switching from setuptools to poetry?
```

## Adding New Commands

To add a new custom command:

1. Create a new `.md` file in `.claude/commands/`
2. Write the command prompt/instructions
3. Use it with `/your-command-name`

Commands are automatically discovered by Claude Code.
