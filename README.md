# mac-draw

`picture` is a Mac-local command-line client for a LAN-hosted image-generation bridge. It does not host a model: it submits generation/edit requests, receives the result, and saves images plus reproducibility metadata into an Obsidian vault.

## Planned flow

```text
picture on macOS → authenticated LAN image bridge → Qwen-Image on DGX Spark
                         ↓
                PNG + metadata returned
                         ↓
              local Obsidian vault / Attachments/gen
```

## Initial commands

```bash
picture draw "A dragon flying over a field" --size 1024x1024
picture edit Attachments/gen/dragon.png "Make it red at sunset"
picture config show
```

The bridge contract and Spark deployment will be added separately. The client intentionally keeps the vault write local and never stores credentials in the vault.

## Configuration

Print a starting configuration:

```bash
picture config sample
```

Save it as `~/.config/picture/config.toml`, set `PICTURE_API_KEY` in your shell or Keychain-backed launcher, and point `vault.path` at the local Obsidian vault. The bridge contract is JSON over HTTPS:

- `POST /v1/images/generations` accepts `prompt`, `size`, optional `seed`, and optional `session_id`.
- `POST /v1/images/edits` accepts the same edit prompt plus `image_b64` and `image_name`.
- Both return OpenAI-style `data[0].b64_json` and optional `metadata`.

Successful calls write a `.png` plus a JSON reproducibility sidecar to `Attachments/gen/` by default.
