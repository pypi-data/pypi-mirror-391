from app.internal.config import settings
from app.utils.constants.settings import App
from azure.storage.blob import BlobProperties, BlobType
import json
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString

asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))
print("\n.")
#################
# root folder
# blob_list=asabm.container_blob_list(App.AzureStorageAccount.Containers.NAME_WITH_DATA,include_subfolders=False)
#################
# subfolders
# container_folders=["logs","logs1"]
# blob_list=asabm.container_blob_list(App.AzureStorageAccount.Containers.NAME_WITH_DATA,container_folders=container_folders)
#################
# modified_hours_ago
container=App.AzureStorageAccount.Containers.NAME_WITH_DATA
container_folders=["folder1"]
blob_list=asabm.container_blob_list(container,container_folders=container_folders,include_subfolders=True,modified_minutes_ago=2)
print("\n.")
for blob_properties in blob_list:
    blob_properties:BlobProperties = asabm.parse_blob_properties_stringify(blob_properties)
    print("----------------------")
    print(f"name: {blob_properties.name}")
    print(f"size: {blob_properties.size} bytes")
    print(f"content_md5: {blob_properties.content_settings.content_md5}")
    print(f"last_modified: {blob_properties.last_modified}")
    print(f"blob_type: {blob_properties.blob_type}")
    # print(json.dumps(blob_properties.__dict__,indent=4,default=str))

# Output
#
# ----------------------
# name: folder1/folder2/upload.txt        
# size: 62 bytes
# content_md5: 6XRTx/eHmuBUn5e4QqV5jQ==   
# last_modified: 2025-11-10 22:35:54+00:00
# blob_type: BlobType.BLOCKBLOB
# ----------------------
# name: folder1/folder2/upload_renamed.txt
# size: 62 bytes
# content_md5: 6XRTx/eHmuBUn5e4QqV5jQ==   
# last_modified: 2025-11-10 22:35:55+00:00
# blob_type: BlobType.BLOCKBLOB


