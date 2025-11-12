# apx-harvest

`apx-harvest` packages the Python automation utilities used by the APX platform to scan source trees, infer domains, plan capsule execution, and verify deterministic transforms. It exposes:

- `apx-harvest detect` – run built-in detectors over a project root, streaming structured JSON.
- `apx-harvest domain` – infer the likely business/domain classification for a repository.
- `apx-harvest plan` – plan capsule execution order with conflict minimisation.
- `apx-harvest verify` – replay write operations twice to confirm determinism.
- `apx-harvest evolve` – skeleton evolutionary pipeline for SPAC optimisation.

Install from PyPI once published:

```bash
pip install apx-harvest
apx-harvest detect /path/to/repo
```

The package is released under the Apache 2.0 license. For more detail on the command output formats, browse the source or consult the APX documentation.***

