# Versioning

The trunk is versioned `MAJOR.MINOR.PATCH`. Current version: see [`VERSION`](VERSION).

| Bump | Means | Examples |
|---|---|---|
| **PATCH** | No change to meaning | Typos, formatting, broken links, build fixes |
| **MINOR** | Expression improved, teaching unchanged | Clarified wording, added scripture reference, expanded practice note |
| **MAJOR** | The teaching itself changed | Stage reordered, practice withdrawn, source reassessed, position reversed |

## Rules

1. **IDs never change.** `WMT C23` is Chapter Twenty-Three permanently — across every
   version, revision, and file move. Retired IDs are never reused.
2. **Every MAJOR release needs a changelog entry** stating what changed, why, and what a
   reader who learned the previous version should now understand differently.
3. **History is never rewritten.** No force-push, no squash, no amend after publication.
   An untraceable road cannot be checked by anyone.

## Releasing

```bash
echo "1.1.0" > VERSION
python3 tools/build.py
git add -A
git commit -m "Release 1.1.0: <what changed>"
git tag -a v1.1.0 -m "<what changed>"
git push && git push --tags
```

Tag every release. A reader in ten years should be able to check out the exact version
someone cited.
