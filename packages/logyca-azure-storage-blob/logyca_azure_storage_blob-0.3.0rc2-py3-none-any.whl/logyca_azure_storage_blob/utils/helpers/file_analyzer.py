from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional, Literal
import os

class FormatDates(StrEnum):
    ISO_DATE                = "%Y-%m-%d"                # 2025-03-25
    ISO_DATETIME            = "%Y-%m-%d %H:%M:%S"       # 2025-03-25 14:30:45
    ISO_DATETIME_WITH_TZ    = "%Y-%m-%dT%H:%M:%S%z"     # 2025-03-25T14:30:45-0500

    SQL_SERVER              = "%Y-%m-%d %H:%M:%S"       # datetime / datetime2 (sin TZ): 2025-03-25 14:30:45
    SQL_SERVER_WITH_TZ      = "%Y-%m-%d %H:%M:%S%z"     # datetimeoffset (con TZ): 2025-03-25 14:30:45-0500

    POSTGRES                = "%Y-%m-%d %H:%M:%S"       # timestamp sin timezone: 2025-03-25 14:30:45
    POSTGRES_WITH_TZ        = "%Y-%m-%d %H:%M:%S%z"     # timestamptz (con timezone): 2025-03-25 14:30:45-0500

@dataclass
class Timestamps:
    creation_date       : Optional[str] = None
    modification_date   : Optional[str] = None
    access_date         : Optional[str] = None
    date_format         : Optional[str] = field(default=FormatDates.POSTGRES_WITH_TZ)

    def to_dict(self)->dict:
        def format_value(value):
            if isinstance(value, datetime):
                return value.strftime(self.date_format)
            return value

        self.creation_date = format_value(self.creation_date)
        self.modification_date = format_value(self.modification_date)
        self.access_date = format_value(self.access_date)

        return self.__dict__

    def format_datetime(self, dt: datetime) -> str:
        """Convierte un datetime en string usando el formato configurado."""
        return dt.strftime(str(self.date_format))

@dataclass
class FileProperties:
    full_path_name  : Optional[str] = None
    name            : Optional[str] = None
    extension       : Optional[str] = None
    size_bytes      : Optional[int] = None
    size_kbytes     : Optional[float] = None
    size_mbytes     : Optional[float] = None
    size_gbytes     : Optional[float] = None
    timestamps      : Timestamps = field(default_factory=Timestamps)
    error_occurred  : Optional[bool] = False
    error_msg       : Optional[str] = None

class FileAnalyzerErrorCode(StrEnum):
    FILE_NOT_FOUND = "File Not Found: {}"
    UNSUPPORTED_OUTPUT_FORMAT = "Unsupported output format. Please select one from the list: {}"

