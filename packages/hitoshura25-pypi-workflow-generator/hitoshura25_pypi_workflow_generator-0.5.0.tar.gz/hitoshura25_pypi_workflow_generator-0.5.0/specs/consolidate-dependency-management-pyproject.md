# Use pyproject.toml for CI/CD Dependencies - Technical Specification

## 1. Feature Overview
This specification outlines the process of removing the `requirements.txt` file and modifying the CI/CD workflows to install dependencies directly from `pyproject.toml`. This change will establish `pyproject.toml` as the single source of truth for project dependencies, simplifying maintenance for both the generator project and the downstream projects that use its templates.

## 2. Architecture Overview
The core of this change is to modify the installation step in the GitHub Actions workflow files. Currently, workflows use `pip install -r requirements.txt` to install dependencies. This will be replaced with `pip install .[test]`, which leverages `setuptools` to install the package in editable mode along with its production and testing dependencies defined in `pyproject.toml`.

This change will be applied to:
1.  The Jinja2 workflow templates (`*.j2`) in `hitoshura25_pypi_workflow_generator/` to propagate the change to downstream users.
2.  The project's own dogfooded workflows in `.github/workflows/` to align the project with its own best practices.

The `requirements.txt` file will be deleted, and all its dependencies will be consolidated within `pyproject.toml`.

## 3. Database Changes
### Schema Modifications
Not applicable.

### Migration Scripts Needed
Not applicable.

## 4. Files to Create
No new files will be created. The primary goal is to eliminate `requirements.txt`.

## 5. Files to Modify
| File | Change Description |
| :--- | :--- |
| `pyproject.toml` | Consolidate all dependencies from `requirements.txt` into the `project.optional-dependencies.test` section. Ensure `Jinja2` and `setuptools` are in `project.dependencies`. |
| `hitoshura25_pypi_workflow_generator/_reusable_test_build.yml.j2` | Replace the step `pip install -r requirements.txt` with `pip install .[test]`. |
| `.github/workflows/_reusable-test-build.yml` | Replace the step `pip install -r requirements.txt` with `pip install .[test]`. This aligns the project's own CI with the new standard. |
| `MANIFEST.in` | Remove the line `include requirements.txt`. |
| `README.md` | Remove any sections or references that instruct users to use or maintain `requirements.txt`. |
| `setup.py` | Remove any logic that reads from or references `requirements.txt`. |

### Files to Delete
| File | Reason for Deletion |
| :--- | :--- |
| `requirements.txt` | This file is being replaced by `pyproject.toml` as the source of dependencies for CI/CD. |

## 6. Implementation Tasks (Ordered)
1.  **Consolidate Dependencies:**
    *   Move all dependencies listed in `requirements.txt` into the `[project.optional-dependencies]` table in `pyproject.toml` under a `test` key.
    *   Verify that core dependencies like `Jinja2` are listed under `[project.dependencies]`.

2.  **Update Jinja2 Template:**
    *   Modify `hitoshura25_pypi_workflow_generator/_reusable_test_build.yml.j2`.
    *   Find the installation step that uses `requirements.txt`.
    *   Replace `pip install -r requirements.txt` with `pip install .[test]`.

3.  **Update Project's Own Workflow:**
    *   Modify the dogfooded workflow at `.github/workflows/_reusable-test-build.yml`.
    *   Apply the same change as in the Jinja2 template: replace `pip install -r requirements.txt` with `pip install .[test]`.

4.  **Update Project Configuration:**
    *   Edit `MANIFEST.in` and remove the line `include requirements.txt`.
    *   If `setup.py` reads `requirements.txt`, remove that logic. Based on the project structure, this is unlikely as `pyproject.toml` and `setuptools_scm` are used, but it should be verified.

5.  **Update Documentation:**
    *   Review `README.md` and any other documentation files.
    *   Remove all instructions and references related to `requirements.txt`.

6.  **Cleanup:**
    *   Delete the `requirements.txt` file from the root of the repository.

7.  **Verification:**
    *   Commit the changes and open a pull request to trigger the modified `test-pr.yml` workflow.
    *   Confirm that the CI pipeline passes, successfully installing dependencies and running tests without `requirements.txt`.

## 7. Testing Requirements
### Unit Tests
*   No new unit tests are required, as the core logic of the Python generator code is not expected to change. Existing tests should continue to pass.

### Integration Tests
*   The primary integration test is the project's own CI/CD pipeline. A successful run of the updated workflow on a pull request will validate that the change works correctly in a real environment.

### E2E Tests
*   After merging, a downstream project could be used to generate a new workflow from the updated template. Running this workflow in the downstream project would serve as a full end-to-end test.

## 8. Security Considerations
*   **Single Source of Truth:** This change improves security and maintainability by consolidating all dependencies into `pyproject.toml`. This reduces the risk of dependency conflicts or discrepancies between development, testing, and production environments.
*   **Dependency Auditing:** Having all dependencies in one file makes it easier to audit them for vulnerabilities using standard tools that scan `pyproject.toml`.

## 9. Performance Considerations
*   The performance impact on the CI/CD pipeline is expected to be negligible. The time taken for `pip install .[test]` should be comparable to `pip install -r requirements.txt`. The primary benefit is in maintainability, not runtime performance.

## 10. Dependencies
*   No new dependencies will be added. This work involves reorganizing existing dependencies from `requirements.txt` into `pyproject.toml`.