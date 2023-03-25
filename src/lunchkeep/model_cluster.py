import pydantic
import pydantic.dataclasses


@pydantic.dataclasses.dataclass
class AWSCluster:
    kind: str
