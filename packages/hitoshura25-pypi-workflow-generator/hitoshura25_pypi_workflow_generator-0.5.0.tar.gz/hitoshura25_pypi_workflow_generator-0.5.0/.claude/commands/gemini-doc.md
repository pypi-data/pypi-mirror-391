Use the `mcp__gemini-workflow__generate_documentation_with_gemini` tool to generate comprehensive documentation.

**PROJECT CONTEXT:**
This is pypi-workflow-generator - a Python tool that creates CI/CD workflow templates (Jinja2 *.j2 files) for other Python PyPI projects. It generates GitHub Actions workflows, pyproject.toml configurations, and release automation for downstream users.

**Key Documentation Considerations:**
- Template architecture: hitoshura25_pypi_workflow_generator/*.j2 (Jinja2 templates)
- Dogfooding approach: This project uses its own generated workflows
- Dual audience: Developers of this tool AND users who generate workflows from it
- Template variables: Document which variables are available and how to customize
- Generation process: How Python code renders templates for downstream projects
- Build system: setuptools-scm versioning, pyproject.toml-based packaging

**USER REQUEST:**
Documentation type: {documentation_type}
Scope: {scope}

**Documentation Instructions for Gemini:**
When generating documentation, ensure coverage of:
1. The template generation system and how Jinja2 templates work
2. The relationship between templates (*.j2) and dogfooding implementations
3. How users can customize generated workflows via template variables
4. The dogfooding approach and why template/workflow pairs exist
5. Examples showing both template usage and generated output
6. How this project maintains consistency between templates and its own workflows

Parameters (extract from ARGUMENTS):
- **documentation_type**: Type of docs (e.g., "architecture", "user-guide", "developer-guide", "template-reference") (required)
- **scope**: What to document (e.g., "template system", "workflow generation", "CLI usage", "entire project") (required)
- **output_path**: Optional - where to save the documentation (default: docs/ or README.md)
- **include_examples**: Optional - whether to include code examples (boolean, recommended: true)

Example usage:
- `/gemini-doc Generate architecture documentation covering the template system`
- `/gemini-doc Create a user guide for generating and customizing workflows`
- `/gemini-doc Write developer documentation for adding new workflow templates`
