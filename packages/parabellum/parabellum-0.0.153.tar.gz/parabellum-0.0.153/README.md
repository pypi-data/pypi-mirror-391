# Parabellum

Parabellum is a research sandbox for experimenting with large-scale, team-based engagements on top of real-world geography.
It builds a differentiable JAX environment from OpenStreetMap data, lets you configure arbitrary unit types and combinations,
and can render animated replays of each rollout.

## Features

- Imports building footprints and basemaps around any geocoded location to ground the simulation in real terrain.
- Supports configurable blue and red team orders of battle, unit capabilities, and sensor ranges via YAML.
- Runs entirely on top of JAX for easy batching, vectorisation, and accelerator support.
- Provides convenience utilities for quantising state to images and exporting GIFs of simulated trajectories.
- Uses `mlxp` to manage experiments, making it simple to sweep parameters or override settings from the command-line.

## Repository Layout

- `main.py` – entry point that launches simulations, saves trajectories, and writes GIFs.
- `parabellum/` – core package with the `Env` class, datatypes, and visualisation helpers.
- `conf/config.yaml` – default experiment configuration (location, unit counts, rules, and runtime parameters).
- `logs/`, `cache/` – directories created by `mlxp` and helper libraries for outputs and cached assets.

## Requirements

- Python 3.11 (the project pins `>=3.11,<3.12`).
- System libraries needed by geospatial packages such as GDAL/PROJ (required by `rasterio`, `cartopy`, and `osmnx`).
- Network access the first time you generate a new map so OpenStreetMap tiles and features can be downloaded.

## Installation

The project is set up for [uv](https://github.com/astral-sh/uv); a lockfile is included.

```bash
# create (or reuse) a virtual environment and install dependencies
uv sync
```

## Running a Simulation

With dependencies installed, run the main entry point. `mlxp` will load `conf/config.yaml` by default and create a run directory under `logs/`.

```bash
uv run python main.py
```

Each execution downloads the requested map (if not cached), simulates the configured number of steps,
and stores an animated replay (that optionally overlays unit positions on the base imagery).

To override configuration values from the CLI, append Hydra-style assignments:

```bash
uv run python main.py steps=400 sims=4 teams.blu.troop=6
```

## Configuration

All runtime settings live in `conf/config.yaml`:

- Top-level parameters (`steps`, `knn`, `noise`, etc.) control simulation length, perception range, and stochasticity.
- `place` and `size` define the map to fetch from OpenStreetMap and its pixel resolution.
- `teams` lists unit counts per type for the blue (`blu`) and red (`red`) forces.
- `rules` encodes per-unit attributes such as health, damage, movement speed, and sight radius.

`mlxp` writes the resolved configuration for each run under `logs/`, making it straightforward to audit experiments.

## Programmatic Use

You can instantiate the environment directly for integration with custom training or evaluation loops:

```python
from omegaconf import OmegaConf
from jax import random
from parabellum import Env

cfg = OmegaConf.load("conf/config.yaml")
env = Env(cfg)
obs, state = env.init(random.PRNGKey(0))
# ... compute actions and call env.step(...) as needed
```

The `Env` exposes JAX-native arrays for unit state, making it easy to vectorise across simulations or plug into learning pipelines.
