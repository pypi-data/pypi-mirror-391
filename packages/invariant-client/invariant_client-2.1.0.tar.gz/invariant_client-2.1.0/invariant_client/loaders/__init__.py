import yaml
from abc import ABC, abstractmethod
from urllib.parse import urlparse, parse_qs
import boto3
import os
import json


class Loader(ABC):
    @abstractmethod
    def load(self, uri: str) -> dict:
        """Load and return parsed YAML/JSON content from the given URI."""
        pass

class EnvLoader(Loader):
    def load(self, uri: str) -> dict:
        """
        Load environment variables from a URI like:
        env://VAR_NAME
        env://VAR_NAME?default=default_value
        """
        parsed = urlparse(uri)
        var_name = parsed.netloc
        query = parse_qs(parsed.query)
        default_value = query.get("default", [None])[0]

        value = os.getenv(var_name, default_value)
        if value is None:
            raise ValueError(f"Environment variable '{var_name}' not found and no default provided")

        return yaml.safe_load(value)

class FileLoader(Loader):
    def load(self, uri: str) -> dict:
        path = uri[len("file://") :] if uri.startswith("file://") else uri
        with open(path, "r") as f:
            return yaml.safe_load(f)


class S3Loader(Loader):
    def load(self, uri: str) -> dict:
        parsed = urlparse(uri)
        bucket = parsed.netloc
        key = parsed.path.lstrip("/")
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=bucket, Key=key)
        content = obj["Body"].read().decode()
        return yaml.safe_load(content)


class AWSSecretLoader(Loader):
    def load(self, uri: str) -> dict:
        """
        Supports URI like:
        secret+aws://my-secret-name
        secret+aws://my-secret-name?region=us-east-1&version_id=...&version_stage=...&key=myfield
        """
        parsed = urlparse(uri)
        secret_id = parsed.netloc + parsed.path  # combine in case path present
        # secret_id = secret_id.lstrip("/")
        query = parse_qs(parsed.query)
        print(f"query: {query}")

        region = query.get("region", [None])[0]
        version_id = query.get("version_id", [None])[0]
        version_stage = query.get("version_stage", [None])[0]
        key = query.get("key", [None])[0]

        # Create client with region if specified, else default
        if region:
            client = boto3.client("secretsmanager", region_name=region)
        else:
            client = boto3.client("secretsmanager")

        # Build get_secret_value params
        params = {"SecretId": secret_id}
        if version_id:
            params["VersionId"] = version_id
        if version_stage:
            params["VersionStage"] = version_stage
        print(f"params: {params}")
        response = client.get_secret_value(**params)

        secret_string = response.get("SecretString")
        if secret_string is None:
            raise ValueError(f"Secret {secret_id} does not have a SecretString")

        # Parse secret string as JSON or YAML
        try:
            secret_data = json.loads(secret_string)
        except json.JSONDecodeError:
            # Fallback to YAML parsing
            secret_data = yaml.safe_load(secret_string)

        if key:
            # Extract nested key
            for part in key.split("."):
                secret_data = secret_data.get(part)
                if secret_data is None:
                    raise KeyError(f"Key '{key}' not found in secret '{secret_id}'")
            return secret_data

        return secret_data


# Registry mapping scheme -> Loader instance
LOADERS = {
    "file": FileLoader(),
    "s3": S3Loader(),
    "secret+aws": AWSSecretLoader(),
    "env": EnvLoader(),
}

def load(uri: str) -> dict:
    # Defaults to returning string if no scheme is provided
    if "://" not in uri:
        return uri
    scheme = uri.split("://")[0]
    loader = LOADERS.get(scheme)
    if loader is None:
        raise ValueError(f"No loader registered for scheme '{scheme}'")
    return loader.load(uri)
