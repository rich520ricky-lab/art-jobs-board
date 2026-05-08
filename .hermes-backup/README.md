# Hermes Agent Backup

This directory contains a portable backup of your Hermes Agent configuration,
memories, and cron job definitions.

## Files

| File | Description |
|------|-------------|
| `memory.md` | Hermes agent memory (project facts, preferences) |
| `user.md` | User profile preferences |
| `config.yaml` | Full Hermes config (API keys redacted) |
| `mlx-model-config.yaml` | MLX local model settings |
| `cron-jobs.json` | All scheduled cron job definitions |

## Restoring

On a new computer, the `setup.sh` script will automatically:
1. Copy these files to `~/.hermes/memories/` and `~/.hermes/`
2. Re-create all cron jobs from `cron-jobs.json`

## Security Notes

- API keys, OAuth secrets, and tokens are REDACTED in this backup.
- You'll need to set them manually on new computer via `hermes config set`.
