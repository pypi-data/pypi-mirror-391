import re
import time
from pathlib import Path

import click
import h5py
import numpy as np

from pyrxiv.datamodel import ArxivPaper
from pyrxiv.download import ArxivDownloader
from pyrxiv.extract import TextExtractor
from pyrxiv.fetch import ArxivFetcher
from pyrxiv.logger import logger


def run_search_and_download(
    download_path: Path = Path("data"),
    category: str = "cond-mat.str-el",
    n_papers: int = 5,
    regex_pattern: str = "",
    start_id: str | None = None,
    start_from_filepath: bool = False,
    loader: str = "pdfminer",
    clean_text: bool = True,
    save_hdf5: bool = False,
    delete_pdf: bool = False,
    delete_hdf5: bool = False,
) -> tuple[list[Path], list["ArxivPaper"]]:
    """
    Searches for a specific number of papers `n_papers` in arXiv for a specified `category` and downloads
    their PDFs in `download_path`. Optionally, metadata can be saved to HDF5 files.

    If `regex_pattern` is specified, only the papers that contain the pattern will be downloaded.
    If `start_id` is specified, the search will start from that ID.
    If `start_from_filepath` is True, the search will start from the last downloaded paper's ID.
    If `loader` is specified, the text will be extracted using the corresponding loader.
    If `clean_text` is True, the extracted text will be cleaned by removing references and unnecessary whitespaces.
    If `save_hdf5` is True, the metadata will be saved to HDF5 files in `download_path`.
    If `delete_pdf` is True, PDFs will be deleted after processing (useful when only HDF5 is needed).
    If `delete_hdf5` is True, HDF5 files will be deleted after processing (useful when only PDFs are needed).

    Args:
        download_path (Path, optional): The path for downloading the arXiv PDFs. Defaults to Path("data").
        category (str, optional): The arXiv category on which the papers will be searched. Defaults to "cond-mat.str-el".
        n_papers (int, optional): The number of arXiv papers to be fetched and downloaded.
            If `regex_pattern` is not specified, this would correspond to the n_papers starting from the newest in the `category`. Defaults to 5.
        regex_pattern (str, optional): If specified, this regex pattern is searched in the arXiv papers so only the ones with
            the corresponding match will be downloaded. Defaults to "".
        start_id (str | None, optional): If specified, the search will start from this arXiv ID. Defaults to None.
        start_from_filepath (bool, optional): If True, the search will start from the last downloaded arXiv ID. Otherwise, it will start from the
            newest papers in the `category`. Defaults to False.
        loader (str, optional): PDF loader to use for extracting text from the downloaded PDFs.
            Defaults to "pdfminer". Available loaders: "pdfminer", "pypdf".
        clean_text (bool, optional): If True, the extracted text will be cleaned by removing references and unnecessary whitespaces.
            Defaults to True.
        save_hdf5 (bool, optional): If True, the metadata will be saved to HDF5 files in `download_path`. Defaults to False.
        delete_pdf (bool, optional): If True, PDFs will be deleted after processing. Defaults to False.
        delete_hdf5 (bool, optional): If True, HDF5 files will be deleted after processing. Defaults to False.

    Returns:
        tuple[list[Path], list[ArxivPaper]]: A tuple containing a list of Paths to the arXiv papers and a list of ArxivPaper objects
            with the extracted text.
    """
    if loader not in ["pdfminer", "pypdf"]:
        raise ValueError(
            f"Invalid loader: {loader}. Available loaders: 'pdfminer', 'pypdf'."
        )

    # check if `download_path` exists, and if not, create it
    download_path = Path(download_path)
    download_path.mkdir(parents=True, exist_ok=True)

    # Initializing classes
    fetcher = ArxivFetcher(
        download_path=download_path,
        category=category,
        start_id=start_id,
        start_from_filepath=start_from_filepath,
        logger=logger,
    )
    downloader = ArxivDownloader(download_path=download_path, logger=logger)
    extractor = TextExtractor(logger=logger)

    pattern_files: list[Path] = []
    pattern_papers: list[ArxivPaper] = []
    with click.progressbar(
        length=n_papers, label="Downloading and processing papers"
    ) as bar:
        while len(pattern_papers) < n_papers:
            papers = fetcher.fetch(
                n_papers=n_papers,
                n_pattern_papers=len(pattern_papers),
            )
            for paper in papers:
                try:
                    pdf_path = downloader.download_pdf(arxiv_paper=paper)
                    text = extractor.get_text(pdf_path=pdf_path, loader=loader)
                except Exception as e:
                    logger.error(f"Error processing paper {paper.id}: {e}")
                    continue

                if not text:
                    logger.info("No text extracted from the PDF.")
                    continue
                if clean_text:
                    text = extractor.delete_references(text=text)
                    text = extractor.clean_text(text=text)

                # Deleting downloaded PDFS that do not match the regex pattern
                regex = re.compile(regex_pattern) if regex_pattern else None
                if regex and not regex.search(text):
                    pdf_path.unlink()
                    continue
                logger.info(
                    f"Paper {paper.id} matches the regex pattern: {regex_pattern}."
                    " Keeping PDF file."
                )

                # If the paper matches the regex_pattern, store text in the corresponding ArxivPaper object
                paper.text = text
                paper.pdf_loader = loader

                # Optionally save the paper metadata to an HDF5 file
                hdf_path = None
                if save_hdf5:
                    hdf_path = download_path / f"{paper.id}.hdf5"
                    with h5py.File(hdf_path, "a") as h5f:
                        _ = paper.to_hdf5(hdf_file=h5f)

                # Handle optional deletion of files
                if delete_pdf and pdf_path.exists():
                    pdf_path.unlink()
                if delete_hdf5 and hdf_path and hdf_path.exists():
                    hdf_path.unlink()

                # Appending the PDF file and paper to the lists
                pattern_files.append(pdf_path if not delete_pdf else hdf_path)
                pattern_papers.append(paper)
                bar.update(1)

                if len(pattern_papers) >= n_papers:
                    break
    return pattern_files, pattern_papers


