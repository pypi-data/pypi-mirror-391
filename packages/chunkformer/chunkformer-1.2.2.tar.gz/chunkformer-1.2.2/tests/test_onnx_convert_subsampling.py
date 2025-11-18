
import torch
import torch.nn as nn
from chunkformer.modules.subsampling import DepthwiseConvSubsampling
from chunkformer.modules.embedding import RelPositionalEncodingWithRightContext

def test_export_onnx_subsampling():
    # Parameters
    batch = 1
    length = 487  # e.g., 10 chunks of 32
    feat_in = 80
    feat_out = 256
    conv_channels = 256
    subsampling = "dwconv"
    subsampling_rate = 8
    subsampling_conv_chunking_factor = -1
    dropout_rate = 0.0
    left_context_size = 128
    right_context_size = 128
    chunk_size = 64

    # Dummy input
    x = torch.randn(batch, length, feat_in)
    mask = torch.ones(batch, 1, length, dtype=torch.int)

    # Relative positional encoding with right context
    pos_enc = RelPositionalEncodingWithRightContext(d_model=feat_out, dropout_rate=dropout_rate)

    # Initialize subsampling module
    subsample = DepthwiseConvSubsampling(
        subsampling=subsampling,
        subsampling_rate=subsampling_rate,
        feat_in=feat_in,
        feat_out=feat_out,
        conv_channels=conv_channels,
        pos_enc_class=pos_enc,
        subsampling_conv_chunking_factor=subsampling_conv_chunking_factor,
        activation=nn.ReLU(),
    )
    subsample.eval()

    # Forward pass
    out, pos_emb, mask = subsample(x, mask)
    print(out.shape, pos_emb.shape, mask.shape)

    # Export to ONNX
    torch.onnx.export(
        subsample,
        (x, mask),
        "test_subsampling.onnx",
        input_names=["x", "mask"],
        output_names=["out", "pos_emb", "out_mask"],
        opset_version=17,
        dynamic_axes={
            "x": {0: "batch", 1: "time"},
            "mask": {0: "batch", 2: "time"},
            "out": {0: "batch", 1: "time_out"},
            "pos_emb": {0: "batch", 1: "time_pos"},
            "out_mask": {0: "batch", 2: "time_out"},
        },
        dynamo=True,
        report= False,
        profile=False,
        strict=False,
        do_constant_folding=True

    )
    print("ONNX export succeeded.")

if __name__ == "__main__":
    test_export_onnx_subsampling()
