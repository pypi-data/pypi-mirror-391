from app.internal.config import settings
from app.utils.constants.settings import App
from azure.storage.blob import BlobProperties
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString
import json

asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))
print("\n.")

# Example
# Container root path
blob_file='upload_renamed_with_properties.txt'
metadata = {
    "origen2": "script2",
    "usuario2": "admin2"
}
content_settings = {
    "cache_control": "max-age=3600",
    "content_type": "application/txt",
    "content_encoding": "latin",
    "content_language": "es-MX",
    "content_disposition": "inline; filename=\"reporte.txt\""
}

properties_kwargs = {
    "timeout": 60,            # Please wait up to 60 seconds for the operation to complete.
    "tags": {                 # Blob index tags
        "owner2": "dev-team2",
        "classification2": "confidential2"
    }
}
status_or_msg_error=asabm.container_blob_set_properties(
        blob_file,
        App.AzureStorageAccount.Containers.NAME_WITH_DATA,
        metadata=metadata,
        content_settings=content_settings,
        force_unlock=True,
        **properties_kwargs
    )

if status_or_msg_error is True:
    blob_properties:BlobProperties=asabm.container_blob_get_properties(blob_file,App.AzureStorageAccount.Containers.NAME_WITH_DATA,stringify=True)
    print("----------------------")
    print("Set OK")
    if isinstance(blob_properties,BlobProperties):
        print("----------------------")
        print("Showing new data")
        print(json.dumps(blob_properties.__dict__,indent=4,default=str))
    else:
        print(blob_properties)
else:
    print(f"Error: {status_or_msg_error}")
