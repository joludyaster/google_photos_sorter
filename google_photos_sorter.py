import os
import shutil
import json
import time
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class GooglePhotosSorter:
    def __init__(
        self, 
        origin_folder: Path, 
        destination_folder: Path, 
        owner: str, 
        files: list[str], 
        additional_file_move: bool = False
    ):
        """
        Initialize class variables

        Parameters
        ----------
        origin_folder : Path
            Folder from where the files will be moved
        destination_folder : Path
            Folder to where the files will be moved
        owner : str
            Owner of the files [doesn't really matter]
        files : list[str]
            List of files to sort
        additional_file_move : bool, optional
            Whether all the files should be moved into one folder without sorting, by default False
        """

        self.origin_folder = origin_folder
        self.files = files
        self.destination_folder = destination_folder
        self.owner = owner
        self.additional_file_move = additional_file_move

        self.photo_formats = [
            "jpeg", 
            "jpg", 
            "gif", 
            "tiff", 
            "raw", 
            "png"
        ]
        self.video_formats = [
            "mp4", 
            "mov", 
            "avi", 
            "wmv", 
            "avchd", 
            "webm", 
            "flv", 
            "mkv", 
            "mpeg-4"
        ]

        self.photo_folder_format = "photos"
        self.video_folder_format = "videos"
        self.file_folder_format = "files"
        
    def file_mover(self) -> None:
        """
        Orchestrates file move
        """

        try:
            if not self.origin_folder.exists():
                logger.error(f"The path {self.origin_folder} is not valid.")
                return
            
            for file in self.files:
                if file.split(".")[-1] == "json":
                    logger.info(f"Skipping {self.origin_folder}/{file}...")
                    continue
                
                get_metadata = self._get_json_google_photo_data(folder=self.origin_folder, file=file)

                if not get_metadata:
                    logger.error(f"JSON data was not found for the file -> {self.origin_folder}/{file}")
                    continue
                
                if not type(get_metadata) is dict:
                    logger.error("Format of the metadata is not dictionary, skipping...")
                    continue
                
                get_photo_taken_time = get_metadata.get("photoTakenTime", None)
                
                if get_photo_taken_time is None:
                    logger.error(f"Photo taken time was not found. Checking next file...")
                    continue
                
                get_timestamp = int(get_photo_taken_time.get('timestamp', None))
                if get_timestamp is None:
                    logger.error(f"Photo taken time was not found. Checking next file...")
                    continue
                
                get_taken_data = datetime.fromtimestamp(timestamp=get_timestamp)
                format_date = get_taken_data.strftime("%Y-%m-%d").replace("-", "_")

                format_selector = self._get_folder_format(extension=file.rsplit(".", 1))

                folder = self.destination_folder / format_selector / self.owner /  f"{format_selector}_from_{format_date}_by_{self.owner}"

                logger.info(f"Trying to transport {self.origin_folder}/{file}...")

                self._move_file(
                    folder=Path(folder),
                    file=file
                )
                
            logger.info(f"Finished transporting files in folder: {self.origin_folder}")

        except Exception:
            logger.exception("Something went wrong while processing information in transport_file() function.")
            return
        
    @staticmethod
    def _get_json_file_path(
        folder: Path, 
        file: str
    ) -> Optional[str]:        
        """
        This function searches for the JSON metadata
        file based on the name of the provided file

        Parameters
        ----------
        folder : Path
            Folder to search
        file : str
            Name of the file

        Returns
        -------
        Optional[str]
            JSON metadata or None
        """
        supplemental_metadata = "supplemental-metadata"
        split_file = file.rsplit(".", 1)
        path_to_file = f"{folder}/{file}"
        
        path_to_json_extension_file = f"{folder}/{split_file[0]}.json"
        if Path(path_to_json_extension_file).exists():
            return path_to_json_extension_file
        
        path_to_file_with_json_extension = f"{path_to_file}.json"
        if Path(path_to_file_with_json_extension).exists():
            return path_to_file_with_json_extension
        
        for index in range(len(supplemental_metadata), -1, -1):
            possible_json_path = f"{path_to_file}.{supplemental_metadata[:index]}.json"
            if Path(possible_json_path).exists():
                return possible_json_path
        
        return None
    
    def _get_folder_format(
        self, 
        extension: str
    ) -> str:
        """
        Function to get a folder format based on the extension

        Parameters
        ----------
        extension : str
            Extension [jpg, jpeg, mp4 etc.]

        Returns
        -------
        str
            Folder format [videos, photos or files]
        """
        if extension[-1].lower() in self.photo_formats:
            return self.photo_folder_format
        elif extension[-1].lower() in self.video_formats:
            return self.video_folder_format

        return self.file_folder_format

    def _get_json_google_photo_data(
        self, 
        folder: Path, 
        file: str
    ) -> Optional[dict]:
        """
        Function to get JSON metadata and return it as dictionary.

        Parameters
        ----------
        folder : Path
            Folder to search
        file : str
            Name of the file that has a metadata

        Returns
        -------
        Optional[dict]
            JSON metadata or None
        """

        try:
            existing_path = self._get_json_file_path(folder=folder, file=file)
                
            if not existing_path:
                return None
            
            with open(existing_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return data
        except Exception:
            logger.exception(f"Something went wrong when trying to get JSON data for the file -> {folder}/{file}")
            return None

    def _move_file(self, folder: Path, file: str) -> None:
        """
        Function to move the file

        Parameters
        ----------
        folder : Path
            Folder in which the file will be located
        file : str
            File to move
        """

        try:
            folder.mkdir(parents=True, exist_ok=True)
            file_path = folder / file
            
            if file_path.exists():
                logger.warning(f"The path {folder}/{file} already exists, skipping...")
                return
                
            if self.additional_file_move:
                Path(self.destination_folder / "all-files").mkdir(parents=True, exist_ok=True)
                shutil.copy(
                    src=f"{self.origin_folder}/{file}",
                    dst=Path(self.destination_folder) / "all-files"
                )
            
            shutil.copy(
                src=f"{self.origin_folder}/{file}",
                dst=folder
            )
        except Exception:
            logger.exception(f"Something went wrong while transporting {file} to -> {folder}")
            return

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
        handlers=[
            error_handler,
            warning_handler,
            info_handler,
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    setup_logging()

    destination_folder = Path.cwd()

    owner = "user"
    
    # Set this if you would like to additionally move all of 
    # your files in one folder without sorting (adds extra space)
    additional_file_move = False

    input_path = str(input("Enter the path of your Google Photos: ")).replace("\\", "/")

    try:
        logger.info(f"Starting to process files in folder -> {input_path}")
        if Path(input_path).exists():

            old_time = time.time()

            for subdir, dirs, files in os.walk(input_path):
                logger.info(f"Processing folder -> {subdir}")
                logger.info(f"Starting to transport files...")
                

                thread = GooglePhotosSorter(
                    origin_folder=Path(subdir),
                    destination_folder=Path(destination_folder),
                    owner=owner,
                    files=files,
                    additional_file_move=additional_file_move
                )
                thread.file_mover()
                logger.info(f"Finished working with {subdir}")

            time_difference = time.time() - old_time

            text = f"""
Program finished transporting all of the files.

Program finished it's job in {time_difference}"""

            logger.info(text)
            return

        logger.error(f"The path you provided doesn't exist.")
        return

    except Exception:
        logger.exception(f"Something went wrong while processing {input_path}")
        return


if __name__ == "__main__":
    main()
