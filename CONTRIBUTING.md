# Contributing to AI Office

Thank you for contributing to AI Office. We maintain an autonomous, verified multi-agent organization with a strict security and commercial boundary.

## Ground Rules

1. **Zero-Cost Constraint**:
   All features, integrations, and dependencies must be 100% free / open-source / freemium. No paid cloud services, paid LLMs, or paid external platform subscriptions may be added or mandated.

2. **Security & Human Authorization Invariant**:
   Any action that communicates with the outside world (e.g. publishing to social media, sending emails, initiating external network calls modifying account state) MUST route through the CEO Approval Gateway. Internal agents cannot approve their own actions or bypass the gateway.

3. **Verification First**:
   Every pull request or task commit must include automated unit/integration tests and update `docs/EXECUTION_LOG.md`.

4. **Conventional Commits**:
   Follow the project's commit style:
   - `feat(scope): ...`
   - `fix(scope): ...`
   - `test(scope): ...`
   - `docs(scope): ...`
   - `refactor(scope): ...`
   - `chore(scope): ...`

5. **No Secrets in Code**:
   Never commit `.env`, credentials, OAuth tokens, private keys, or API tokens. Secrets must be supplied via local environment variables or the Android keystore / SQLite encrypted token vault.

## Development Workflow

1. Fork or branch from `main`.
2. Implement your changes.
3. Run Python backend tests:
   ```bash
   cd backend
   pytest tests/ -v
   ```
4. Run Android Kotlin tests:
   ```bash
   cd android
   ./gradlew test
   ```
5. Ensure code formatting and linting pass.
6. Open a pull request describing the changes and test results.
