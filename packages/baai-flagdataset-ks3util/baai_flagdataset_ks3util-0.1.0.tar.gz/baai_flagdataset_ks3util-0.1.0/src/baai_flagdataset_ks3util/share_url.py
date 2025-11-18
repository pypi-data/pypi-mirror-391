import subprocess


def _get_share_url(output: str):
    lines = output.split("\n")
    for line in lines:
        if line.startswith("http"):
            return line
    return None


def get_share_url(dir_path):
    result = subprocess.run(
        [
            "/Users/hgshicc/.sdk_download/ks3util",
            "share-create",
            "--access-code",
            "123456",
            "--valid-period",
            "30d",
            dir_path,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    return _get_share_url(result.stdout)

