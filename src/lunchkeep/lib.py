import subprocess


def main():
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


rc, message = main()
print(message)
