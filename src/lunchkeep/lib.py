import datetime
import json as jsonmod
import pathlib
import subprocess
import typing

import jinja2
import pkg_resources
import platformdirs

from . import model

package = __name__.split(".")[0]
templates_dir = pathlib.Path(pkg_resources.resource_filename(package, "templates"))
loader = jinja2.FileSystemLoader(searchpath=templates_dir)
env = jinja2.Environment(loader=loader, keep_trailing_newline=True)

appname = package
appauthor = "taylor"
_dir = platformdirs.user_cache_dir(appname, appauthor)
cache_dir = pathlib.Path(_dir)
cache_path = cache_dir / "data.json"
cache_path.parent.mkdir(exist_ok=True, parents=True)


def run_kubectl():
    cmd = [
        "kubectl",
        "--kubeconfig=./my-cluster.kubeconfig",
        "get",
        "nodes",
        "-o",
        "json",
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


def categorize_nodes(nodes: list[model.Node]) -> dict:
    bastion_nodes = []
    control_plane_nodes = []
    worker_nodes = []

    for node in nodes:
        if node.is_control_plane:
            control_plane_nodes.append(node)
        else:
            worker_nodes.append(node)

    data = {
        "workers": worker_nodes,
        "control_plane": control_plane_nodes,
        "bastions": bastion_nodes,
    }

    return data


def regenerate_cache():
    rc, json = run_kubectl()
    if not rc:
        msg = f"failed to run kubectl, {json}"
        raise ValueError(msg)

    out = jsonmod.dumps(json)
    cache_path.write_text(out)


def write_cache() -> dict:
    if not cache_path.exists():
        regenerate_cache()

    mtime = cache_path.stat().st_mtime
    timestamp = datetime.datetime.fromtimestamp(mtime)
    now = datetime.datetime.now()
    cache_is_old = now - timestamp > datetime.timedelta(hours=3)

    if cache_is_old:
        regenerate_cache()


def main() -> None:
    write_cache()
    with open(cache_path) as file:
        nodes_dict = jsonmod.load(file)
        nodes: typing.List[model.Node] = [
            model.Node(**node) for node in nodes_dict["items"]
        ]

    template = env.get_template("ssh-config.j2")
    data = categorize_nodes(nodes)
    out = template.render(data=data)
    print(out)


if __name__ == "__main__":
    main()
