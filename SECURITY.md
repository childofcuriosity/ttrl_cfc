# Security and artifact hygiene

Do not commit API keys, cloud credentials, SSH history, raw research notebooks,
model checkpoints or signed download URLs.

Before publishing new artifacts, scan staged files and inspect logs for provider
tokens. Use environment variables or an untracked `.env` file for credentials.
The repository `.gitignore` excludes the common local artifact locations used by
this project.
