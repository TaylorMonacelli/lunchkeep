import pydantic
import pydantic.dataclasses


class NodeMetadata(pydantic.BaseModel):
    labels: dict


@pydantic.dataclasses.dataclass
class Node:
    kind: str
    metadata: NodeMetadata
    is_control_plane: bool = pydantic.Field(default=False)

    def __post_init__(self):
        if "labels" not in self.metadata:
            return

        labels = set(self.metadata["labels"])
        if "node-role.kubernetes.io/control-plane" in labels:
            self.is_control_plane = True