@click.group(help="Entry point to run `pyrxiv` CLI commands.")
def cli():
    pass


@cli.command(
    name="search_and_download",
    help="Searchs papers in arXiv for a specified category and downloads them in a specified path.",
)
@click.option(
    "--download-path",
    "-path",
    type=str,
    default="data",
    required=False,
    help="""
    (Optional) The path for downloading the arXiv PDFs and, optionally (if set with --save-hdf5), the HDF5 metadata files. Defaults to "data".
    """,
)
@click.option(
    "--category",
    "-c",
    type=str,
    default="cond-mat.str-el",
    required=False,
    help="""
    (Optional) The arXiv category on which the papers will be searched. Defaults to "cond-mat.str-el".
    """,
)
@click.option(
    "--n-papers",
    "-n",
    type=int,
    default=5,
    required=False,
    help="""
    (Optional) The number of arXiv papers to be fetched and downloaded. If `regex-pattern` is not specified, this
    would correspond to the n_papers starting from the newest in the `category`. Defaults to 5.
    """,
)
@click.option(
    "--regex-pattern",
    "-regex",
    type=str,
    required=False,
    help="""
    (Optional) If specified, this regex pattern is searched in the arXiv papers so only the ones with
    the corresponding match will be downloaded.
    """,
)
@click.option(
    "--start-id",
    "-s",
    type=str,
    required=False,
    help="""
    (Optional) If specified, the search will start from this arXiv ID. This is useful for resuming the search
    from a specific point. If not specified, the search will start from the newest papers in the `category`.
    """,
)
@click.option(
    "--start-from-filepath",
    "-sff",
    type=bool,
    default=False,
    required=False,
    help="""
    (Optional) If specified, the search will start from the last downloaded arXiv ID. This is useful for resuming
    the search from a specific point. If not specified, the search will start from the newest papers in the `category`.
    """,
)
@click.option(
    "--loader",
    "-l",
    type=click.Choice(["pdfminer", "pypdf"], case_sensitive=False),
    default="pdfminer",
    required=False,
    help="""
    (Optional) PDF loader to use for extracting text from the downloaded PDFs. Defaults to "pdfminer".
    Available loaders: "pdfminer", "pypdf".
    """,
)
@click.option(
    "--clean-text",
    "-ct",
    type=bool,
    default=True,
    required=False,
    help="""
    (Optional) If True, the extracted text will be cleaned by removing references and unnecessary whitespaces.
    Defaults to True.
    """,
)
@click.option(
    "--save-hdf5",
    "-h5",
    is_flag=True,
    default=False,
    required=False,
    help="""
    (Optional) If True, the metadata will be saved to HDF5 files in `download_path`. Defaults to False.
    """,
)
@click.option(
    "--delete-pdf",
    "-dp",
    is_flag=True,
    default=False,
    required=False,
    help="""
    (Optional) If True, PDFs will be deleted after processing. Useful when only HDF5 metadata is needed. Defaults to False.
    """,
)
@click.option(
    "--delete-hdf5",
    "-dh5",
    is_flag=True,
    default=False,
    required=False,
    help="""
    (Optional) If True, HDF5 files will be deleted after processing. Useful when only PDFs are needed. Defaults to False.
    """,
)
def search_and_download(
    download_path,
    category,
    n_papers,
    regex_pattern,
    start_id,
    start_from_filepath,
    loader,
    clean_text,
    save_hdf5,
    delete_pdf,
    delete_hdf5,
):
    start_time = time.time()

    run_search_and_download(
        download_path=Path(download_path),
        category=category,
        n_papers=n_papers,
        regex_pattern=regex_pattern,
        start_id=start_id,
        start_from_filepath=start_from_filepath,
        loader=loader,
        clean_text=clean_text,
        save_hdf5=save_hdf5,
        delete_pdf=delete_pdf,
        delete_hdf5=delete_hdf5,
    )

    elapsed_time = time.time() - start_time
    click.echo(f"Downloaded arXiv papers in {elapsed_time:.2f} seconds\n\n")


