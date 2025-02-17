import cv2
import numpy as np
import torch
from PIL import Image

from src.nodes import ExportSingleFrameGRPC
from .conftest import *

curr_path = pathlib.Path(__file__).parent


@pytest.fixture
def img_tensor():
    img = Image.open(curr_path / "fixtures" / 'test_img.jpg')
    img_np = np.array(img, dtype=np.uint8)
    img_tensor = torch.from_numpy(img_np)
    return img_tensor


def test_stream_single_input(img_tensor, launch_FloWWeaver_grpc):
    node = ExportSingleFrameGRPC()
    node.export_single_frame(frame=img_tensor.unsqueeze(0), stream_id="1", fps=60, end_stream=True)


def test_stream_multi_input(img_tensor, launch_FloWWeaver_grpc):
    node = ExportSingleFrameGRPC()

    for i in range(50):
        node.export_single_frame(frame=img_tensor.unsqueeze(0), stream_id="3", fps=10, end_stream=False)
