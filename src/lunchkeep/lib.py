import dataclasses
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


# cat <<'__eot__' >data.json
# [
#   {
#     "test": "Zero to One",
#     "title": "Zero to One",
#     "subtitle": "Notes on Startups, or How to Build the Future",
#     "author": "Peter Thiel",
#     "publisher": "Ballantine Books",
#     "isbn_10": "0753555190",
#     "isbn_13": "978-0753555194",
#     "price": 14.29,
#     "author2": {
#       "name": "Peter Thiel",
#       "verified": true
#     }
#   },
#   {
#     "title": "The Lean Startup",
#     "subtitle": "How Relentless Change Creates Radically Successful Businesses",
#     "author": "Eric Ries",
#     "publisher": "Penguin UK",
#     "isbn_10": "0670921602",
#     "isbn_13": "978-0670921607",
#     "price": 12.96
#   }
# ]
# __eot__
# #+END_SRC


class NodeMetadata(pydantic.BaseModel):
    labels: dict
    annotations: dict


@dataclasses.dataclass
class Node(pydantic.BaseModel):
    kind: str
    metadata: NodeMetadata
    is_control_plane: bool = dataclasses.field(init=False)

    def __post_init__(self):
        labels = set(self.metadata.labels)
        if "node-role.kubernetes.io/control-plane" in labels:
            self.is_control_plane = True


def main() -> None:
    """Main function."""

    data_path = pathlib.Path("/Users/mtm/pdev/taylormonacelli/lunchkeep/out.json")

    with open(data_path) as file:
        data = json.load(file)
        nodes_tmp = data["items"]
        nodes: typing.List[Node] = [Node(**item) for item in nodes_tmp]

    for node in nodes:
        print(node.kind)


#    print(books[0])
#    print(books[0].dict(exclude={"price"}))
#    print(books[1].copy())


if __name__ == "__main__":
    main()