class FileAnalyzer:
    def __init__(self,full_path_name:str) -> None:
        """
        Analyzes and retrieves metadata and filesystem properties of a given file.

        This class extracts details such as:
        - File name and extension
        - Size (bytes, KB, MB, GB)
        - Creation, modification, and last access timestamps
        - Error handling information

        Upon initialization, all properties are automatically evaluated and stored
        inside a `FileProperties` instance. The results can then be returned either
        as a structured object or as a JSON-friendly dictionary.

        Parameters
        ----------
        full_path_name : str
            The absolute or relative path of the file to be analyzed.

        Attributes
        ----------
        _file_properties : FileProperties
            Holds all extracted metadata and timestamps.
            If an error occurs (file not found, unsupported format, etc.),
            `error_occurred` will be set to True and `error_msg` will describe the issue.

        Methods
        -------
        get_properties(output_format='file_properties')
            Returns the file properties in either dictionary (`json`) format
            or as a `FileProperties` data class instance.
        """
        self._file_properties = FileProperties(full_path_name=full_path_name)

        if(os.path.exists(full_path_name)):
            try:
                self._file_properties.error_msg ="_get_name_properties: {}"     ; self._get_name_properties()
                self._file_properties.error_msg ="_get_modification_date: {}"   ; self._get_modification_date()
                self._file_properties.error_msg ="_get_creation_date: {}"       ; self._get_creation_date()
                self._file_properties.error_msg ="_get_access_date: {}"         ; self._get_access_date()
                self._file_properties.error_msg ="_get_size: {}"                ; self._get_size()
                self._file_properties.error_occurred = False
                self._file_properties.error_msg =""
            except Exception as e:
                self._file_properties.error_occurred = True
                self._file_properties.error_msg = self._file_properties.error_msg.format(str(e))
        else:
            self._file_properties.error_occurred = True
            self._file_properties.error_msg = FileAnalyzerErrorCode.FILE_NOT_FOUND.format(full_path_name)

    def _add_local_timezone(self, ts: float) -> datetime:
        return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone()

    def _convert_datetime_to_string(self, dt: datetime) -> str:
        return dt.strftime(str(self._file_properties.timestamps.date_format))

    def _get_name_properties(self)->str:
        self._file_properties.name = os.path.basename(self._file_properties.full_path_name)
        item_list=self._file_properties.name.split(".")        
        self._file_properties.extension = item_list[len(item_list)-1]

    def _get_modification_date(self)->str:
        modification_time = os.path.getmtime(self._file_properties.full_path_name)
        modification_time = self._add_local_timezone(modification_time)
        self._file_properties.timestamps.modification_date = self._convert_datetime_to_string(modification_time)

    def _get_creation_date(self)->str:
        creation_time = os.path.getctime(self._file_properties.full_path_name)
        creation_time = self._add_local_timezone(creation_time)
        self._file_properties.timestamps.creation_date = self._convert_datetime_to_string(creation_time)

    def _get_access_date(self)->str:
        access_time = os.path.getatime(self._file_properties.full_path_name)
        access_time = self._add_local_timezone(access_time)
        self._file_properties.timestamps.access_date = self._convert_datetime_to_string(access_time)

    def _get_size(self,round_digits:int = 2):
        KB = 1024
        MB = KB * 1024
        GB = MB * 1024
        size_bytes = os.path.getsize(self._file_properties.full_path_name)
        self._file_properties.size_bytes = size_bytes
        self._file_properties.size_kbytes = float(round(size_bytes / KB,round_digits))
        self._file_properties.size_mbytes = float(round(size_bytes / MB,round_digits))
        self._file_properties.size_gbytes = float(round(size_bytes / GB,round_digits))
        
    def get_properties(self,output_format:Literal["json","file_properties"] = "file_properties")->dict|FileProperties:
        """
        Returns the analyzed file properties.

        Parameters
        ----------
        output_format : Literal["json", "file_properties"], optional
            Determines the output format:
            - "json": returns a dictionary (`dict`) containing the file properties,
            including timestamp values already formatted as strings.
            - "file_properties": returns a `FileProperties` object containing
            the structured properties.

        Returns
        -------
        dict | FileProperties
            Depending on the `output_format` parameter, returns either:
            - A `dict` with sorted keys and timestamp values converted to strings, or
            - A `FileProperties` object with all file information.

        Notes
        -----
        In case of an error (e.g., file not found or unsupported output format),
        the attribute `error_occurred` inside `FileProperties` will be set to True,
        and `error_msg` will contain a descriptive message.

        Example
        -------
        ```python
        from file_analyzer import FileAnalyzer, FileProperties
        import json, os

        file_name="hello asa s sas. as as a. as as .txt"
        file_name_full_path_from_actual_folder=os.path.abspath(os.path.join(os.path.dirname(__file__),file_name))
        file_analyzer=FileAnalyzer(file_name_full_path_from_actual_folder)

        file_properties:FileProperties = file_analyzer.get_properties()
        if file_properties.error_occurred:
            print(f"Error: {file_properties.error_msg}")
        else:
            print(f"==================================")
            print("output_format=file_properties")
            print(f"name:{file_properties.name}")
            print(f"extension:{file_properties.extension}")
            print(f"modification_date:{file_properties.timestamps.date_format}")
            print(f"modification_date:{file_properties.size_bytes}")
            print(f"modification_date:{file_properties.size_kbytes}")
            print(f"modification_date:{file_properties.timestamps.modification_date}")
            print(f"==================================")
            print("output_format=json")
            file_properties = file_analyzer.get_properties("json")
            print((json.dumps(file_properties,indent=4, ensure_ascii=False)))

        ```
        """
        output_list = ["json","file_properties"]
        if output_format not in output_list:
            self._file_properties.error_occurred = True
            self._file_properties.error_msg = FileAnalyzerErrorCode.UNSUPPORTED_OUTPUT_FORMAT.format(output_list)
            return self._file_properties
        match output_format:
            case "json":
                self._file_properties.timestamps = self._file_properties.timestamps.to_dict()
                return dict(sorted(asdict(self._file_properties).items()))
            case "file_properties":
                return self._file_properties
            case _:
                return self._file_properties
