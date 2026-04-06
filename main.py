import os
import time
from typing import Optional
import exiftool
import logging
import sys
from pathlib import Path
from google_photos_sorter import GooglePhotosSorter

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """
    Function to set up logging.
    """

    error_handler = logging.FileHandler("errors.log", mode="w")
    error_handler.setLevel(logging.ERROR)

    warning_handler = logging.FileHandler("logs.log", mode="w")
    warning_handler.setLevel(logging.WARNING)

    info_handler = logging.FileHandler("logs.log", mode="w")
    info_handler.setLevel(logging.INFO)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8",
        handlers=[
            error_handler,
            warning_handler,
            info_handler,
            logging.StreamHandler(stream=open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False))
        ]
    )


def check_exiftool_existence() -> bool:
    """
    Function to check ExifTool existence in the system

    Returns
    -------
    bool
        True if exists otherwise False
    """
    try:
        with exiftool.ExifToolHelper() as et:
            logger.info(f"ExifTool version: {et.version}")
            logger.info("Installation check successful.")
            return True
    except Exception as e:
        logger.info(f"Installation check failed: {e}")
        logger.info("Ensure 'exiftool' (the command-line tool) is installed and in your PATH.")
        return False


def process_folder(input_path: Path, destination_folder: Path, owner: str, additional_file_move: bool = False) -> None:
    """
    Extracted function to process folders

    Parameters
    ----------
    input_path : Path
        Path where Google Photos are located
    destination_folder : Path
        Destination folder where the photos will be moved to
    owner : str
        Owner of the files [matters not]
    additional_file_move : bool
        Whether all files should be moved into a separate directory, purely for convenience
    """

    old_time = time.time()

    for subdir, dirs, files in os.walk(input_path):
        logger.info(f"Processing folder -> {subdir}")
        logger.info(f"Starting to transport files...")

        google_photos_sorter = GooglePhotosSorter(
            origin_folder=Path(subdir),
            destination_folder=destination_folder,
            owner=owner,
            files=files,
            additional_file_move=additional_file_move
        )
        google_photos_sorter.file_mover()
        logger.info(f"Finished working with {subdir}")

    time_difference = time.time() - old_time
    logger.info("Program finished transporting all of the files.")
    logger.info(f"Program finished its job in {time_difference:.2f}s")


def get_input_path() -> Optional[Path]:
    """
    Function to process inputted path from the user

    Returns
    -------
    Optional[Path]
        Path or None
    """

    input_path = Path(input("Enter the path of your Google Photos: ").replace("\\", "/"))
    if not input_path.exists():
        logger.error("The path you provided doesn't exist.")
        return None
    return input_path


def main():
    setup_logging()

    if not check_exiftool_existence():
        return

    input_path = get_input_path()
    if not input_path:
        return

    destination_folder = Path.cwd()
    owner = "user"
    additional_file_move = False

    logger.info(f"Starting to process files in folder -> {input_path}")
    try:
        process_folder(input_path, destination_folder, owner, additional_file_move)
    except Exception:
        logger.exception(f"Something went wrong while processing {input_path}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Program was interrupted.")
