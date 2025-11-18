import torch
import torch.nn as nn
import numpy as np
from chunkformer.modules.convolution import ChunkConvolutionModule

def test_export_onnx_convolution():
    # Parameters
    batch = 1
    time = 64  # Use a fixed length for ONNX export
    channels = 80
    kernel_size = 15
    dynamic_conv = True  # Set to True if you want to test dynamic conv

    # Create dummy input
    x = torch.randn(batch, time, channels, requires_grad=False)
    mask_pad = torch.ones(batch, 1, time, dtype=torch.bool)
    cache = torch.zeros(batch, channels, 0)
    chunk_size = 64

    # Initialize module
    conv = ChunkConvolutionModule(
        channels=channels,
        kernel_size=kernel_size,
        activation=nn.ReLU(),
        norm="batch_norm",
        causal=False,
        bias=True,
        dynamic_conv=dynamic_conv,
    )
    conv.eval()

    out_conv = conv(x, mask_pad, cache, chunk_size)
    print(out_conv[0].shape, out_conv[1].shape)

    # Export to ONNX
    torch.onnx.export(
        conv,
        (x, mask_pad, cache, chunk_size),
        "test_convolution.onnx",
        input_names=["x", "mask_pad", "cache", "chunk_size"],
        output_names=["output", "new_cache"],
        opset_version=17,
        dynamic_axes={
            "x": {0: "batch", 1: "time"},
            "mask_pad": {0: "batch", 2: "time"},
            "output": {0: "batch", 1: "time"},
        },
        dynamo=True
    )
    print("ONNX export succeeded.")

if __name__ == "__main__":
    test_export_onnx_convolution()
