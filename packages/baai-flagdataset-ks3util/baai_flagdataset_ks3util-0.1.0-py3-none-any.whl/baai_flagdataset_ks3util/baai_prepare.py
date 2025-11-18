import os
import pathlib

HOME = pathlib.Path(os.path.expanduser("~")) / ".sdk_download"


def ks3util():
    util_path = HOME / "ks3util"

    if util_path.exists():
       return util_path.absolute().__str__()
    # TODO: 获取ks3util, 放到具体使用该包的地方进行下载
    return util_path.absolute().__str__()
