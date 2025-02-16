import pathlib

import pytest
import torch

from PIL import Image

import numpy as np

from src.nodes import ExportSingleFrameGRPC

from .conftest import *

curr_path = pathlib.Path(__file__).parent


@pytest.fixture
def img_tensor():
    img = Image.open(curr_path / "fixtures" / 'test_img.jpg')
    img_np = np.array(img)
    img_tensor = torch.from_numpy(img_np)
    return img_tensor


def test_stream_single_input(img_tensor, launch_FloWWeaver_grpc):
    node = ExportSingleFrameGRPC()
    node.export_single_frame(frame=img_tensor, stream_id="1", fps=60, end_stream=True)
