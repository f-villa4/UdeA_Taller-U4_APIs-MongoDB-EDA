import logging
import sys

from etl.extract.extract import extract_main
from etl.load.load import load_main
from etl.transform.transform import transform_main


def setup_logging() -> None:
    """
    Configure logs for the ETL pipeline.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def main() -> None:
    """
    Run ETL commands from the terminal.
    """
    setup_logging()

    if len(sys.argv) < 2:
        print("Usage: python main.py [extract|transform|load|run]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "extract":
        extract_main()
    elif command == "transform":
        transform_main()
    elif command == "load":
        load_main()
    elif command == "run":
        extract_main()
        transform_main()
        load_main()
    else:
        print("Unknown command. Use: extract | transform | load | run")
        sys.exit(1)


if __name__ == "__main__":
    main()