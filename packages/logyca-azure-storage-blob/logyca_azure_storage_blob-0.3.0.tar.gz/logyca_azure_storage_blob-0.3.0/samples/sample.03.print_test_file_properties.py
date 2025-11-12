from logyca_azure_storage_blob import FileAnalyzer, FileProperties, FormatDates
import json, os

file='upload.txt'
file_local_full_path=os.path.abspath(os.path.join(os.path.dirname(__file__),'files',file))
file_analyzer=FileAnalyzer(
        full_path_name=file_local_full_path,
        date_format=FormatDates.POSTGRES_WITH_TZ
    )
print("\n.")

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

# Output
#
# ==================================
# output_format=file_properties
# name:upload.txt
# extension:txt
# modification_date:%Y-%m-%d %H:%M:%S%z
# modification_date:62
# modification_date:0.06
# modification_date:2020-02-01 19:00:00-0500
# ==================================
# output_format=json
# {
#     "error_msg": "_get_size: {}",
#     "error_occurred": false,
#     "extension": "txt",
#     "full_path_name": "C:\\Users\\Andres\\OneDrive - GRUPO LOGYCA\\tmp\\blob-pypi.org\\samples\\files\\upload.txt",
#     "name": "upload.txt",
#     "size_bytes": 62,
#     "size_gbytes": 0.0,
#     "size_kbytes": 0.06,
#     "size_mbytes": 0.0,
#     "timestamps": {
#         "creation_date": "2025-11-10 15:15:45-0500",
#         "modification_date": "2020-02-01 19:00:00-0500",
#         "access_date": "2025-11-11 10:17:48-0500",
#         "date_format": "%Y-%m-%d %H:%M:%S%z"
#     }
# }
