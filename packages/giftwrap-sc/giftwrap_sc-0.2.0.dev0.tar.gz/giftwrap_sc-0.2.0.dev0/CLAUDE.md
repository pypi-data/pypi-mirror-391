# CLAUDE.md - GIFTwrap Development Guide

## Project Overview

**GIFTwrap** is a Python package for processing and analyzing GIFT-seq (genotyping from image-free technology) data. It provides both a command-line interface (CLI) for transforming FASTQ files into counts matrices and a Python API for downstream analysis of single-cell gapfill data.

### Key Information
- **Language**: Python 3.11+
- **Package Name**: `giftwrap-sc`
- **Repository**: https://github.com/clareaulab/giftwrap
- **Documentation**: https://clareaulab.github.io/giftwrap
- **Version**: 0.2.0-dev
- **Status**: Beta (Development Status 4)

### Main Features
- **Data Processing**: FastQ to counts matrix pipeline for GIFT-seq data
- **Quality Control**: Filtering based on paired WTA (Whole Transcriptome Amplification) data from 10X Cell Ranger
- **Genotype Calling**: Single-cell resolution SNV genotyping from gapfill sequences
- **Spatial Analysis**: Tools for spatial GIFT-seq data analysis and visualization
- **Multiple Technology Support**: Flex, VisiumHD, and custom technology definitions

---

## Development Setup

