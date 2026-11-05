# GAM Workshop – Dortmund 2025

Material for a workshop on Generalized Additive Models (GAMs):

| Folder | Contents |
|---|---|
| `Slides/` | Lecture slides (PDF) |
| `R_demos/` | R demo scripts using `mgcv`, `mgcViz`, `qgam`, ... (with rendered `.html` versions) |
| `Py_demos/` | Python versions of the demos as Jupyter notebooks, using [`pymgcv`](https://github.com/SmoothForge/pymgcv) |
| `exercises/` | Exercise sheet and solutions |
| `Papers/` | Background reading |

This README explains how to set up a single environment that can run **both** the
R demos and the Python demos, using [pixi](https://pixi.sh).

## Why pixi?

`pymgcv` is a Python wrapper around the R package `mgcv`. It calls R through
`rpy2`, so Python needs a working R installation with `mgcv`. Pixi installs Python,
R, the R packages and the Python packages together from
[conda-forge](https://conda-forge.org) into one project-local environment
(`.pixi/`). You don't need a system-wide R or Python, and nothing outside this
folder is changed.

The environment is defined in [`pixi.toml`](pixi.toml), and the exact versions are
locked in `pixi.lock`.

## 1. Install pixi

macOS / Linux:

```bash
curl -fsSL https://pixi.sh/install.sh | sh
```

Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm -useb https://pixi.sh/install.ps1 | iex"
```

Restart your terminal, then check the installation:

```bash
pixi --version
```

See the [pixi installation docs](https://pixi.sh/latest/#installation) for other options.

## 2. Create the environment

From the root of this repository:

```bash
pixi install
```

This installs:

- **Python** (≥ 3.11) with `numpy`, `pandas`, `scipy`, `matplotlib`, `rpy2`, plus JupyterLab to run the notebooks
- **pymgcv** (from PyPI)
- **R** with `mgcv`, `mgcViz`, `qgam`, `MASS`, `dplyr`, `magrittr`, `mvnfast`, `remotes`
- C/C++/Fortran compilers, used in the next step to build R packages from source

The first run takes a few minutes. Later runs are fast.

## 3. Install the GitHub-only R packages

Some R demos use packages that are not on CRAN or conda-forge:

| Package | Source | Used in |
|---|---|---|
| `testGam` | [mfasiolo/testGam](https://github.com/mfasiolo/testGam) | All demos (datasets) |
| `gamFactory` | [mfasiolo/gamFactory](https://github.com/mfasiolo/gamFactory) | `3_multi_gams.R` |
| `SCM` | [VinGioia90/SCM](https://github.com/VinGioia90/SCM) | `3_multi_gams.R` |

Install them into the pixi environment once:

```bash
pixi run install-r-github
```

The Python demos don't need this step. `pymgcv` only needs `mgcv`, and the
datasets are downloaded directly from GitHub.

## 4. Check the setup

```bash
pixi run check
```

This loads the main R packages and prints their versions, then imports `pymgcv`
from Python and confirms it can reach R's `mgcv`. To check only one side, run
`pixi run check-py` or `pixi run check-r`.

## 5. Run the demos

### R demos

```bash
pixi run r-demo 1_Intro_Gefcom14.R
```

or start an interactive R session in the environment:

```bash
pixi run R
```

### Python demos (Jupyter notebooks)

The Python demos are Jupyter notebooks (`Py_demos/*.ipynb`). Start JupyterLab in the
pixi environment:

```bash
pixi run lab
```

This opens JupyterLab in your browser, showing the `Py_demos/` folder. Then:

1. Double-click a notebook, e.g. `1_Intro_Gefcom14.ipynb`.
2. Check that the kernel (top right) is **Python 3 (ipykernel)**. This is the pixi
   environment's Python, so `pymgcv` and R are available.
3. Run the cells one by one with **Shift + Enter**, or run everything with
   **Run → Run All Cells**.

Plots appear directly below the cells. To stop JupyterLab, press **Ctrl + C** in the
terminal twice.

To run every notebook from the command line without opening a browser (for example,
to check that they all still work), run:

```bash
pixi run run-notebooks
```

This executes the notebooks and saves the outputs into the `.ipynb` files.

### Using an editor instead of the browser

**VS Code:** install the *Python* and *Jupyter* extensions, open a notebook, click
**Select Kernel** (top right) → *Python Environments* and pick
`.pixi/envs/default/bin/python` (`.pixi\envs\default\python.exe` on Windows). If it
isn't listed, run `pixi install` first and reload the window.

**RStudio / Positron:** for the R demos, point the R interpreter to
`.pixi/envs/default/bin/R`, or launch the IDE from a `pixi shell`.

### Working in a terminal

To activate the environment in your current terminal (similar to `conda activate`):

```bash
pixi shell        # type `exit` to leave
jupyter lab       # or: Rscript R_demos/1_Intro_Gefcom14.R
```

## Tips for writing Python demos with pymgcv

- **Factors:** R turns character columns (e.g. `Dow`) into factors automatically,
  but pymgcv doesn't. Convert them explicitly, otherwise `fit` fails with
  `TypeError: Variable Dow is of unsupported type ...`:

  ```python
  data["Dow"] = data["Dow"].astype("category")
  ```

- **Smoothing-parameter method:** `mgcv::gam()` uses GCV by default, while
  pymgcv uses REML. To reproduce the R numbers, pass `method="GCV.Cp"` to `fit`.
- **Datasets:** load the `testGam` datasets straight from GitHub:

  ```python
  from pymgcv.utils import load_rdata_dataframe_from_url
  url = "https://raw.githubusercontent.com/mfasiolo/testGam/master/data/gefcom_small.rda"
  data = load_rdata_dataframe_from_url(url)
  ```

- Full API reference: <https://smoothforge.github.io/pymgcv/>.

## Adding packages

```bash
pixi add r-<package>           # R package from conda-forge, e.g. pixi add r-gratia
pixi add <package>             # Python package from conda-forge
pixi add --pypi <package>      # Python package from PyPI
```

Commit the updated `pixi.toml` and `pixi.lock` so everyone gets the same environment.

## Troubleshooting

- **`R_HOME` / `libR` errors from rpy2:** run Python through pixi (`pixi run` or
  `pixi shell`), not a system Python, so that rpy2 finds the R inside `.pixi/`.
- **`install-r-github` fails while compiling:** make sure you ran `pixi install`
  first so the compilers are available. On macOS, the Xcode command line tools
  may also be needed: `xcode-select --install`.
- **Start from scratch:** delete the `.pixi/` folder and run `pixi install` again.
