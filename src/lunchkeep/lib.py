import json
import pathlib
import subprocess
import typing

from . import model


def generate_json():
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


def main() -> None:
    data_path = pathlib.Path("/Users/mtm/pdev/taylormonacelli/lunchkeep/out.json")

    with open(data_path) as file:
        data = json.load(file)
        nodes_tmp = data["items"]
        nodes: typing.List[model.Node] = [model.Node(**item) for item in nodes_tmp]

    for node in nodes:
        print(node.is_control_plane, node.status.internal_ip)


if __name__ == "__main__":
    main()
