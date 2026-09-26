# Gemma 4 12B deployment plan

## Objective
Deploy and verify `google/gemma-4-12B-it-qat-w4a16-ct` on DGX Spark without changing OpenCode agent routing or disrupting the existing Gemma E2B Python-workload service.

## Fixed sequencing
1. Deploy and test Gemma 12B.
2. Update documentation using measured live results.
3. Review agent/settings routing with John.
4. Make agent changes only after that review and explicit approval.

## Scope boundaries
- Keep `vllm-gemma4-e2b` running and unchanged.
- Keep Qwen-Image-2.1 and its authenticated bridge running.
- Do not edit `~/.config/opencode/opencode.json`, `~/opencode/AGENTS.md`, or any other machine's agent settings in phases 1–2.

## Deployment gates
- [ ] Select a Spark-compatible serving image/runtime for the QAT compressed-tensors checkpoint.
- [ ] Download model and start a memory-capped test service on a new, non-conflicting loopback port.
- [ ] Verify `/health` or `/v1/models` and complete text generation.
- [ ] Verify image/tool capability only if the runtime advertises and accepts it.
- [ ] Measure load/runtime memory and a representative response latency.
- [ ] Promote to LAN service only after tests pass.
- [ ] Update Spark configuration documentation and the vault deployment note.
- [ ] Hold routing/agent review; no edits before explicit approval.

## Rollback
Stop and remove only the new Gemma 12B container. Existing E2B, Qwen Image, bridge, and stopped legacy Qwen containers are out of scope.
