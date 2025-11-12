from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import boto3
from boto3.exceptions import ResourceNotExistsError
from botocore.exceptions import ClientError
import base64, json


def retrieve_secrets(point, azure_vault_url=None, aws_secret_name=None, aws_region=None):
    """ Helper function to connect to Azure/AWS, and retrieve the secrets. """

    if point.lower() == "azure":
        if not azure_vault_url:
            raise ValueError("Provide the required Azure Vault URL !")

        creds = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=azure_vault_url, credential=creds)
        secrets_dict = {}

        # 1. List properties of all secrets (does not include values)
        secret_properties = secret_client.list_properties_of_secrets()

        # 2. Iterate through properties and fetch the value for each secret
        for secret_property in secret_properties:
            # Check if the secret is enabled before retrieving (optional)
            if secret_property.enabled:
                try:
                    # Get the specific secret with its value
                    secret = secret_client.get_secret(secret_property.name)
                    secrets_dict[secret.name] = secret.value
                except Exception as e:
                    raise KeyError(f"Could not retrieve secret '{secret_property.name}': {e}")
        
        return secrets_dict
    
    elif point.lower() == "aws":
        if not aws_secret_name:
            raise ValueError("Provide the required AWS Secret name !")
        if not aws_region:
            raise ValueError("Provide the required region name of the AWS Secret !")
        
        # Create a AWS Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=aws_region
        )

        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=aws_secret_name
            )
            if 'SecretString' in get_secret_value_response:
                return json.loads(get_secret_value_response['SecretString'])
            else:
                return json.loads(base64.b64decode(get_secret_value_response['SecretBinary']))

        except ClientError as error:
            raise error
        except ResourceNotExistsError as error:
            raise error