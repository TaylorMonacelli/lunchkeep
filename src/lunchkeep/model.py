import pydantic
import pydantic.dataclasses


class NodeStatus(pydantic.BaseModel):
    addresses: list[dict]

    @property
    def internal_ip(self) -> str | None:
        for item in self.addresses:
            if item["type"] == "InternalIP":
                return item["address"]

        return None


class NodeMetadata(pydantic.BaseModel):
    labels: dict


@pydantic.dataclasses.dataclass
class Node:
    kind: str
    status: NodeStatus
    metadata: NodeMetadata
    is_control_plane: bool = pydantic.Field(default=False)

    def __post_init__(self):
        if "labels" not in self.metadata:
            return

        labels = set(self.metadata["labels"])
        if "node-role.kubernetes.io/control-plane" in labels:
            self.is_control_plane = True
