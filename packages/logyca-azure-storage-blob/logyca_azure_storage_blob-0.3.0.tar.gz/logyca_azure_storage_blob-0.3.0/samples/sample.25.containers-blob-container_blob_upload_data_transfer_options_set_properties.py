from app.internal.config import settings
from app.utils.constants.settings import App
from jaanca_chronometer import Chronometer
from logyca_azure_storage_blob import (
        AzureStorageAccountBlobManagement,
        FileAnalyzer,
        FileProperties,
        SetCredentialsConnectionString,
    )
import os

asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))
print("\n.")
chronometer=Chronometer()
# Assigning properties
file='upload.txt'
folder_local_full_path=os.path.abspath(os.path.join(os.path.dirname(__file__),'files'))
file_local_full_path=os.path.abspath(os.path.join(folder_local_full_path,file))
file_analyzer=FileAnalyzer(file_local_full_path)
file_properties:FileProperties = file_analyzer.get_properties()
if file_properties.error_occurred:
    print(f"Error: {file_properties.error_msg}")
    file_properties = {}
else:
    file_properties = file_properties.timestamps.to_dict()

container_folders=[]
file_new_name='upload_renamed_with_properties.txt'

metadata = {
    "origen": "script",
    "usuario": "admin"
}

file_properties = {f"source_file_{key}":value for key,value in file_properties.items()}
metadata_merged = {**metadata,**file_properties}
metadata_merged = dict(sorted(metadata_merged.items()))

content_settings = {
    "cache_control": "max-age=3600, public",
    "content_type": "application/pdf",
    "content_encoding": "utf-8",
    "content_language": "es-CO",
    "content_disposition": "inline; filename=\"reporte.pdf\""
}

tags = {                 # Blob index tags
    "owner": "dev-team",
    "classification": "confidential"
}
tags = dict(sorted(tags.items()))
upload_kwargs = {
    "timeout": 60,            # Please wait up to 60 seconds for the operation to complete.
    "validate_content": True, # valid HTTP response
    "tags": tags
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
        metadata=metadata_merged,
        content_settings=content_settings,
        **upload_kwargs
    )
chronometer.stop()
print("Container:[{}]".format(App.AzureStorageAccount.Containers.NAME_WITH_DATA))
if status is True:
    print("blob:[{}] uploaded...".format(os.path.join(folder_local_full_path,file_new_name)))
    print(f"Elapsed time: {chronometer.get_elapsed_time()}")
else:
    print(f"Error = {status}")