### Prerequisites
- **Python 3.11+** (required)
- **uv**: Modern Python package manager (https://github.com/astral-sh/uv)
  - Install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Initial Setup
```bash
# Clone the repository
git clone https://github.com/clareaulab/giftwrap.git
cd giftwrap

# Install all dependencies (including optional extras)
uv sync --all-extras --all-groups

# Verify installation
python -c "import giftwrap; print(giftwrap.__version__)"
```

### Dependency Groups
- **Core**: Essential dependencies for basic functionality (Bio, scipy, numpy, pandas, h5py, anndata, matplotlib, etc.)
- **Spatial**: `protobuf`, `spatialdata`, `spatialdata-plot`, `squidpy` (for spatial data processing)
- **Analysis**: `scanpy`, `igraph`, `numba`, `leidenalg`, `pyfamsa`, `logomaker`, `rapidfuzz`, `adjusttext` (for advanced analysis)
- **Docs**: Full documentation build stack (mkdocs, mkdocs-material, mkdocstrings, etc.)

---

## Build, Test, and Development Commands

### Building the Package
```bash
# Build wheel and source distribution
uv build

# Output will be in dist/ directory
# - dist/giftwrap_sc-0.2.0-py3-none-any.whl
# - dist/giftwrap_sc-0.2.0.tar.gz
```

### Documentation
```bash
# Preview documentation locally (requires docs extra)
uv run mkdocs serve
# Visit http://localhost:8000 to view

# Build documentation for deployment
uv run mkdocs build

# Deploy to GitHub Pages (maintainers only)
uv run mkdocs gh-deploy --force
```

### Running the CLI
```bash
# Main pipeline command
giftwrap --probes path/to/probes.xlsx --project fastqs/fastq_prefix -o output_dir/

# Individual pipeline steps
giftwrap-count --help
giftwrap-correct-umis --help
giftwrap-correct-gapfill --help
giftwrap-collect --help
giftwrap-summarize --help

# Utility commands
giftwrap-generate-r > read_giftwrap.R
giftwrap-generate-tech > tech_def.py
giftwrap-convert-probes
giftwrap-revert-probes
```

### Dependency Management
```bash
# Add new dependency
uv add package_name

# Update dependencies to latest compatible versions
uv sync

# Add optional dependency to specific group
uv add --optional spatial package_name

# Update lock file after pyproject.toml changes
uv lock
```

### Python API Usage
```bash
# Launch Python REPL with giftwrap environment
uv run python

# Or in scripts:
import giftwrap as gw
adata = gw.read_h5_file("counts.1.h5")
gw.pp.filter_gapfills(adata)
gw.tl.call_genotypes(adata)
```

---

## Architecture & Key Modules

### Project Structure
```
giftwrap/
├── src/giftwrap/              # Main package source
│   ├── __init__.py            # Package exports and version
│   ├── pipeline.py            # Main CLI orchestrator
│   ├── utils.py               # Core utilities (92KB - largest file)
│   ├── step1_count_gapfills.py      # Process FastQ → probe counts
│   ├── step2_correct_umis.py        # UMI error correction
│   ├── step3_correct_gapfill.py     # Gapfill sequence correction
│   ├── step4_collect_counts.py      # Aggregate counts into matrix
│   ├── step5_summarize_counts.py    # Generate QC reports & plots
│   ├── misc_scripts.py              # Utility scripts (generate_r, generate_tech, etc.)
│   ├── analysis/               # Downstream analysis module
│   │   ├── preprocess.py       # Filtering functions
│   │   ├── tools.py            # Analysis tools (genotype calling, imputation)
│   │   ├── plots.py            # Plotting functions (logo, violin, umap, etc.)
│   │   ├── spatial.py          # Spatial analysis (binning, imputation, spatial plots)
│   │   └── __init__.py
│   ├── resources/              # Data files and templates
│   └── read_gf_h5.R            # R script for reading h5 files
├── docs/                        # Documentation (mkdocs + tutorials)
├── notebooks/                   # Jupyter notebooks for examples
├── tests/ (inferred)           # Tests (if present)
├── pyproject.toml              # Project metadata and dependencies
├── uv.lock                      # Locked dependency versions
├── mkdocs.yml                  # Documentation configuration
└── README.md                    # User-facing readme
```

### Core Data Flow

1. **Input**: FastQ files + probe definition file (TSV/CSV/XLSX)

2. **Processing Pipeline** (5 steps):
   - **Step 1** (count_gapfills): Parse FastQ reads, extract probe barcodes and gapfill sequences
   - **Step 2** (correct_umis): Error-correct UMIs using prefix-tree (PrefixTrie)
   - **Step 3** (correct_gapfill): Error-correct gapfill sequences
   - **Step 4** (collect_counts): Aggregate into sparse cell×feature matrix (h5 format)
   - **Step 5** (summarize_counts): Generate summary statistics and PDF report

3. **Output**: 
   - `counts.N.h5`: Raw counts matrix (sparse, CellxFeature format)
   - `counts.N.filtered.h5`: Quality-filtered counts (if WTA data provided)
   - `fastq_metrics.tsv`: Read-level QC metrics
   - `counts.N.summary.csv`: Cell-level summary statistics
   - `counts.N.summary.pdf`: Visualization report

4. **Analysis** (Python API):
   - Load h5 file into AnnData object
   - Preprocessing: filter low-quality gapfills
   - Genotype calling: SNV genotypes per cell from gapfill sequences
   - Advanced: imputation, spatial analysis, visualization

### Key Abstractions

#### TechnologyFormatInfo (Base Class)
Defines sequencing technology layout: read lengths, barcode positions, constant sequences, etc.
- Subclasses: `FlexFormatInfo`, `VisiumHDFormatInfo`, `VisiumFormatInfo`
- Custom technologies can be defined by subclassing

#### ReadProcessState (Enum)
Tracks processing status for each read:
- EXACT: No corrections needed
- CORRECTED_*: Specific error corrections applied
- FILTERED_*: Reads filtered at various stages
- TOTAL_READS: Placeholder for read counting

#### ProbeParser
Parses probe sequences from read data, performs barcode error correction using computed distance metrics

#### Analysis Modules (under `analysis/`)
- **preprocess.py**: `filter_gapfills()`, `filter_genotypes()`
- **tools.py**: `call_genotypes()`, `intersect_wta()`, `transfer_genotypes()`, `collapse_gapfills()`, `impute_genotypes()`
- **plots.py**: `plot_logo()`, `dotplot()`, `matrixplot()`, `violin()`, `clustermap()`, `umap()`, `tsne()`
- **spatial.py**: `bin()`, `join_with_wta()`, `plot_genotypes()`, `impute_genotypes()`, `recipe_spatial_expression_coclustering()`

### Important Patterns & Conventions

1. **Warning Suppression**: FutureWarnings from dependencies are filtered at package init
2. **Multiprocessing**: Conditional via `maybe_multiprocess()` (cores > 1 triggers Pool)
3. **Streaming Output**: Subprocesses use `streaming_subprocess_run()` for live console feedback
4. **Shared Tries**: PrefixTrie used for efficient barcode/UMI lookup with multiprocessing support
5. **H5 File Format**: Custom dense/sparse matrix storage with metadata
6. **Error Correction**: Uses edit distance metrics (computed differently per barcode type)

---

## Existing Documentation

### Main Documentation Files
- **README.md**: Installation, basic usage, CLI examples, file format descriptions
- **docs/contributing.md**: Developer setup, building, documentation updates, release process
- **docs/index.md**: Main documentation hub with feature overview
- **docs/file_formats.md**: Detailed h5 file structure and format specifications
- **docs/tutorials/**: 
  - `getting_started.md`: Installation and first use
  - `processing_giftseq_data.md`: CLI workflow tutorial
  - `analyzing_giftseq_data.ipynb`: Python API examples
  - `spatial_giftseq.md`: Spatial analysis tutorial
  - `imputation.md`: Genotype imputation guide
  - `seurat_integration.md`: R/Seurat integration
  - `extending_giftwrap.md`: Custom technology definitions
- **docs/cli/**: Auto-generated CLI command reference

### GitHub Configuration
- **.github/workflows/python-publish.yml**: Release automation (build + PyPI publish on GitHub release)
- **.github/workflows/docs.yml**: Auto-deploy docs to GitHub Pages on push/release

---

## Common Development Tasks

### Adding a New Feature

1. **Create feature branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Update code** in appropriate module(s):
   - For CLI: modify `pipeline.py` and relevant `step*.py` files
   - For analysis: add to `src/giftwrap/analysis/*.py`
   - For utilities: extend `src/giftwrap/utils.py`

3. **Update dependencies** if needed:
   ```bash
   uv add package_name
   ```

4. **Update documentation**:
   - Add docstrings (Sphinx format, see existing code)
   - Add/update `.md` files in `docs/`
   - Update `mkdocs.yml` nav if adding new pages

5. **Test locally**:
   ```bash
   uv run python -m your_test_script
   # Or import and test interactively
   ```

6. **Commit and push**:
   ```bash
   git add .
   git commit -m "feat: description of changes"
   git push origin feature/my-feature
   ```

### Updating Dependencies
```bash
# Check for updates
uv pip compile pyproject.toml --upgrade

# Add new dependency (core or optional)
uv add package_name
uv add --optional spatial package_name

# Remove dependency
uv remove package_name

# Update all
uv sync --upgrade
```

### Creating a Release (Maintainers Only)

1. **Update version** in `pyproject.toml`:
   ```toml
   version = "0.2.1"  # Update from 0.2.0-dev
   ```

2. **Build locally** (optional verification):
   ```bash
   uv build
   ```

3. **Create release on GitHub** with tag `vX.Y.Z`:
   - Triggers `python-publish.yml` workflow
   - Automatically builds and publishes to PyPI
   - Uploads wheel to GitHub release

4. **Alternative manual publish**:
   ```bash
   uv publish --token <your-pypi-token>
   ```

### Fixing Documentation

1. Edit files in `docs/` directory
2. Preview: `uv run mkdocs serve`
3. Commit changes
4. On merge to main: auto-deployed via GitHub Actions

---

## Important Implementation Details

### File Reading/Writing
- **FastQ**: Uses `Bio.SeqIO.QualityIO.FastqGeneralIterator` (streaming)
- **H5**: `h5py` for sparse/dense matrices with custom schema
- **Probe Definitions**: `pandas` reads TSV/CSV/XLSX with validation
- **Manifests**: Generated during pipeline, stored as TSV with probe metadata

### Error Correction
- **Barcodes**: Edit distance with position-specific thresholds
- **UMIs**: Prefix-tree based correction for efficiency
- **Gapfill Sequences**: Sequence alignment via edit distance

### Spatial Data
- **VisiumHD Barcodes**: Parse format `s_{resolution:03d}um_{y:05d}_{x:05d}-1` to extract coordinates
- **Integration**: Uses `spatialdata` and `squidpy` libraries
- **Binning**: Aggregate cells to higher resolution for visualization

### Analysis Methods
- **Genotype Calling**: Counts-based thresholding (configurable PCR threshold)
- **Imputation**: Spatial-aware genotype inference
- **Visualization**: Built on scanpy/matplotlib with custom styling

---

## Testing & Quality

The repository includes:
- Sample data in `sample_data/` directory (test datasets)
- Jupyter notebooks in `notebooks/` for interactive testing
- Miscellaneous test scripts in `misc/`

**To run tests**:
```bash
# Run any Python test files
uv run python misc/test.py

# Run notebook cells
uv run jupyter notebook notebooks/cell_line_visium_analysis.ipynb
```

---

## Key Dependencies Summary

| Dependency | Purpose | Required |
|-----------|---------|----------|
| biopython | FastQ parsing | Yes |
| scipy/numpy | Numerical computing | Yes |
| pandas | Data manipulation | Yes |
| h5py | HDF5 file I/O | Yes |
| anndata | Single-cell data structure | Yes |
| matplotlib | Plotting | Yes |
| tqdm | Progress bars | Yes |
| rich-argparse | CLI help formatting | Yes |
| prefixtrie | Efficient barcode matching | Yes |
| scanpy | Single-cell analysis | Optional (analysis) |
| spatialdata | Spatial data framework | Optional (spatial) |
| squidpy | Spatial analysis | Optional (spatial) |

---

## Resources & References

- **Official Docs**: https://clareaulab.github.io/giftwrap
- **GitHub**: https://github.com/clareaulab/giftwrap
- **PyPI**: https://pypi.org/project/giftwrap-sc/
- **Issues**: https://github.com/clareaulab/giftwrap/issues

---

## Notes for Contributors

1. **Backward Compatibility**: This is in beta (v0.2.0-dev). Breaking changes are possible.
2. **Type Hints**: Codebase uses type hints; please maintain this style.
3. **Warning Handling**: FutureWarnings are suppressed at package level for dependency compatibility.
4. **Multiprocessing**: Always use `maybe_multiprocess()` for core > 1 logic.
5. **Documentation**: Use Sphinx docstring format (evident in existing code).
6. **Testing Data**: Use `sample_data/` directory for reproducible examples.
7. **Performance**: Large files use streaming and sparse matrices; be mindful of memory.

---

**Last Updated**: 2025-10-24  
**Python Support**: 3.11+  
**Package Manager**: uv (https://astral.sh/uv)
