from pydantic import (
    BaseModel,
    FilePath,
    ValidationError,
    Field,
    model_validator,
    FieldValidationInfo,
    field_validator,
    AfterValidator,
    SecretStr,
)
from typing import Literal, Optional, List, Union, Any
from enum import Enum
import yaml
from pathlib import Path
from typing import Annotated
from invariant_client.loaders import load


class SourceKind(str, Enum):
    LIBRENMS = "librenms"
    AWS = "aws"


class BaseSourceConfig(BaseModel):
    name: str
    kind: SourceKind  # Pydantic handles SourceKind enum correctly for discrimination


class LibreNMSConfig(BaseSourceConfig):
    # Using the enum member for Literal is fine for str enums
    kind: Literal[SourceKind.LIBRENMS]
    hostname: str
    device_group: str
    api_key: SecretStr
    ssh_key: Optional[SecretStr] = None
    ssh_key_path: Optional[FilePath] = None
    ssh_user: Optional[str] = None

    @model_validator(mode="after")
    def _check_ssh_key_or_path_exclusive(self) -> "LibreNMSConfig":
        ssh_key_present = self.ssh_key is not None
        ssh_key_path_present = self.ssh_key_path is not None

        if ssh_key_present and ssh_key_path_present:
            raise ValueError(
                f"Error in source {self.name}: Fields 'ssh_key' and 'ssh_key_path' are mutually exclusive. Provide only one."
            )
        if not ssh_key_present and not ssh_key_path_present:
            raise ValueError(
                f"Error in source {self.name}: Exactly one of 'ssh_key' or 'ssh_key_path' is required."
            )
        return self

    @model_validator(mode="after")
    def _resolve_secrets_in_model(self) -> "LibreNMSConfig":
        if self.api_key:
            if "://" in self.api_key.get_secret_value():
                self.api_key = SecretStr(load(self.api_key.get_secret_value()))
        if self.ssh_key:
            if "://" in self.ssh_key.get_secret_value():
                self.ssh_key = SecretStr(load(self.ssh_key.get_secret_value()))
        return self


class AWSConfig(BaseSourceConfig):
    kind: Literal[SourceKind.AWS]  # Using the enum member for Literal is fine
    profile: Optional[str] = None
    role: Optional[str] = None
    regions: List[str] = []
    accounts: List[str] = []
    ignore_accounts: List[str] = []
    skip_resources: List[str] = []


Sources = Annotated[Union[LibreNMSConfig, AWSConfig], Field(discriminator="kind")]


class TopLevelConfig(BaseModel):
    model_config = {
        "deprecated": {
            "output_path": "The 'output_path' field is deprecated and will be removed in a future release."
        }
    }
    sources: List[Sources]  # Pydantic uses 'kind' for discrimination
    output_path: Optional[Path] = None


def validate_yaml(yaml_file: dict, context: Optional[dict] = None) -> TopLevelConfig:
    try:
        return TopLevelConfig.model_validate(yaml_file)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML: {e}")
    except ValidationError as e:
        raise ValueError(f"Configuration validation error:\n{e}") from e
