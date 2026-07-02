# flamapy-sharpsat

`flamapy-sharpsat` is a [flamapy](https://flamapy.github.io) plugin that adds **scalable
approximate model counting** and **almost-uniform sampling** of feature-model configurations,
on top of the CNF produced by the SAT metamodel.

It complements the existing backends:

- The SAT (`flamapy-sat`) and Z3 backends count configurations by full enumeration, which does
  not scale; the BDD backend counts exactly but the diagram can blow up on large models.
- `flamapy-sharpsat` uses [ApproxMC](https://github.com/meelgroup/approxmc) for an
  (epsilon, delta) **approximate** count and [UniGen](https://github.com/meelgroup/unigen) for
  **almost-uniform** sampling — both hashing-based tools from the CryptoMiniSat family that
  scale to far larger models.

## Installation

```
pip install flamapy-sharpsat
```

This pulls in `pyapproxmc` and `pyunigen` (and the flamapy core/FM/SAT plugins).

## Operations

| Operation | Class |
|---|---|
| Approximate number of configurations | `SharpSATConfigurationsNumber` |
| Almost-uniform sampling | `SharpSATSampling` |

## Usage

```python
from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.sharpsat_metamodel.transformations import FmToSharpSAT
from flamapy.metamodels.sharpsat_metamodel.operations import (
    SharpSATConfigurationsNumber,
    SharpSATSampling,
)

fm = UVLReader('model.uvl').transform()
model = FmToSharpSAT(fm).transform()

count = SharpSATConfigurationsNumber().execute(model).get_result()

sampler = SharpSATSampling()
sampler.set_sample_size(10)
sample = sampler.execute(model).get_sample()
```

Counting and sampling are projected onto the feature variables, so auxiliary variables
(such as the ones introduced by the optional Tseytin CNF encoding, available through
`FmToSharpSAT(fm, cnf_method='tseytin')`) never distort the results.

## License

GPL-3.0-or-later.
