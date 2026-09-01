# Migration runbook

The goal: on the new machine, going from bare OS to a working Hermes is a clone,
a script, and a paste of one `.env` file. Everything else is in git.

## Before you buy — nothing to do

The stack is deliberately hardware-agnostic. No step below depends on what you
buy. If the new box has a GPU, that is an *addition* (see `LOCAL-MODELS.md`), not
a different setup.

## On the old machine (day before)

```bash
scripts/backup.sh ~/migrate          # sessions, memories, skills, cron, auth, .env
```

The archive holds live API keys and is written `0600`. Move it by scp or a USB
stick. Do not put it in this repo, in cloud sync, or in a chat window.

Then confirm the repo is current:

```bash
git status --short          # should be clean
git push
```

## On the new machine

```bash
# 1. Prerequisites
python3 --version                       # 3.11-3.13
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
exec $SHELL -l

# 2. This repo
git clone <your-remote> ~/hermes-stack && cd ~/hermes-stack

# 3. Install + deploy config (idempotent, backs up anything it overwrites)
scripts/bootstrap.sh

# 4. Credentials
scripts/restore.sh ~/migrate/hermes-state-*.tar.gz    # if you took a backup
#   ... or, from scratch:
cp litellm/.env.example ~/.litellm/.env && chmod 600 ~/.litellm/.env && $EDITOR ~/.litellm/.env

# 5. Verify credentials reach every provider
scripts/preflight.sh

# 6. Start the proxy
mkdir -p ~/.config/systemd/user
cp service/litellm-proxy.service ~/.config/systemd/user/
systemctl --user daemon-reload && systemctl --user enable --now litellm-proxy
loginctl enable-linger "$USER"          # keeps it running headless / after logout
#   macOS: cp service/com.local.litellm.plist ~/Library/LaunchAgents/ && launchctl load -w ~/Library/LaunchAgents/com.local.litellm.plist
#   Either OS, foreground for debugging: scripts/start-proxy.sh

# 7. Verify routing end to end
scripts/smoke-test.sh

# 8. Verify Hermes sees the router
hermes config get model                 # provider: litellm, default: smart-router
hermes
```

## Verification checklist

Done means all five, in order:

- [ ] `scripts/validate-config.py` — config loads into a real LiteLLM Router
- [ ] `scripts/preflight.sh` — every key you set answers `200`
- [ ] `curl -s localhost:4000/health/readiness` — proxy up
- [ ] `scripts/smoke-test.sh` — all four rows OK, and the LONG row is **not**
      served by `cerebras-fast` (that is the context-fallback working)
- [ ] `hermes` starts, answers a prompt, and `~/.hermes/logs` shows no provider errors

## Rollback

`bootstrap.sh` timestamps a `.bak.*` copy of every config it replaces, and
`restore.sh` moves an existing `~/.hermes` aside rather than deleting it. To go
back: stop the service, restore the `.bak` file, restart.

## Decommissioning the old machine

Only after the checklist above passes on the new one:

1. Revoke and reissue every provider key — they have been on two machines, and
   they were in a tarball that moved between them.
2. `shred -u` the backup archive on both machines.
3. `rm -rf ~/.litellm ~/.hermes` on the old machine.

Reissuing keys is the step people skip. `preflight.sh` makes re-verifying the
new ones a 10-second job, so there is no excuse to leave the old ones live.

## If something is wrong

| Symptom | Look at |
|---|---|
| Hermes says "provider not found" | `providers:` name in `~/.hermes/config.yaml` must match `model.provider` |
| 401 from the proxy | `LITELLM_MASTER_KEY` differs between `~/.litellm/.env` and `~/.hermes/.env` — `preflight.sh` checks this |
| 404 from one provider | base URL — usually Cloudflare's account id or the wrong DashScope region |
| Long prompts fail instead of rerouting | `enable_pre_call_checks: true` and `max_input_tokens` present? |
| Everything lands on the cheap tier | expected — see `explain-routing.py` and ASSESSMENT.md |
| Proxy dies overnight | `journalctl --user -u litellm-proxy -n 100` |
