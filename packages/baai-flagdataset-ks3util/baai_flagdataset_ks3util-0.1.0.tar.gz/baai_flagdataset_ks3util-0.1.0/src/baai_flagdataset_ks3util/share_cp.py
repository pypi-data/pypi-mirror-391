import pathlib
import subprocess
from collections import deque


from .baai_prepare import ks3util


def share_cp_with_cmdargs_output(share_url, save_path=".", jobs=20):
    local_dir = (pathlib.Path(save_path) / "data").absolute().__str__()

    cmd_args = [
        ks3util(),
        "share-cp",
        share_url,
        local_dir,
        "--access-code",
        "123456",
        "-u",
        "-j",
        f"{jobs}"
    ]

    process = subprocess.Popen(
        cmd_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        bufsize=1  # 行缓冲
    )

    output = deque([])
    while True:
        if len(output) > 2:
            p1 = output.popleft()
            p2 = output.popleft()

            p3 = "".join([p1, p2])
            if p3.count('[') == 2:
                start = p3.find('[')
                end = p3[start:]
                print('\033[2K\033[1G' + p3[start:end].replace('\n', '').replace('\r', ''), end="", flush=True)
                output.appendleft(p3[end:])
            else:
                output.appendleft(p3)

        chunk = process.stdout.read(150)
        if process.poll() is not None:
            break

        if len(output) == 1:
            chunk = output.popleft() +  chunk

        if chunk.count("[") == 0:
            # print(chunk)
            continue

        pos  = chunk.find("[")
        # if pos != 0:
        #     print(chunk[:pos])
        end_ = chunk[pos+1:].find("[")
        if end_ != -1:
            print('\033[2K\033[1G' + chunk[pos:end_+1].replace('\n', '').replace('\r', ''), end="", flush=True)
            output.append(chunk[end_+1:])
            continue

        output.append(chunk[pos:])

    output.append(process.stdout.read())
    print("")
    end_lines = "".join(output).split("\n")
    print("\n".join(end_lines[1:]))



def share_cp_with_cmdargs_log(share_url, save_path="."):
    data_dir = (pathlib.Path(save_path) / "data").absolute().__str__()
    log_dir = (pathlib.Path(save_path) / "log")
    log_dir.mkdir(exist_ok=True)
    log_file = (log_dir / "app.log").absolute().__str__()

    cmd_args = [
        ks3util(),
        "share-cp",
        share_url,
        data_dir,
        "--access-code",
        "123456",
        "-u",
        "-j",
        "20",
    ]

    with open(log_file, "w", encoding="utf-8") as f:
        proc = subprocess.Popen(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=0,
        )

        while proc.poll() is None:
            line = proc.stdout.readline()

            if not line:
                continue

            # 将\r替换为\n, 确保换行, 同时去除多余空白
            processed_line = line.replace("\r", "\n").strip() + "\n"
            f.write(processed_line)
            f.flush()

        # 读取剩余输出(子进程结束后可能有残留)
        remaining = proc.stdout.read()

        if remaining:
            processed_remaining = remaining.replace("\r", "\n").strip() + "\n"
            f.write(processed_remaining)
            f.flush()