@cli.command(
    name="download_pdfs",
    help="Downloads the PDFs of the arXiv papers stored in HDF5 files in a specified path.",
)
@click.option(
    "--data-path",
    "-path",
    type=str,
    default="data",
    required=False,
    help="""
    (Optional) The path where the HDF5 files with the arXiv papers metadata exist. The downloaded PDFs will be stored in there as well. Defaults to "data".
    """,
)
def download_pdfs(data_path):
    start_time = time.time()

    # check if `data_path` exists, and if not, create it
    data_path = Path(data_path)
    if not data_path.exists():
        raise click.ClickException(f"The specified path {data_path} does not exist.")

    downloader = ArxivDownloader(download_path=data_path, logger=logger)

    # Loops over all HDF5 files in the `data_path` and downloads the corresponding PDFs
    papers_to_download = {}
    # Use HDF5 files from the data path
    hdf5_files = list(data_path.glob("*.hdf5"))
    if not hdf5_files:
        raise click.ClickException(f"No HDF5 files found in {data_path}.")

    for file in hdf5_files:
        try:
            paper = ArxivPaper.from_hdf5(file=file)
            papers_to_download[str(file)] = paper
        except Exception as e:
            logger.error(f"Failed to load HDF5 file {file}: {e}")

    failed_downloads = []
    with click.progressbar(
        length=len(papers_to_download), label="Downloading PDFs from HDF5 files"
    ) as bar:
        for identifier, paper in papers_to_download.items():
            try:
                _ = downloader.download_pdf(arxiv_paper=paper)
            except Exception as e:
                failed_downloads.append(identifier)
                logger.error(f"Failed to download PDF for {identifier}: {e}")
            bar.update(1)

    elapsed_time = time.time() - start_time
    click.echo(f"Downloaded arXiv papers in {elapsed_time:.2f} seconds\n\n")

    if failed_downloads:
        click.echo("\nFailed to download PDFs for the following files:")
        for failed_file in failed_downloads:
            click.echo(f"  - {failed_file}")
