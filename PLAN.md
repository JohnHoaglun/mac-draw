# Gemma 4 12B deployment record

## Objective — complete
Deploy and verify `google/gemma-4-12B-it-qat-w4a16-ct` on the DGX Spark without changing OpenCode agent routing or disrupting the existing Gemma E2B Python-workload service.

## Completed deployment
- [x] Selected the Spark-compatible vLLM runtime and deployed Gemma 12B as `vllm-gemma4-12b`.
- [x] Bound Gemma 12B to LAN `:8012`, with 128K context, max-seq 2, fixed 12 GiB KV cache, `--gpu-memory-utilization 0.20`, and a 24 GiB container cap.
- [x] Verified `/v1/models` and a LAN chat-completion smoke test (`gemma4-12b-qat`).
- [x] Kept the E2B API/port stable; after its independent 16 GiB-cap tune, `/v1/models` is healthy as `gemma4-e2b` on LAN `:8007`.
- [x] Kept Qwen-Image-2.1 and its authenticated bridge live and private/raw-endpoint constrained as designed.
- [x] Updated the local vault deployment note and `DGX-Spark-Config` remote documentation with measured live results.
- [x] Delivered the human-facing `mac-draw "draw a picture of …"` command, automatic Keychain credential lookup, and global local launcher.

## Verified operating boundary
- All retained Spark containers use `restart: unless-stopped` and JSON log rotation of 100 MB × 7.
- Legacy LiteLLM/tools/CLI/search services and the retired Qwen MoE/dense containers are removed.
- After John’s explicit post-deployment decision, a **manual-only** provider and named `gemma4-12b-qat` agent were added to this workstation. It does not alter `build`, `research`, fallbacks, subagents, or E2B routing.
- No OpenCode agent route, `AGENTS.md`, or other-machine agent configuration was edited.

## Next deliberate phase — review, not implementation
1. Review with John which callers beyond the approved manual Gemma 12B selection should use the shared image bridge.
2. Agree a desired OpenCode/agent topology.
3. Make only the explicitly approved routing/agent changes.

## Rollback
Stop and remove only the new Gemma 12B container. E2B, Qwen Image, bridge, and agent configurations remain independent of this rollback.
