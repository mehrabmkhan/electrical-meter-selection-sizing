# MeterSpec Architecture

MeterSpec keeps engineering decisions separate from the web interface.

```mermaid
flowchart TD
  A[Customer requirements wizard] --> B[Pydantic validation model]
  B --> C[Engineering validation]
  C --> D[CT sizing]
  C --> E[PT requirement logic]
  C --> F[Hard product filtering]
  F --> G[Deterministic ranking]
  G --> H[Communication architecture]
  H --> I[Technical result]
  I --> J[HTML report]
```

The catalog is stored in `data/catalog.yaml` so product limits and capabilities are not scattered through source code.
