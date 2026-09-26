# Spark multimodal deployment TODO

## Completed
- [x] Deploy and LAN-smoke-test Gemma 4 12B QAT on the DGX Spark.
- [x] Tune Gemma 12B to 128K context / max-seq 2 / fixed 12 GiB KV.
- [x] Tune and validate E2B's 16 GiB container cap without changing its API contract.
- [x] Tune Qwen-Image-2.1 to a 48 GiB cap; keep its raw service loopback-only.
- [x] Recreate retained services with `restart: unless-stopped` and 100 MB × 7 log rotation.
- [x] Remove legacy routers/search/Qwen services and unused data; document final disk state.
- [x] Update the vault note and the DGX-Spark-Config repository.
- [x] Add `gx10-gemma12/gemma4-12b-qat` and its named `gemma4-12b-qat` manual agent on Mac and Windows; preserve active routes.
- [x] Inventory Pi and Windows harnesses: Pi has no installed harness/config to update; Windows Codex remains independently cloud-configured.

## Pending review with John
- [ ] Decide the caller skill/API design for `draw_picture` and, later, `edit_picture`.
- [ ] Decide whether any OpenCode agents should target Gemma 12B or the image bridge.
- [ ] Review agent/settings topology before making any config edits.

## Explicitly deferred
- [ ] Enable real image edits: translate client/bridge JSON+base64 into Qwen's native multipart edit API.
- [ ] OpenCode and other-machine agent/config edits — require the post-deployment review and explicit approval.
