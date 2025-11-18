# numba_extinction

**Numba-accelerated implementation of the [`extinction`](https://github.com/kbarbary/extinction) package.**

This package rewrites and extends the functionality of `extinction.py` using [Numba](https://numba.pydata.org/) for performance.
It reproduces the original `extinction` curves (albeit with some ~1e-15 differences due to floating-point arithmetic).

An equivalent implementation of the UV-to-IR extinction curve by [Gordon et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023ApJ...950...86G/abstract) is included and validated against [`dust_extinction`](https://github.com/karllark/dust_extinction) for consistency.

Please check out [`dust_extinction`](https://github.com/karllark/dust_extinction) too! It is much more fleshed-out and feature complete.
This package was developed for personal purposes before I discovered [`dust_extinction`](https://github.com/karllark/dust_extinction) and is not meant to be a replacement.

---

## Installation

You can install `numba_extinction` from PyPI or in editable mode for development.

### Install from source

```bash
# Clone the repository
git clone https://github.com/G-Francio/numba_extinction.git
cd numba_extinction

# Install as a local editable package
pip install -e .
```

### Install from PyPI

```bash
pip install numba_extinction
```

---

## Requirements

The package requires:

* `astropy >= 7.1.1`
* `numba >= 0.62.1`
* `numpy >= 2.3.4`

Optional extras can be installed for validation, convenience, and plotting purposes:

```bash
# Validation and plotting
# Install matplotlib and the packages required to run the example
pip install "numba_extinction[plot]"

# Convenience
# Additionally install IPython, notebooks, and matplotlib
pip install "numba_extinction[ipython]"
```


---

## Links

* [PyPI](https://pypi.org/project/numba-extinction)
* [extinction](https://github.com/kbarbary/extinction)
* [dust_extinction](https://github.com/karllark/dust_extinction)

---

## Authors

**Francesco Guarneri** ([francesco.guarneri@uni-hamburg.de](mailto:francesco.guarneri@uni-hamburg.de))  
**ChatGPT** - For this wonderful `README.md` :)

Licensed under the **MIT License**.
