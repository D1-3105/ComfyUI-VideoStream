import pathlib
import subprocess
import time

import psutil
import pytest


@pytest.fixture()
def git_pull_FloWWeaver():
    curr_dir = pathlib.Path(__file__).parent
    flowweaver_pth = curr_dir / "FloWWeaver"
    if not flowweaver_pth.exists():
        res = subprocess.run(
            f"git clone https://github.com/D1-3105/go_video_streamer.git {flowweaver_pth}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert res.returncode == 0
    return flowweaver_pth


def is_port_listening(port=50051):
    for conn in psutil.net_connections():
        if conn.status == 'LISTEN' and conn.laddr.port == port:
            return True
    return False


@pytest.fixture()
def launch_FloWWeaver_grpc(git_pull_FloWWeaver):  # noqa
    if not is_port_listening():
        flowweaver_pth = git_pull_FloWWeaver

        if not (exe := flowweaver_pth / "FloWWeaver.exe").exists():
            res = subprocess.run(
                f"GOMOD={flowweaver_pth / 'go.mod'} "
                f"go build -o {exe} {flowweaver_pth / 'cmd' / 'grpc_app' / 'main.go'}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=flowweaver_pth
            )
            assert res.returncode == 0, f"{res.stderr=}\n\n{res.stdout=}"

        flowweaver_process = subprocess.Popen(
            f"GRPC_PORT=50051 {exe}", shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        time.sleep(4)
        try:
            assert is_port_listening(50051)
            yield
        finally:
            flowweaver_process.terminate()
    else:
        yield
