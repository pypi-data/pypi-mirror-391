# How to Use `pyrxiv` CLI

This guide explains how to use the **pyrxiv** command-line interface (CLI) to search and download arXiv papers.

## Table of Contents

- [Installation](#installation)
- [Available Commands](#available-commands)
- [Pipeline Overview](#pipeline-overview)
- [Command 1: search_and_download](#command-1-search_and_download)
  - [Basic Usage](#basic-usage)
  - [Advanced Usage](#advanced-usage)
  - [Options Reference](#options-reference)
- [Command 2: download_pdfs](#command-2-download_pdfs)
- [Complete Pipeline Examples](#complete-pipeline-examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Installation

Install `pyrxiv` using pip:

```bash
pip install pyrxiv
```

## Available Commands

`pyrxiv` provides two main commands:

1. **`search_and_download`** - Search for papers in a specific arXiv category and download them
2. **`download_pdfs`** - Download PDFs from existing HDF5 metadata files

To see all available commands:

```bash
pyrxiv --help
```

## Pipeline Overview

The typical `pyrxiv` workflow follows these steps:

1. **Search and Filter**: Use `search_and_download` to:

   - Fetch papers from a specific arXiv category
   - Optionally filter papers using a regex pattern
   - Download PDFs and/or save metadata to HDF5 files
2. **Process or Analyze**: Work with the downloaded papers and metadata
3. **Re-download if Needed**: Use `download_pdfs` to re-download PDFs from HDF5 metadata files if you previously deleted them

## Command 1: search_and_download

The `search_and_download` command searches for papers in arXiv and downloads them to a specified directory.

### Basic Usage

Download the 5 most recent papers from the default category (`cond-mat.str-el`):

```bash
pyrxiv search_and_download
```

Download 10 papers from a specific category:

```bash
pyrxiv search_and_download --category physics.optics --n-papers 10
```

### Advanced Usage

#### Filtering with Regex Patterns

Download papers whose text contains a specific matched regex pattern. When using `--regex-pattern`, pyrxiv will continue fetching papers until it finds the specified number that match the pattern:

```bash
pyrxiv search_and_download --category cond-mat.str-el --regex-pattern "DMFT|Hubbard" --n-papers 5
```

**Important**: Papers that don't match the regex pattern are automatically discarded and not downloaded.

#### Resuming from a Specific Paper

Resume downloading from a specific arXiv ID:

```bash
pyrxiv search_and_download --category cond-mat.str-el --start-id "2201.12345v1" --n-papers 10
```

**Important**: you have to add the full arXiv ID, including the versioning part.

Resume from the last downloaded paper in your download directory:

```bash
pyrxiv search_and_download --category cond-mat.str-el --start-from-filepath True --n-papers 10
```

These options are important if your search and download process abruptly stopped while processing the number of papers.

#### Saving Metadata to HDF5

Save both PDFs and metadata to HDF5 files:

```bash
pyrxiv search_and_download --category cond-mat.str-el --regex-pattern "DMFT|Hubbard" --n-papers 5 --save-hdf5
```

#### Saving Only Metadata (No PDFs)

If you only need metadata and want to save storage:

```bash
pyrxiv search_and_download --category cond-mat.str-el --n-papers 5 --save-hdf5 --delete-pdf
```

#### Saving Only PDFs (No HDF5)

If you only need PDFs and want to clean up metadata files:

```bash
pyrxiv search_and_download --category cond-mat.str-el --n-papers 5 --save-hdf5 --delete-hdf5
```

**Note**: You must use `--save-hdf5` even if you're deleting HDF5 files, as the files need to be created first before deletion.

**Note 2**: Yes, this option does not make any sense, but GitHub Copilot wrote this and thought it was funny to keep it :-)

#### Customizing PDF Text Extraction

Choose a different PDF loader:

```bash
pyrxiv search_and_download --category cond-mat.str-el --loader pypdf --n-papers 5
```

Disable text cleaning (keep references and extra whitespace):

```bash
pyrxiv search_and_download --category cond-mat.str-el --clean-text False --n-papers 5
```

#### Custom Download Path

Specify a custom directory for downloads:

```bash
pyrxiv search_and_download --download-path my_papers --category cond-mat.str-el --n-papers 5
```

### Options Reference

| Option                    | Short      | Description                                            | Default             |
| ------------------------- | ---------- | ------------------------------------------------------ | ------------------- |
| `--download-path`       | `-path`  | Path for downloading PDFs and HDF5 files               | `data`            |
| `--category`            | `-c`     | arXiv category to search                               | `cond-mat.str-el` |
| `--n-papers`            | `-n`     | Number of papers to download                           | `5`               |
| `--regex-pattern`       | `-regex` | Regex pattern to filter papers                         | None                |
| `--start-id`            | `-s`     | arXiv ID to start from                                 | None                |
| `--start-from-filepath` | `-sff`   | Resume from last downloaded paper                      | `False`           |
| `--loader`              | `-l`     | PDF text extraction loader (`pdfminer` or `pypdf`) | `pdfminer`        |
| `--clean-text`          | `-ct`    | Clean extracted text (remove references, whitespace)   | `True`            |
| `--save-hdf5`           | `-h5`    | Save metadata to HDF5 files                            | `False`           |
| `--delete-pdf`          | `-dp`    | Delete PDFs after processing                           | `False`           |
| `--delete-hdf5`         | `-dh5`   | Delete HDF5 files after processing                     | `False`           |

## Command 2: download_pdfs

The `download_pdfs` command downloads PDFs from existing HDF5 metadata files. This is useful if you previously saved only metadata or deleted PDFs to save space.

### Usage

Download PDFs from HDF5 files in the default `data/` directory:

```bash
pyrxiv download_pdfs
```

Download PDFs from HDF5 files in a custom directory:

```bash
pyrxiv download_pdfs --data-path my_papers
```

### Options

| Option          | Short     | Description                 | Default  |
| --------------- | --------- | --------------------------- | -------- |
| `--data-path` | `-path` | Path where HDF5 files exist | `data` |

## Complete Pipeline Examples

### Example 1: Basic Paper Collection

Collect 10 recent papers from condensed matter physics:

```bash
# Download papers
pyrxiv search_and_download --category cond-mat.str-el --n-papers 10

# Papers will be saved in ./data/
```

### Example 2: Filtered Search with Metadata

Search for papers about DMFT or Hubbard models, saving both PDFs and metadata:

```bash
# Download and filter papers
pyrxiv search_and_download \
  --category cond-mat.str-el \
  --regex-pattern "DMFT|Hubbard" \
  --n-papers 5 \
  --save-hdf5

# Work with the downloaded papers...

# If you later delete PDFs to save space, you can re-download them:
pyrxiv download_pdfs
```

### Example 3: Metadata-Only Collection

Collect metadata without keeping PDFs (useful for building a searchable database):

```bash
# Download papers, extract text, save metadata, delete PDFs
pyrxiv search_and_download \
  --category physics.optics \
  --n-papers 20 \
  --save-hdf5 \
  --delete-pdf

# Your ./data/ directory will contain only .hdf5 files with metadata and extracted text
```

### Example 4: Continuous Collection

Set up a continuous collection workflow:

```bash
# First batch
pyrxiv search_and_download --category cond-mat.str-el --n-papers 10 --save-hdf5

# Later, resume from where you left off
pyrxiv search_and_download \
  --category cond-mat.str-el \
  --start-from-filepath True \
  --n-papers 10 \
  --save-hdf5
```

### Example 5: Multi-Step Research Pipeline

A complete research workflow:

```bash
# Step 1: Collect papers matching your research topic
pyrxiv search_and_download \
  --category cond-mat.str-el \
  --regex-pattern "topological insulator|Weyl semimetal" \
  --n-papers 20 \
  --save-hdf5 \
  --download-path research_papers

# Step 2: Analyze the collected papers (your custom scripts)
# ... perform analysis on PDFs and HDF5 metadata ...

# Step 3: Clean up PDFs if you only need metadata going forward
rm research_papers/*.pdf

# Step 4: Later, re-download specific PDFs you need
pyrxiv download_pdfs --data-path research_papers
```

## Best Practices

1. **Start Small**: Begin with a small number of papers (e.g., `--n-papers 5`) to test your setup and regex patterns.
2. **Use Meaningful Regex**: When using `--regex-pattern`, make sure your pattern is specific enough to avoid false positives but broad enough to capture relevant papers.
3. **Save Metadata**: Use `--save-hdf5` to preserve paper metadata, which is useful for later analysis and record-keeping.
4. **Organize by Category**: Use different download paths for different categories to keep your papers organized:

   ```bash
   pyrxiv search_and_download --download-path papers/condensed_matter --category cond-mat.str-el
   pyrxiv search_and_download --download-path papers/optics --category physics.optics
   ```
5. **Resume Capability**: Use `--start-from-filepath True` when continuing a previous download session to avoid re-downloading papers.
6. **Storage Management**:

   - Use `--delete-pdf` with `--save-hdf5` if you primarily need metadata and text content
   - Use `download_pdfs` later to retrieve specific PDFs when needed
7. **Text Extraction**: The default `pdfminer` loader generally works well, but if you encounter issues with specific PDFs, try `--loader pypdf`.
8. **Monitor Progress**: The CLI displays a progress bar during downloads. For large batches, be patient as the tool may need to fetch many papers to find matches for your regex pattern.

## Troubleshooting

### No papers match my regex pattern

- Try broadening your regex pattern
- Check the pattern syntax is correct
- Remember that `pyrxiv` searches the full text of papers, not just titles or abstracts

### Downloads are slow

- arXiv has rate limits; `pyrxiv` respects these
- When using regex filtering, the tool must download and process papers until it finds enough matches
- Consider reducing `--n-papers` or using a less restrictive regex pattern

### PDF extraction errors

- Try switching between `--loader pdfminer` and `--loader pypdf`
- Some papers may have PDF issues; these will be skipped automatically

### Can't find HDF5 files

- Ensure you used `--save-hdf5` when running `search_and_download`
- Check that the `--data-path` matches where you saved the files

---

For more information, see the [main README](../README.md) or visit the [`pyrxiv` GitHub repository](https://github.com/JosePizarro3/pyrxiv).
