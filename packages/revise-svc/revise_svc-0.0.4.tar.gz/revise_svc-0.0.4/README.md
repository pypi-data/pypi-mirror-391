# REVISE

REVISE is a Python toolkit for reconstruct and analyse spatial transcriptomics (ST) data at single-cell resolution across diverse ST platforms.

Visit our [documentation](https://revise-svc.readthedocs.io/en/latest/) for installation, tutorials, examples and more.

## Highlights
- **Benchmark module**: Reproducible evaluation pipelines for simulated or public datasets, enabling method-to-method comparisons.
- **Application module**: Annotation, reconstruction, and downstream analyses for real ST data.

## Quick Start
If you just need the published Python package:
```bash
pip install revise-svc
```

## Example
```python
import anndata as ad
from revise.application import SpSvc

st = ad.read_h5ad("data/spatial.h5ad")
sc = ad.read_h5ad("data/single_cell_reference.h5ad")
config = ...

svc = SpSvc(st, sc, config=config, logger=None)
svc.annotate()
svc.reconstruct()
```

## Repository Layout
- `revise/application`: SVC workflows for real datasets.
- `revise/benchmark`: SVC variants for benchmarking studies.
- `revise/methods`: Algorithm implementations and model components.
- `revise/tools`: Distance metrics, logging helpers, and general utilities.
- `conf`: Example configurations and experiment parameters.

## License
REVISE is released under the MIT License (see `LICENSE`).
