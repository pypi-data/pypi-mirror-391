from app.internal.config import settings
from app.utils.constants.settings import App
from azure.storage.blob import BlobProperties
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString
import json


asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))
print("\n.")

# Example 1 - Small file
# Container root path
blob_file='upload.txt'
blob_properties:BlobProperties=asabm.container_blob_get_properties(blob_file,App.AzureStorageAccount.Containers.NAME_WITH_DATA,stringify=False)
if isinstance(blob_properties,BlobProperties):
    print("----------------------")
    print(f"name: {blob_properties.name}")
    print(f"size: {blob_properties.size} bytes")
    print(f"content_md5: {blob_properties.content_settings.content_md5}")
    print(f"last_modified: {blob_properties.last_modified}")
    print(f"blob_type: {blob_properties.blob_type}")
else:
    print(blob_properties)

# Example 2 - Small file
# Container and subfolders path
blob_file='upload.txt'
container_folders=["folder1","folder2"]
blob_properties:BlobProperties=asabm.container_blob_get_properties(blob_file,App.AzureStorageAccount.Containers.NAME_WITH_DATA,container_folders,stringify=True)
if isinstance(blob_properties,BlobProperties):
    print("----------------------")
    print(f"name: {blob_properties.name}")
    print(f"size: {blob_properties.size} bytes")
    print(f"content_md5: {blob_properties.content_settings.content_md5}")
    print(f"last_modified: {blob_properties.last_modified}")
    print(f"blob_type: {blob_properties.blob_type}")
else:
    print(blob_properties)


# Example 3 - Small file
# Container root path
# Read all properties
blob_file_new_name='upload_renamed_with_properties.txt'
blob_properties:BlobProperties=asabm.container_blob_get_properties(blob_file_new_name,App.AzureStorageAccount.Containers.NAME_WITH_DATA,stringify=True)
if isinstance(blob_properties,BlobProperties):
    print("----------------------")
    print(json.dumps(blob_properties.__dict__,indent=4,default=str))
else:
    print(blob_properties)


# output 1
#
# name: upload.txt
# size: 62 bytes
# content_md5: 6XRTx/eHmuBUn5e4QqV5jQ==
# last_modified: 2024-05-15 14:47:08+00:00
# blob_type: BlobType.BLOCKBLOB

# output 2
#
# name: folder1/folder2/upload.txt
# size: 62 bytes
# content_md5: bytearray(b'\xe9tS\xc7\xf7\x87\x9a\xe0T\x9f\x97\xb8B\xa5y\x8d')
# last_modified: 2024-05-15 14:46:45+00:00
# blob_type: BlobType.BLOCKBLOB

# output 3
#
# {
#     "name": "upload_renamed_with_properties.txt",
#     "container": "tmp",
#     "snapshot": null,
#     "version_id": null,
#     "is_current_version": null,
#     "blob_type": "BlockBlob",
#     "metadata": {
#         "origen": "script",
#         "usuario": "admin"
#     },
#     "encrypted_metadata": null,
#     "last_modified": "2025-11-11 04:58:37+00:00",
#     "etag": "\"0x8DE20DEF973AA7C\"",
#     "size": 62,
#     "content_range": null,
#     "append_blob_committed_block_count": null,
#     "is_append_blob_sealed": null,
#     "page_blob_sequence_number": null,
#     "server_encrypted": true,
#     "copy": "{'id': None, 'source': None, 'status': None, 'progress': None, 'completion_time': None, 'status_description': None, 'incremental_copy': None, 'destination_snapshot': None}",
#     "content_settings": "{'content_type': 'application/pdf', 'content_encoding': 'utf-8', 'content_language': 'es-CO', 'content_md5': '6XRTx/eHmuBUn5e4QqV5jQ==', 'content_disposition': 'inline; filename=\"reporte.pdf\"', 'cache_control': 'max-age=3600, public'}",
#     "lease": "{'status': 'unlocked', 'state': 'available', 'duration': None}",
#     "blob_tier": "Cool",
#     "rehydrate_priority": null,
#     "blob_tier_change_time": null,
#     "blob_tier_inferred": true,
#     "deleted": false,
#     "deleted_time": null,
#     "remaining_retention_days": null,
#     "creation_time": "2025-11-10 23:54:31+00:00",
#     "archive_status": null,
#     "encryption_key_sha256": null,
#     "encryption_scope": null,
#     "request_server_encrypted": true,
#     "object_replication_source_properties": [],
#     "object_replication_destination_policy": null,
#     "last_accessed_on": null,
#     "tag_count": 2,
#     "tags": {
#         "classification": "confidential",
#         "owner": "dev-team"
#     },
#     "immutability_policy": "{'expiry_time': None, 'policy_mode': None}",
#     "has_legal_hold": null,
#     "has_versions_only": null
# }
