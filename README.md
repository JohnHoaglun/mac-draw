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
