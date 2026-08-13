# Pushing this to GitHub

The repository is already initialized, committed, and tagged `v1.0.0`. It only needs a
remote.

## 1. Create the repository

On GitHub: **New repository** → name it `way-of-mercy-and-truth` → **Public** → do not
initialize with a README, license, or .gitignore (this repo already has them).

## 2. Push

```bash
cd way-of-mercy-and-truth
git remote add origin https://github.com/<your-username>/way-of-mercy-and-truth.git
git branch -M main
git push -u origin main
git push --tags
```

## 3. Turn on GitHub Pages (optional, ~2 minutes)

Settings → Pages → Source: `main` / root. The README becomes the front door at
`<username>.github.io/way-of-mercy-and-truth`, and `llms.txt`, `manifest.json`, and every
`dist/*.txt` become stable public URLs — which is the point of building them.

If you later register a domain, add it under Settings → Pages → Custom domain, and the
citation URLs become permanent.

## 4. Enable issues

Settings → Features → Issues. The templates in `.github/ISSUE_TEMPLATE/` will appear
automatically. This is the "check me rather than trust me" apparatus in working form.

## After any edit to the manuscript

```bash
python3 tools/build.py     # regenerates llms.txt, manifest.json, dist/
git add -A
git commit -m "C23: <what changed and why>"
git push
```

## Releasing a new version

```bash
echo "1.1.0" > VERSION
python3 tools/build.py
git add -A && git commit -m "Release 1.1.0: <what changed>"
git tag -a v1.1.0 -m "<what changed>"
git push && git push --tags
```

See [VERSIONING.md](VERSIONING.md) for what counts as PATCH, MINOR, and MAJOR.

## A note on the pseudonym

Git records `user.name` and `user.email` on every commit. This repo is configured
locally as `A. Pilgrim <pilgrim@wayofmercyandtruth.org>`. If you push from a machine
where your global git config has your real name, **it will be attached to every commit
permanently** — history is not rewritten here by policy, so it cannot be quietly cleaned
up afterward.

Set it per-repository before pushing:

```bash
git config user.name "A. Pilgrim"
git config user.email "pilgrim@wayofmercyandtruth.org"
```

Also check: GitHub account name, and Settings → Emails → **Keep my email address
private**. This is a decision to make deliberately once, not to discover later.
