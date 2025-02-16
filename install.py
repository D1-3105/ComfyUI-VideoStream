import pathlib
import subprocess
import requests


def get_proto_schema(git_url):
    """Downloads a .proto file from a given URL."""
    resp = requests.get(git_url)
    resp.raise_for_status()
    return resp.content.decode("utf-8")


def compile_grpc_schema():
    """Downloads and compiles gRPC schema."""
    # Root directory for proto files
    proto_root = pathlib.Path("src/protos")
    proto_root.mkdir(parents=True, exist_ok=True)

    # Directory for generated Python files
    proto_export = pathlib.Path("src/grpc_client")
    proto_export.mkdir(parents=True, exist_ok=True)

    # Paths to .proto files
    input_shard_pth = proto_root / "InputStreamShard.proto"
    vrcv_pth = proto_root / "VideoRCV.proto"

    # Download and save proto files
    input_shard_pth.write_text(get_proto_schema(
        "https://raw.githubusercontent.com/D1-3105/"
        "go_video_streamer/main/internal/InputStreamShard/InputStreamShard.proto"
    ))
    vrcv_pth.write_text(get_proto_schema(
        "https://raw.githubusercontent.com/D1-3105/"
        "go_video_streamer/main/internal/grpc_consumer/VideoRCV.proto"
    ))

    # Add __init__.py to ensure proper Python imports
    (proto_export / "__init__.py").touch()

    # Compile .proto files using subprocess
    command = [
        "python", "-m", "grpc_tools.protoc",
        f"-I={proto_root}",  # Path to proto files
        f"--python_out={proto_export}",  # Output directory for Python files
        f"--grpc_python_out={proto_export}",  # Output directory for gRPC files
        str(input_shard_pth),  # Input .proto file
        str(vrcv_pth),  # Input .proto file
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print("Compilation error:")
        print(result.stderr)
    else:
        print("gRPC files successfully compiled.")
        # Fix the imports in generated files to use relative imports
        generated_files = list(proto_export.glob("*.py"))
        for file in generated_files:
            content = file.read_text()
            # Replace absolute imports with relative ones
            content = content.replace(
                "import InputStreamShard_pb2",
                "from . import InputStreamShard_pb2"
            )
            content = content.replace(
                "import VideoRCV_pb2",
                "from . import VideoRCV_pb2"
            )
            file.write_text(content)


if __name__ == "__main__":
    compile_grpc_schema()
