# Security Policy

## Supported branch

Security fixes are maintained on `project-current`, the repository's
authoritative branch. Historical branches and the legacy repository are not
supported deployment sources.

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting or a private security
advisory. Do not open a public issue containing credentials, provider payloads,
private paths, exploit details, or sensitive evidence.

Include the affected commit, file or component, realistic impact, reproduction
conditions, and whether the issue requires network opt-in or non-default
configuration. Never include live provider keys or paid raw responses.

## Security boundaries

- The FastAPI service and Next.js Workspace are local-only and must bind to a
  loopback address.
- Provider network access is disabled by default and requires explicit,
  provider-specific opt-in.
- Credentials must come from an approved secret store or process environment;
  they must never be committed, logged, placed in `.env`, or copied into an
  issue or pull request.
- Raw paid-provider payloads, local data-lake contents, databases, caches,
  notebooks, and private runtime logs are not public repository artifacts.
- The public application is read-only. Recommendation execution, broker access,
  trading, production writes, and model promotion remain locked.

Before a visibility or release change, run:

```bash
python scripts/audit_public_release_readiness.py
python scripts/audit_local_workspace_boundary.py
python -m pytest tests -q
```

The tracked-tree audit complements, but does not replace, a credential scan of
the complete reachable Git history.
