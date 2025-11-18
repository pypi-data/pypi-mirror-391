import os
import pathlib

__all__ = [
    "multi_download",
]


def multi_download(use_loc: str, network: str, max_parallel: int, share_url: str):
    from .share_cp import share_cp_with_cmdargs_output

    home = pathlib.Path(os.path.expanduser("~")) / ".sdk_download"
    if not home.exists():
        home.mkdir(parents=True)

    config_public = home / "ks3utilconfig.public"
    if not config_public.exists():
        with config_public.open("w") as f:
            f.write("""[Credentials]
language
accessKeyID=public
accessKeySecret=sccret
endpoint=ks3-cn-beijing.ksyuncs.com
loglevel=info""")

    config_private = home / "ks3utilconfig.private"
    if not config_private.exists():
        with config_private.open("w") as f:
            f.write("""[Credentials]
language
accessKeyID=private
accessKeySecret=sccret
endpoint=ks3-cn-beijing-internal.ksyuncs.com
loglevel=info
""")

    if network == "public":
        share_cp_with_cmdargs_output(share_url, use_loc, max_parallel, config_public.absolute().__str__())
    else:
        share_cp_with_cmdargs_output(share_url, use_loc, max_parallel, config_private.absolute().__str__())

