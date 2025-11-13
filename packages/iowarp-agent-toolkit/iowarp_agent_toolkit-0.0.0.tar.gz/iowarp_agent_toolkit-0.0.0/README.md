# iowarp-agent-toolkit

[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.11%2B-purple)](https://gofastmcp.com)

**IOWarp Agent Toolkit** - PyPI Package for IOWarp Agent Toolkit

A comprehensive collection of Model Context Protocol (MCP) servers for scientific computing, HPC resources, and research datasets. Based on the [agent-toolkit](https://github.com/iowarp/agent-toolkit) project from the Gnosis Research Center at Illinois Institute of Technology.

## Features

- **15+ MCP Servers** for scientific computing and HPC
- **Unified Interface** for AI agents to work with research tools
- **Scientific Data Formats**: HDF5, Parquet, ADIOS
- **HPC Integration**: Slurm job management, Lmod environment modules
- **Research Tools**: ArXiv paper discovery, data visualization
- **System Utilities**: Hardware info, compression, parallel sorting

## Installation

### Basic Installation

```bash
pip install iowarp-agent-toolkit
```

### With Specific MCP Servers

```bash
# Install with HDF5 support
pip install iowarp-agent-toolkit[hdf5]

# Install with multiple servers
pip install iowarp-agent-toolkit[hdf5,slurm,arxiv]

# Install all MCP servers
pip install iowarp-agent-toolkit[all]
```

## Available MCP Servers

- **hdf5** - HDF5 FastMCP for scientific data access
- **parquet** - Apache Parquet data access
- **pandas** - Data analysis and manipulation
- **slurm** - HPC job management
- **arxiv** - Research paper discovery
- **plot** - Data visualization
- **compression** - File compression tools
- **lmod** - Environment module management
- **chronolog** - Data logging
- **adios** - Advanced I/O system
- **ndp** - NDP dataset discovery
- **darshan** - I/O characterization
- **jarvis** - System configuration
- **node-hardware** - Hardware information
- **parallel-sort** - Parallel sorting

## Usage

### Command Line

```bash
# List all available MCP servers
iowarp-agent-toolkit list-servers

# Show information about a specific server
iowarp-agent-toolkit info hdf5

# Show version
iowarp-agent-toolkit version
```

### Python API

```python
import iowarp_agent_toolkit

print(iowarp_agent_toolkit.__version__)
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/iowarp/iowarp-agent-toolkit.git
cd iowarp-agent-toolkit

# Install in development mode with all dependencies
pip install -e ".[dev,all]"
```

### Running Tests

```bash
pytest
```

### Building the Package

```bash
python -m build
```

## License

This project is licensed under the BSD-3-Clause License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Based on the [agent-toolkit](https://github.com/iowarp/agent-toolkit) project developed by the Gnosis Research Center at Illinois Institute of Technology with NSF support.

## Links

- **Homepage**: [https://iowarp.github.io/agent-toolkit/](https://iowarp.github.io/agent-toolkit/)
- **Repository**: [https://github.com/iowarp/agent-toolkit](https://github.com/iowarp/agent-toolkit)
- **PyPI**: [https://pypi.org/project/iowarp-agent-toolkit/](https://pypi.org/project/iowarp-agent-toolkit/)
