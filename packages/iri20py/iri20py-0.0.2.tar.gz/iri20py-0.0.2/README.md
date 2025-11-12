[![DOI](https://zenodo.org/badge/1089134543.svg)](https://zenodo.org/badge/latestdoi/1089134543)
# IRI-2020 Python Wrapper
`iri20py` is a wrapper around the [IRI-2020](https://ccmc.gsfc.nasa.gov/models/IRI~2020/) empirical model.

This repository includes a version of the IRI-2020 model where the call signatures have been modified for
ease of integration with Python. The integration is achieved by means of a FORTRAN shim ([`irishim.f90`](src/IRI2020/irishim.f90))
that is compiled into a module using [F2PY](https://numpy.org/doc/stable/f2py/index.html). Data files
associated with IRI-2020 are included in the [`data`](src/IRI2020/data) folder and are available at
runtime. The wrapper automatically retrieves the latest available [`ig_rz.dat`](https://chain-new.chain-project.net/echaim_downloads/ig_rz.dat)
and [`apf107.dat`](https://chain-new.chain-project.net/echaim_downloads/apf107.dat) files on import.

## Installation
A Fortran compiler is *REQUIRED* to build the FORTRAN extension module.

### From [PyPI](https://pypi.org/project/iri20py/)
```sh
pip install iri20py
```
### From [GitHub](https://github.com/sunipkm/iri20py)
```sh
pip install iri20py@git+https://github.com/sunipkm/iri20py
```

## Usage
```py
from iri20py import Iri2020, alt_grid
from datetime import datetime, UTC
import matplotlib.pyplot as plt

# Instantiate the model
iri = Iri2020()
# Note: iri is a singleton (thread safety with FORTRAN)
# Evaluate the model
_, ds = iri.evaluate(
    datetime(2022, 3, 12, 0, 0, 0, tzinfo=UTC),
    40, -70,
    alt_grid()
)

# ds is an xarray Dataset
# Plot electron density profile
ds.Ne.plot(y='alt_km')
plt.show()
```

## Output Dataset Format
- Coordinates
  - Altitude (`alt_km`): Altitude in *km*
- Data Variables (as a function of altitude)
  - Electron density (`Ne`) in *cm*<sup>-3</sup>
  - Electron temperature (`Te`) in *K*
  - Ion temperature (`Ti`) in *K*
  - O<sup>+</sup>, H<sup>+</sup>, He<sup>+</sup>, O<sub>2</sub><sup>+</sup>, NO<sup>+</sup>, N<sup>+</sup> and cluster ion densities (*cm*<sup>-3</sup>)
- Attributes
  - `settings`: JSON string of settings (`iri20py.Settings`) used to evaluate the model.
  - `date`: ISO formatted date and time for which the model was evaluated.
  - `lat` and `lon`: Latitude and longitude for where the model was evaluated.
  - Additional attributes as returned in the `OARR` struct (refer to IRI-2020 documentation).
    These additional attributes are provided as JSON dictionaries containing a `value`, its `unit`,
    a longer name (`long_name`) and an associated `description`, if available.

The dataset is NetCDF4 compatible.

## Example Plot
An example script to generate the following plot is available in the
[`tests/test_iri2020.py`](tests/test_iri2020.py) file.
![Example IRI-2020 Output](tests/iri20.png)

# Citation
If you use this code in your work, please cite the repository:
```bibtex
@software{sunipkm_iri20py_2025,
  author       = {Sunip K. Mukherjee},
  title        = {{iri20py}: A Python Wrapper for the IRI-2020 Empirical Model},
  month        = nov,
  year         = 2025,
  publisher    = {GitHub},
  version      = {v0.0.2},
  doi          = {https://zenodo.org/badge/latestdoi/1089134543},
  url          = {https://github.com/sunipkm/iri20py},
}
```