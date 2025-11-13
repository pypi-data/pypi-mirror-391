from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.github_commit import GithubCommit


T = TypeVar("T", bound="GithubBranch")


@_attrs_define
class GithubBranch:
    """
    Attributes:
        name (str):
        commit (GithubCommit):
    """

    name: str
    commit: "GithubCommit"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        commit = self.commit.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "commit": commit,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.github_commit import GithubCommit

        d = dict(src_dict)
        name = d.pop("name")

        commit = GithubCommit.from_dict(d.pop("commit"))

        github_branch = cls(
            name=name,
            commit=commit,
        )

        github_branch.additional_properties = d
        return github_branch

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
