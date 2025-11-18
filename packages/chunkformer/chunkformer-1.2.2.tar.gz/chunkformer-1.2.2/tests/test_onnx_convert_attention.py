
import torch
import torch.nn as nn
import numpy as np
from chunkformer.modules.attention import ChunkAttentionWithRelativeRightContext

def test_export_onnx_attention():

    # Parameters
    batch = 1
    length = 64 * 10  # Dynamic length for q, k, v
    n_feat = 256
    n_head = 4
    dropout_rate = 0.0
    left_context_size = 128
    right_context_size = 128
    chunk_size = 64

    # Create dummy input (q, k, v are the same)
    qkv = torch.randn(batch, length, n_feat, requires_grad=False)
    mask = torch.ones(batch, 1, length, dtype=torch.bool)
    pos_emb = torch.randn(batch, length, n_feat, requires_grad=False)
    cache = torch.zeros(1, 0, 0, 0)

    # Initialize module
    attn = ChunkAttentionWithRelativeRightContext(
        n_head=n_head,
        n_feat=n_feat,
        dropout_rate=dropout_rate,
    )
    attn.eval()

    attn_out = attn(qkv, qkv, qkv, mask, pos_emb, cache, chunk_size, left_context_size, right_context_size)
    print(attn_out[0].shape, attn_out[1].shape)

    # export torchscript
    # attn = torch.jit.script(attn, example_inputs=(qkv, qkv, qkv, mask, pos_emb, cache, chunk_size, left_context_size, right_context_size))
    # filename = "/raid/agi-ds/data-sharing/common/khanhle2/chunkformer/tests/att_jit.pt"
    # attn.save(str(filename))
    # exit()


    # Export to ONNX
    torch.onnx.export(
        attn,
        (qkv, qkv, qkv, mask, pos_emb, cache, chunk_size, left_context_size, right_context_size),
        "test_chunk_attention.onnx",
        input_names=["query", "key", "value", "mask", "pos_emb", "cache", "chunk_size", "left_context_size", "right_context_size"],
        output_names=["output"],
        opset_version=17,
        dynamic_axes={
            "query": {0: "batch", 1: "time1"},
            "key": {0: "batch", 1: "time2"},
            "value": {0: "batch", 1: "time2"},
            "mask": {0: "batch", 2: "time2"},
            "output": {0: "batch", 1: "time1"},
        },
        dynamo=True,
        report=False,
        profile=False
    )
    print("ONNX export succeeded.")

if __name__ == "__main__":
    test_export_onnx_attention()
