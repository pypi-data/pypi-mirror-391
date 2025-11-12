from app.internal.config import settings
from app.utils.constants.settings import App
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString

asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))
for container_name in App.AzureStorageAccount.Containers:
    status=asabm.container_delete(container_name)
    if status is True:
        print("Contenedor {} borrado...".format(container_name))
    else:
        print(f"Error: {status}")

