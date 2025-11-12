# Bloomr

[![CI](https://github.com/gnathoi/bloomr/actions/workflows/ci.yml/badge.svg)](https://github.com/gnathoi/bloomr/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/bloomr.svg)](https://pypi.org/project/bloomr/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Made with Rust](https://img.shields.io/badge/Made%20with-Rust-orange.svg)](https://www.rust-lang.org/)

Solve the Mixed Chinese Postman Problem on real road networks. Find the shortest route that traverses every street at least once, handling both one-way and two-way streets.

## Installation

```bash
pip install bloomr
```

## Quick Start

```python
from bloomr import solve_cpp

# Download road network and solve CPP
result = solve_cpp("Monaco")

# View solution
print(result.summary())  # Distance efficiency, route metrics
print(f"GPX route: {result.gpx_path}")
```

## How It Works

Bloomr downloads road networks from OpenStreetMap, identifies degree imbalances caused by one-way streets, and computes near-optimal routes using a hybrid Blossom-Greedy matching approach:

1. Blossom algorithm finds optimal pairings for ~98% of imbalanced nodes
2. Greedy fallback handles remaining nodes when graph disconnectivity prevents full matching
3. Eulerian circuit generates the final route traversing all streets

This hybrid strategy preserves optimality where possible while gracefully handling real-world road network constraints.

## API

### solve_cpp()

```python
solve_cpp(
    place: str = None,
    *,
    graphml_path: Path = None,
    output_dir: Path = None,
    network_type: str = "drive_service",
    simplify: bool = False,
    method: str = "blossom",
    verbose: bool = False,
    visualize: bool = True
)
```

Arguments:

- `place`: Location name (e.g., "Jersey, Channel Islands")
- `graphml_path`: Path to existing GraphML file (alternative to place)
- `output_dir`: Directory for output files (default: `solutions/{region}`)
- `network_type`: OSMnx network type - `"drive"`, `"drive_service"`, `"walk"`, `"bike"`, or `"all"`
- `simplify`: Simplify graph topology (default: False)
- `method`: `"blossom"` (optimal, default) or `"greedy"` (fast approximation)
- `verbose`: Enable detailed logging from Rust solver
- `visualize`: Generate route visualization map (requires matplotlib, contextily)

Returns: `CPPResult` with `gpx_path`, `metrics`, and solution files

### download_graph()

```python
download_graph(
    place: str,
    *,
    output_dir: Path = None,
    network_type: str = "drive_service",
    simplify: bool = False,
    force: bool = False
) -> Path
```

Arguments:

- `place`: Location name for OSMnx (e.g., "San Francisco, California")
- `output_dir`: Directory for GraphML file (default: `graphml_data`)
- `network_type`: OSMnx network type - `"drive"`, `"drive_service"`, `"walk"`, `"bike"`, or `"all"`
- `simplify`: Simplify graph topology (default: False)
- `force`: Force re-download even if cached (default: False)

Returns: Path to saved GraphML file

Example:

```python
from bloomr import download_graph

graph_path = download_graph("San Francisco, California")
result = solve_cpp(graphml_path=graph_path)
```

## Output

Solutions are saved to `solutions/{region}/`:

- `{region}_cpp_route.gpx` - GPS-ready route file
- `{region}_metrics.json` - Efficiency metrics and statistics

Metrics:

- `distance_efficiency` - Proportion of route that's useful coverage (not duplicated)
- `duplication_ratio` - Average times each street is traversed
- `deadhead_percentage` - Percentage of route spent repeating streets

## Architecture

- Python: OSMnx integration, API, visualization
- Rust: Graph algorithms (Blossom, shortest paths, Eulerian circuits)
