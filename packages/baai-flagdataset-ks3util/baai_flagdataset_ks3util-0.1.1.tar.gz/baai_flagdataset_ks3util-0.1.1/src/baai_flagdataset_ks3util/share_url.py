import subprocess

from .baai_prepare import ks3util


def _get_share_url(output: str):
    lines = output.split("\n")
    for line in lines:
        if line.startswith("http"):
            return line
    return None


def get_share_url(dir_path, ak=None, sk=None):
    cmd_args = [
        ks3util(),
        "share-create",
        "--access-code",
        "123456",
        "--valid-period",
        "30d",
        dir_path,
    ]

    if ak and sk:
        cmd_args.append("-i")
        cmd_args.append(ak)
        cmd_args.append("-k")
        cmd_args.append(sk)

    result = subprocess.run(
        cmd_args,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    return _get_share_url(result.stdout)

