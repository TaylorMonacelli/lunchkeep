import datetime
import json as jsonmod
import logging
import os
import pathlib
import subprocess
import sys
import typing

import jinja2
import pkg_resources
import platformdirs

from . import model

_logger = logging.getLogger(__name__)

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
ssh_config_path = pathlib.Path("~/.ssh/cluster-api-test.config").expanduser()
kubeconfig_path = pathlib.Path.cwd() / "my-cluster.kubeconfig"

keyname = "AWS_SSH_KEY_NAME"
if not os.getenv(keyname, None):
    msg = f"{keyname} not defined"
    raise ValueError(msg)
ssh_identity_path = pathlib.Path(f"~/.ssh/{os.getenv(keyname, None)}.pem").expanduser()


def normalize_newlines(s: str) -> str:
    """
    Normalizes new lines such they are comparable across different operating systems
    :param s:
    :return:
    """
    return s.replace("\r\n", "\n").replace("\r", "\n")


def run_process(
    cmd: typing.Any,
    env: typing.Any = None,
    print_error: bool = True,
    raise_exception: bool = True,
    timeout: typing.Optional[float] = None,
) -> typing.Tuple[str, str]:
    try:
        process = subprocess.Popen(
            args=cmd,
            shell=False,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        bstdout, bstderr = process.communicate(timeout=timeout)
        stdout = normalize_newlines(bstdout.decode().rstrip())
        stderr = normalize_newlines(bstderr.decode().rstrip())
        if process.returncode != 0:
            if print_error:
                sys.stderr.write(f"Subprocess error:\n{stderr}\n")
            if raise_exception:
                raise subprocess.CalledProcessError(
                    returncode=process.returncode, cmd=cmd
                )
        return stdout, stderr
    except Exception as e:
        if print_error:
            cmd = " ".join(cmd)
            sys.stderr.write(f"=== Error executing:\n{cmd}\n===================")
        raise e


def run_kubectl():
    cmd = [
        "kubectl",
        "--kubeconfig",
        str(kubeconfig_path),
        "get",
        "nodes",
        "-o",
        "json",
    ]
    stdout, stderr = run_process(cmd)
    _logger.debug(stdout)

    return stdout


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
    json = run_kubectl()
    cache_path.write_text(json)


def write_cache() -> dict:
    if not cache_path.exists():
        regenerate_cache()

    mtime = cache_path.stat().st_mtime
    timestamp = datetime.datetime.fromtimestamp(mtime)
    now = datetime.datetime.now()
    cache_is_old = now - timestamp > datetime.timedelta(hours=3)

    if cache_is_old:
        msg = f"{cache_path} is old, regenerating"
        _logger.debug(msg)
        regenerate_cache()


def main(args) -> None:
    if args.show_config:
        msg = f"{cache_path}"
        # _logger.info(message)
        print(msg)

    write_cache()
    with open(cache_path) as file:
        nodes_dict = jsonmod.load(file)
        nodes: typing.List[model.Node] = [
            model.Node(**node) for node in nodes_dict["items"]
        ]

    template = env.get_template("ssh-config.j2")
    node_data = categorize_nodes(nodes)
    data = {"ssh_identity_path": str(ssh_identity_path), **node_data}

    out = template.render(data=data)
    ssh_config_path.write_text(out)


if __name__ == "__main__":
    main()
