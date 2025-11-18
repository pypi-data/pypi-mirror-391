
import torch
import torch.nn as nn
from chunkformer.modules.attention import ChunkAttentionWithRelativeRightContext
from chunkformer.modules.encoder_layer import ChunkFormerEncoderLayer

def main():
    # Parameters
    batch = 1
    length = 640  # e.g. 10 chunks of 64
    n_feat = 256
    n_head = 4
    dropout_rate = 0.0
    left_context_size = 128
    right_context_size = 128
    chunk_size = 64

    # Dummy input
    x = torch.randn(batch, length, n_feat, requires_grad=False)
    mask = torch.ones(batch, length, length, dtype=torch.bool)
    pos_emb = torch.randn(batch, length, n_feat, requires_grad=False)
    mask_pad = torch.ones(batch, 1, length, dtype=torch.bool)
    att_cache = torch.zeros(0, 0, 0, 0)
    cnn_cache = torch.zeros(0, 0, 0)

    # Attention module
    attn = ChunkAttentionWithRelativeRightContext(
        n_head=n_head,
        n_feat=n_feat,
        dropout_rate=dropout_rate,
    )

    # Convolution module
    from chunkformer.modules.convolution import ChunkConvolutionModule
    conv = ChunkConvolutionModule(
        channels=n_feat,
        kernel_size=15,
        activation=nn.ReLU(),
        norm="batch_norm",
        causal=False,
        bias=True,
        dynamic_conv=True,
    )

    # Encoder layer
    encoder_layer = ChunkFormerEncoderLayer(
        size=n_feat,
        self_attn=attn,
        feed_forward=None,
        feed_forward_macaron=None,
        conv_module=conv,
        dropout_rate=dropout_rate,
        normalize_before=True,
    )
    encoder_layer.eval()

    # Forward once for shape check
    out = encoder_layer(x, mask, pos_emb, mask_pad, att_cache, cnn_cache, chunk_size, left_context_size, right_context_size)
    print([o.shape if isinstance(o, torch.Tensor) else o for o in out])

    # Export to ONNX
    onnx_path = "test_encoder_layer.onnx"
    torch.onnx.export(
        encoder_layer,
        (x, mask, pos_emb, mask_pad, att_cache, cnn_cache, chunk_size, left_context_size, right_context_size),
        onnx_path,
        input_names=["x", "mask", "pos_emb", "mask_pad", "att_cache", "cnn_cache", "chunk_size", "left_context_size", "right_context_size"],
        output_names=["output", "mask_out", "att_cache_out", "cnn_cache_out"],
        opset_version=17,
        dynamic_axes={
            "x": {0: "batch", 1: "time"},
            "mask": {0: "batch", 1: "time", 2: "time"},
            "pos_emb": {0: "batch", 1: "time"},
            "mask_pad": {0: "batch", 2: "time"},
            "output": {0: "batch", 1: "time"},
            "mask_out": {0: "batch", 1: "time", 2: "time"},
        },
        dynamo=True
    )
    print(f"ONNX export succeeded: {onnx_path}")

if __name__ == "__main__":
    main()

