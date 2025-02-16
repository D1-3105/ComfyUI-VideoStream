import gzip
import logging
import os

import grpc
import torch
import torch.nn.functional as F

from src.grpc_client import InputStreamShard_pb2
from src.grpc_client import VideoRCV_pb2, VideoRCV_pb2_grpc

logger = logging.getLogger("FloWWeaver-exporter")


class ExportSingleFrameGRPC:
    FUNCTION = "export_single_frame"
    CATEGORY = "image/export_video_stream"
    OUTPUT_NODE = True
    RETURN_TYPES = ()

    def __init__(self):
        self.streams = dict()
        channel = grpc.insecure_channel(os.getenv("FLOWWEAVER_SERVER_ADDRESS", "localhost:50051"))
        self.grpc_client = VideoRCV_pb2_grpc.VideoRCVStub(channel)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frame": ("IMAGE",),
                "stream_id": ("STRING",),
                "fps": ("FLOAT",),
                "end_stream": ("BOOLEAN",)
            },
        }

    def export_single_frame(self, frame: torch.Tensor, stream_id, fps, end_stream: bool):
        # If the stream doesn't exist, create it
        if stream_id not in self.streams:
            new_stream = VideoRCV_pb2.NewStream(
                name=stream_id,  # Use stream_id here for the name
                fps=fps,
                width=frame.shape[2],
                height=frame.shape[1],
                streamType=0
            )
            resp: VideoRCV_pb2.EditStreamOperationResponse = self.grpc_client.AddStream(new_stream)
            logger.critical(
                f"Stream {stream_id} added: {resp.status=} {resp.message=}"
            )

            if resp.status == 200:
                self.streams[stream_id] = new_stream
            else:
                raise Exception(
                    f"Unable to create stream {stream_id=}. "
                    f"Status: {resp.status}. "
                    f"Message: {resp.message}"
                )

        # Get the stream parameters
        stream_params: VideoRCV_pb2.NewStream = self.streams[stream_id]

        frame_resized = F.interpolate(frame.unsqueeze(0), size=(stream_params.height, stream_params.width),
                                      mode='bilinear', align_corners=False).squeeze(0)

        # Prepare the NamedFrame with the resized frame
        nf = VideoRCV_pb2.NamedFrame(
            stream=stream_id,
            shard=InputStreamShard_pb2.StreamShard(
                image_data=gzip.compress(frame_resized.numpy().tobytes()),  # Convert frame to byte data
                width=frame_resized.shape[1],
                height=frame_resized.shape[2],
                fps=stream_params.fps,
                gzipped=True
            )
        )
        # Send the frame
        resp: VideoRCV_pb2.VideoStreamResponse = self.grpc_client.StreamFrames(nf)
        logger.info(f"Streamed into {stream_id=} with new frames: {resp.status=}")
        # If the stream ends, remove the stream
        if end_stream:
            rm_stream = VideoRCV_pb2.RemoveStream(name=stream_id)
            resp: VideoRCV_pb2.EditStreamOperationResponse = self.grpc_client.RMStream(rm_stream)
            logger.critical(f"Stream {stream_id} removed: {resp.status=} {resp.message=}")
            if resp.status == 200:
                del self.streams[stream_id]
