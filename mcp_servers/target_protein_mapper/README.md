# Target Protein Mapper MCP Server

An MCP server that maps medical symptoms to potential target proteins using the Monarch Initiative, Open Targets, and UniProt APIs.

## Installation

This project uses `uv` for dependency management.

```bash
# Install uv if you haven't already
pip install uv

# Create virtual environment and sync dependencies
uv sync
```

## Usage

### Running the Server

```bash
uv run target-protein-mapper
```

### Running Tests

```bash
uv run pytest tests/
```

## Tools

1.  **get_hpo_ids**: Converts natural language symptoms to HPO IDs.
2.  **find_target_proteins**: Finds target proteins associated with HPO IDs.
3.  **get_protein_details**: Fetches biological function and length for proteins.
