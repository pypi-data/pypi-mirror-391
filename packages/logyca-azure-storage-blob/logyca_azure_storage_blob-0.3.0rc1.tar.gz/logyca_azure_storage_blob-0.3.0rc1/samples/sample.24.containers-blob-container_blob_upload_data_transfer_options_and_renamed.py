from app.internal.config import settings
from app.utils.constants.settings import App
from jaanca_chronometer import Chronometer
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString
import os

asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))
print("\n.")
chronometer=Chronometer()
folder_local_full_path=os.path.abspath(os.path.join(os.path.dirname(__file__),'files'))

# Example 1 - Small file
# Container root path
file='upload.txt'
chronometer.start()
status=asabm.container_blob_upload_data_transfer_options(folder_local_full_path,file,App.AzureStorageAccount.Containers.NAME_WITH_DATA,max_concurrency=2,verify_file_integrity=True)
chronometer.stop()
print("Container:[{}]".format(App.AzureStorageAccount.Containers.NAME_WITH_DATA))
if status is True:
    print("blob:[{}] uploaded...".format(os.path.join(folder_local_full_path,file)))
    print(f"Elapsed time: {chronometer.get_elapsed_time()}")
else:
    print(status)

# Example 2 - Small file
# Container and subfolders path
container_folders=["folder1","folder2"]
file='upload.txt'
chronometer.start()
status=asabm.container_blob_upload_data_transfer_options(folder_local_full_path,file,App.AzureStorageAccount.Containers.NAME_WITH_DATA,container_folders,max_concurrency=2,verify_file_integrity=True)
chronometer.stop()
print("Container:[{}]".format(App.AzureStorageAccount.Containers.NAME_WITH_DATA))
if status is True:
    print("blob:[{}] uploaded...".format(os.path.join(folder_local_full_path,file)))
    print(f"Elapsed time: {chronometer.get_elapsed_time()}")
else:
    print(status)

# Example 3 - Small file
# Container root path
# Assigning properties
container_folders=[]
file='upload.txt'
file_new_name='upload_renamed_with_properties.txt'
metadata = {
    "origen": "script",
    "usuario": "admin"
}
content_settings = {
    "cache_control": "max-age=3600, public",
    "content_type": "application/pdf",
    "content_encoding": "utf-8",
    "content_language": "es-CO",
    "content_disposition": "inline; filename=\"reporte.pdf\""
}

upload_kwargs = {
    "timeout": 60,            # Please wait up to 60 seconds for the operation to complete.
    "validate_content": True, # valid HTTP response
    "tags": {                 # Blob index tags
        "owner": "dev-team",
        "classification": "confidential"
    }
}

chronometer.start()
status=asabm.container_blob_upload_data_transfer_options(
        folder_local_full_path,
        file,
        App.AzureStorageAccount.Containers.NAME_WITH_DATA,
        container_folders,
        max_concurrency=2,
        verify_file_integrity=True,
        file_new_name=file_new_name,
        metadata=metadata,
        content_settings=content_settings,
        **upload_kwargs
    )
chronometer.stop()
print("Container:[{}]".format(App.AzureStorageAccount.Containers.NAME_WITH_DATA))
if status is True:
    print("blob:[{}] uploaded...".format(os.path.join(folder_local_full_path,file_new_name)))
    print(f"Elapsed time: {chronometer.get_elapsed_time()}")
else:
    print(status)
