# REVISE

REVISE (Regenerative Evaluation of VIable Spatial Expression) is a Python toolkit for benchmarking and annotating spatial transcriptomics (ST) data. It bundles standardized benchmarking workflows and application-ready SVC (Spatial transcriptomics Variational Comparison) pipelines so that researchers can compare algorithms, reproduce analyses, and build their own reference pipelines with minimal friction.

## Highlights
- **Benchmark module**: Reproducible evaluation pipelines for simulated or public datasets, enabling method-to-method comparisons.
- **Application module**: Annotation, reconstruction, and downstream analyses for real ST data with built-in ST/SC preprocessing.
- **Utility tools**: Ready-to-use helpers such as efficient similarity metrics in `revise.tools.distance`, simplifying scripting.
- **Extensible architecture**: Layered `BaseSvc` / `ApplicationSvc` classes make it straightforward to plug in new tasks or methods.

## Quick Start
```bash
git clone https://github.com/wuys13/REVISE.git
cd REVISE
python -m venv .venv && source .venv/bin/activate
pip install -e ".[annotation]"
```

## Minimal Example
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

Explore the full set of benchmark/application services in `revise/application` and `revise/benchmark`. To extend the framework, inherit from the relevant base class and override preprocessing, optimization, or evaluation hooks.

## Repository Layout
- `revise/application`: SVC workflows for real datasets.
- `revise/benchmark`: SVC variants for benchmarking studies.
- `revise/methods`: Algorithm implementations and model components.
- `revise/tools`: Distance metrics, logging helpers, and general utilities.
- `conf`: Example configurations and experiment parameters.

## Contributing
Issues and pull requests are welcome-especially bug reports, documentation improvements, and new method implementations. Install the dev extras via `pip install -e ".[dev]"` to run `ruff` and `pytest` before submitting changes.

## License
REVISE is released under the MIT License (see `LICENSE`).
