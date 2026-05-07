import logging

from datetime import datetime
from pathlib import Path
from typing import Any, Literal

logger = logging.getLogger(__name__)

class ReadFromService:

    photo_formats = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".heic",
        ".heif",
        ".bmp",
        ".tiff",
        ".tif",
        ".raw",
        ".arw",  # Sony
        ".cr2",  # Canon
        ".cr3",  # Canon (newer)
        ".dng",  # Adobe / Google Pixel
        ".nef",  # Nikon
        ".nrw",  # Nikon (compact)
        ".orf",  # Olympus
        ".raf",  # Fujifilm
        ".rw2",  # Panasonic
        ".srw",  # Samsung
        ".x3f",  # Sigma
        ".pef",  # Pentax
    }

    video_formats = {
        ".mp4",
        ".m4v",
        ".mov",
        ".avi",
        ".wmv",
        ".flv",
        ".webm",
        ".mkv",
        ".3gp",
        ".3g2",
        ".m2ts",
        ".mts",
        ".mpg",
        ".mpeg",
        ".ogv",
    }

    @staticmethod
    def _get_extension(obj: Path) -> str:
        """
        Function to get an extension of the provided path to the file.

        Parameters
        ----------
        obj : Path
            Path of the file.

        Examples
        --------
        >>> path = Path("/home/users/img.jpg")
        >>> print(ReadFromService._get_extension(path)) # .jpg

        Returns
        -------
        str
            Extension of the path to the file.
        """
        return obj.suffix.lower()

    @staticmethod
    def _get_filename(obj: Path) -> str:
        """
        Function to the a filename of the path to the file.

        Parameters
        ----------
        obj : Path
            Path to the file.

        Examples
        --------
        >>> path = Path("/home/users/img.jpg")
        >>> print(ReadFromService._get_filename(path)) # img

        Returns
        -------
        str
            Filename of the path to the file.
        """
        return obj.name

    @staticmethod
    def _to_int(value: Any) -> int | None:
        """
        Function to turn a str of Any into integer if it's possible

        Parameters
        ----------
        value : Any
            Value that needs to be turned into integer

        Returns
        -------
        int or None
            Either an integer or None
        """
        try:
            return int(value)
        except (TypeError, ValueError, Exception):
            return None

    @staticmethod
    def _get_folder_to_move(destination_path: Path, folder_format: Literal["photos", "videos", "files"], owner_name: str, formatted_date: str) -> Path:
        """
        Function to construct a Path-like object from the provided arguments.

        Parameters
        ----------
        destination_path : Path
            Destination path where the file should be moved into.
        folder_format : Literal["photos", "videos", "files"]
            Folder type for the file that's being moved.
        owner_name  : str
            Name of the owner of the files.
        formatted_date : str
            Formatted date of the file in a format YYYY_MM_DD.

        Returns
        -------
        Path
            Path to the destination folder.
        """
        return destination_path / folder_format / owner_name / f"{folder_format}_from_{formatted_date}_by_{owner_name}"

    @staticmethod
    def _get_field(obj: dict, keys: tuple[str] | list[str] | str, default: Any = None) -> Any | None:
        """
        Function to get data from the obj depending on the keys provided

        Parameters
        ----------
        obj : dict
            Object where the data needs to be extracted from
        keys : tuple[str] or list[str] or str
            Keys to use to extract data
        default : Any, optional
            Default value to return in case a key doesn't exist

        Returns
        -------
        Any or None
            Extracted data or None
        """

        if isinstance(keys, str):
            try:
                return obj.get(keys, default)
            except AttributeError:
                return None

        temp = obj

        for key in keys:
            try:
                temp = temp.get(key)
            except AttributeError:
                return None

        return temp

    def _get_folder_format(self, file_path: Path) -> Literal["photos", "videos", "files"]:

        if self._get_extension(file_path) in self.photo_formats:
            return "photos"
        elif self._get_extension(file_path) in self.video_formats:
            return "videos"

        return "files"

    def _get_formatted_date(self, metadata: dict) -> str | None:
        """
        Function to get a formatted date from the metadata.

        Parameters
        ----------
        metadata : dict
            Metadata for the file that's being moved.

        Returns
        -------
        str or None
            Either a formatter date or None
        """
        timestamp = self._get_field(metadata, ("photoTakenTime", "timestamp"))
        if timestamp is None:
            logger.error(f"Photo taken time was not found. Checking next file...")
            return None

        to_int = self._to_int(timestamp)
        if not to_int:
            return None

        from_time_stamp = datetime.fromtimestamp(to_int)
        return from_time_stamp.strftime("%Y-%m-%d").replace("-", "_")