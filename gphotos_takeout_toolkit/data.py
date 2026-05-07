from dataclasses import dataclass

@dataclass
class CommonFields:
    """
    Dataclass to hold common fields of the metadata
    """

    photo_taken_time: int | None = None
    modification_time: int | None = None
    description: str | None = None
    device_type: str | None = None
    starred: int | None = None
    geo_data: dict | None = None
    get_data_exif: dict | None = None
