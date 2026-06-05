import logging

from etl.extract.extract import extract_main


def setup_logging() -> None:
    """
    Configure application logging for the ingestion script.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


if __name__ == "__main__":
    setup_logging()
    extract_main()