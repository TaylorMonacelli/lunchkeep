import json
import pathlib
import subprocess
import typing

import pydantic
import pydantic.dataclasses


def main1():
    cmd = [
        "kubectl",
        "--kubeconfig=./my-cluster.kubeconfig",
        "get",
        "nodes",
        "-o",
        "wide",
    ]
    cmd_str = " ".join(cmd)

    result = subprocess.run(
        cmd_str,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    if result.returncode == 0:
        return True, result.stdout
    else:
        return False, result.stdout + result.stderr


class NodeMetadata(pydantic.BaseModel):
    labels: dict


@pydantic.dataclasses.dataclass
class Node:
    kind: str
    metadata: NodeMetadata
    is_control_plane: bool | None = pydantic.Field(
        default=False,
    )

    def __post_init__(self):
        labels = set(self.metadata["labels"])
        if "node-role.kubernetes.io/control-plane" in labels:
            self.is_control_plane = True


def main() -> None:
    data_path = pathlib.Path("/Users/mtm/pdev/taylormonacelli/lunchkeep/out.json")

    with open(data_path) as file:
        data = json.load(file)
        nodes_tmp = data["items"]
        nodes: typing.List[Node] = [Node(**item) for item in nodes_tmp]

    for node in nodes:
        print(node)


if __name__ == "__main__":
    main()
