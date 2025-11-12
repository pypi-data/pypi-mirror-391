from app.internal.config import settings
from app.utils.constants.settings import App
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString
import json

asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))

# 1) Delete all by date searching from the root of the container (if preview_only=true it does not delete)
res = asabm.container_blob_delete_by_age(
    container_name=App.AzureStorageAccount.Containers.NAME_WITH_DATA,
    older_than_unit="seconds",
    older_than=1,
    container_folders=[],
    include_subfolders=True,
    preview_only=True
)

print("\n.")

if isinstance(res,dict):
    print(f"details={json.dumps(res,indent=4)}")
else:
    print(f"Error: {res}")

# Output 1: files not deleted
#
# details={
#     "container": "tmp",
#     "folder_start": "/",
#     "include_subfolders": true,
#     "preview_only": true,
#     "total_scanned": 0,
#     "deleted": 0,
#     "affected": []
# }


# Output 2: deleted files
#
# details={
#     "container": "tmp",
#     "folder_start": "/",
#     "include_subfolders": true,
#     "preview_only": true,
#     "total_scanned": 5,
#     "deleted": 0,
#     "affected": [
#         {
#             "name": "app_worker.info.log",
#             "last_modified": "2025-11-10T22:55:00+00:00",
#             "size": 72
#         },
#         {
#             "name": "folder1/folder2/upload.txt",
#             "last_modified": "2025-11-10T23:07:25+00:00",
#             "size": 62
#         },
#         {
#             "name": "folder1/folder2/upload_renamed.txt",
#             "last_modified": "2025-11-10T23:07:26+00:00",
#             "size": 62
#         },
#         {
#             "name": "logs/app_worker.error.log",
#             "last_modified": "2025-11-10T22:55:00+00:00",
#             "size": 72
#         },
#         {
#             "name": "upload.txt",
#             "last_modified": "2025-11-10T23:07:23+00:00",
#             "size": 62
#         }
#     ]
# }