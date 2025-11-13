from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    TypeVar,
    cast,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.github_branch import GithubBranch
    from ..models.github_repository import GithubRepository


T = TypeVar("T", bound="GithubRepositoryData")


@_attrs_define
class GithubRepositoryData:
    """
    Attributes:
        integration_uuid (UUID):
        type_ (Literal['github']):
        stub (bool):
        url (str):
        github_repo (GithubRepository):
        branches (list['GithubBranch']):
        sot_branch (list[str]):
        sync_branches (list[str]):
    """

    integration_uuid: UUID
    type_: Literal["github"]
    stub: bool
    url: str
    github_repo: "GithubRepository"
    branches: list["GithubBranch"]
    sot_branch: list[str]
    sync_branches: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        integration_uuid = str(self.integration_uuid)

        type_ = self.type_

        stub = self.stub

        url = self.url

        github_repo = self.github_repo.to_dict()

        branches = []
        for branches_item_data in self.branches:
            branches_item = branches_item_data.to_dict()
            branches.append(branches_item)

        sot_branch = self.sot_branch

        sync_branches = self.sync_branches

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "integration_uuid": integration_uuid,
                "type": type_,
                "stub": stub,
                "url": url,
                "github_repo": github_repo,
                "branches": branches,
                "sot_branch": sot_branch,
                "sync_branches": sync_branches,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.github_branch import GithubBranch
        from ..models.github_repository import GithubRepository

        d = dict(src_dict)
        integration_uuid = UUID(d.pop("integration_uuid"))

        type_ = cast(Literal["github"], d.pop("type"))
        if type_ != "github":
            raise ValueError(f"type must match const 'github', got '{type_}'")

        stub = d.pop("stub")

        url = d.pop("url")

        github_repo = GithubRepository.from_dict(d.pop("github_repo"))

        branches = []
        _branches = d.pop("branches")
        for branches_item_data in _branches:
            branches_item = GithubBranch.from_dict(branches_item_data)

            branches.append(branches_item)

        sot_branch = cast(list[str], d.pop("sot_branch"))

        sync_branches = cast(list[str], d.pop("sync_branches"))

        github_repository_data = cls(
            integration_uuid=integration_uuid,
            type_=type_,
            stub=stub,
            url=url,
            github_repo=github_repo,
            branches=branches,
            sot_branch=sot_branch,
            sync_branches=sync_branches,
        )

        github_repository_data.additional_properties = d
        return github_repository_data

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
