import logging
import json
import os
import shutil

from pathlib import Path
from gphotos_takeout_toolkit.metadata import Metadata
from . import ReadFromService

logger = logging.getLogger(__name__)


class ReadFromFolder(ReadFromService):

    def __init__(
            self,
            source_path: Path,
            destination_path: Path,
            owner_name: str = "user",
            additional_file_move: bool = False
    ):
        """
        Initialize class variables.

        Parameters
        ----------
        source_path : Path
            Path to the folder from which files should be moved.
        destination_path : Path
            Destination path to where the files should be moved into.
        owner_name : str, default "user"
            Owner of the files, defaults to "user".
        additional_file_move : bool, default False
            Whether files should additionally be moved to a separate folder all together.
        """

        self.source_path = source_path
        self.destination_path = destination_path
        self.owner = owner_name
        self.additional_file_move = additional_file_move

        # Counters to keep track of failed and successful file moves
        self.successful_counter = 0
        self.failed_counter = 0


    @staticmethod
    def _handle_metadata(file_path: Path, metadata: dict) -> bool:
        """
        Function to call a Metadata() class to restore the metadata for the file.

        Parameters
        ----------
        file_path : Path
            Path to the file.
        metadata : dict
            Metadata of the file.

        Returns
        -------
        bool
            True if metadata was restored successfully, False otherwise
        """
        metadata_restorer = Metadata(
            file_path=file_path,
            metadata=metadata
        )
        result = metadata_restorer.restore()
        return result

    def _get_destination_path(self, file_path: Path, metadata: dict = None) -> Path | None:
        """
        Function to get a destination path based on the metadata.
        If metadata isn't provided, that means the file is a failed one.

        Parameters
        ----------
        file_path : Path
            Path to the file that's being moved.
        metadata : dict or None
            Metadata of the file that's being moved.

        Returns
        -------
        Path or None
            Either a path or None
        """

        if not metadata:
            return self.destination_path / "failed-files"

        folder_format = self._get_folder_format(file_path)
        formatted_date = self._get_formatted_date(metadata)
        if not formatted_date:
            logger.error("Formatted date wasn't configured properly. Doing nothing...")
            return None

        folder_to_move = self._get_folder_to_move(
            self.destination_path,
            folder_format,
            self.owner,
            formatted_date
        )
        return folder_to_move

    def _move(self, file_path: Path, metadata: dict = None) -> None:
        """
        Function to move the file to a destination path.

        Parameters
        ----------
        file_path : Path
            Path of the file that's being moved.
        metadata : dict or None
            Metadata of the file that's being moved
        """

        destination_path = self._get_destination_path(file_path, metadata)
        if not destination_path:
            logger.error(f"Couldn't get a destination path, failed to move {file_path}")
            return

        destination_path.mkdir(parents=True, exist_ok=True)
        destination_file_path = destination_path / file_path.name

        if destination_file_path.exists():
            logger.warning(f"The path {destination_file_path} already exists, skipping...")
            return

        try:
            shutil.copy2(file_path, destination_path)
            if self.additional_file_move:
                additional_path = Path(destination_path / "all-files")
                additional_path.mkdir(parents=True, exist_ok=True)

                additional_file_path = additional_path / file_path.name

                if additional_file_path.exists():
                    logger.warning(f"The path {additional_file_path} already exists, skipping...")
                    return

                shutil.copy2(file_path, additional_path)

            if metadata:
                self._handle_metadata(destination_file_path, metadata)

            logger.info(f"Successfully moved {file_path} to {destination_path}")
            return
        except (shutil.Error, Exception):
            logger.exception(f"Couldn't move the file {file_path}")
            return

    def process(self) -> None:
        """
        Function to iterate through files in a directory, find corresponding JSON metadata and move the file.
        Optimized version - same logic, just faster.
        """

        members_by_filename: dict[str, Path] = {}
        json_members: list[Path] = []

        for root, _, filenames in os.walk(self.source_path):
            root_path = Path(root)
            for filename in filenames:
                file_path = root_path / filename
                if file_path.is_dir():
                    continue

                ext = self._get_extension(file_path)
                if ext == ".json":
                    json_members.append(file_path)
                else:
                    key = self._get_filename(file_path)
                    # Only add if not exists (keeps first occurrence like original)
                    if key not in members_by_filename:
                        members_by_filename[key] = file_path

        matched_filenames = set()

        for member in json_members:
            try:
                with open(member, "r", encoding="utf-8") as file:
                    data = json.load(file)

                title = data.get("title", "")
                if not title:
                    continue

                path_member = members_by_filename.get(title)
                if path_member:
                    logger.info(f"Trying to move {path_member}")
                    matched_filenames.add(title)

                    self._move(path_member, data)
                    self.successful_counter += 1
            except Exception as e:
                logger.error(f"Failed to process metadata {member.name}: {e}")

        # Second pass - move unmatched media files
        for filename, member in members_by_filename.items():
            if filename not in matched_filenames:
                self.failed_counter += 1
                self._move(member)
