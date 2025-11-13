from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GithubRepository")


@_attrs_define
class GithubRepository:
    """
    Attributes:
        id (int):
        name (str):
        full_name (str):
        html_url (str):
        description (Union[None, str]):
        git_url (str):
        ssh_url (str):
        default_branch (str):
        archived (bool):
        disabled (bool):
        url (str):
        clone_url (str):
    """

    id: int
    name: str
    full_name: str
    html_url: str
    description: Union[None, str]
    git_url: str
    ssh_url: str
    default_branch: str
    archived: bool
    disabled: bool
    url: str
    clone_url: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        full_name = self.full_name

        html_url = self.html_url

        description: Union[None, str]
        description = self.description

        git_url = self.git_url

        ssh_url = self.ssh_url

        default_branch = self.default_branch

        archived = self.archived

        disabled = self.disabled

        url = self.url

        clone_url = self.clone_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "full_name": full_name,
                "html_url": html_url,
                "description": description,
                "git_url": git_url,
                "ssh_url": ssh_url,
                "default_branch": default_branch,
                "archived": archived,
                "disabled": disabled,
                "url": url,
                "clone_url": clone_url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        full_name = d.pop("full_name")

        html_url = d.pop("html_url")

        def _parse_description(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        description = _parse_description(d.pop("description"))

        git_url = d.pop("git_url")

        ssh_url = d.pop("ssh_url")

        default_branch = d.pop("default_branch")

        archived = d.pop("archived")

        disabled = d.pop("disabled")

        url = d.pop("url")

        clone_url = d.pop("clone_url")

        github_repository = cls(
            id=id,
            name=name,
            full_name=full_name,
            html_url=html_url,
            description=description,
            git_url=git_url,
            ssh_url=ssh_url,
            default_branch=default_branch,
            archived=archived,
            disabled=disabled,
            url=url,
            clone_url=clone_url,
        )

        github_repository.additional_properties = d
        return github_repository

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
