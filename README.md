# mac-draw

`mac-draw` is a human-facing Mac command for generating images through the authenticated Qwen-Image bridge on the DGX Spark. It saves the PNG and reproducibility JSON locally in the Obsidian vault.

## Draw an image

```bash
mac-draw "draw a picture of a red dragon over a sunset field"
```

That is the normal workflow. The command reads the bridge token automatically from the macOS Keychain service `mac-draw-image-bridge`; no exported token or developer-path command is needed.

Optional controls remain available:

```bash
mac-draw "a red dragon over a sunset field" --size 1024x1024 --session-id dragon-01
mac-draw config show
```

Generated PNGs and JSON sidecars are written to `Attachments/gen/` in the configured local vault. The current bridge is `http://192.168.4.52:8092`; raw Qwen Image is never exposed to the LAN.

## Configuration

The local, non-secret file is `~/.config/picture/config.toml`. Print a template with:

```bash
mac-draw config sample
```

The default Keychain service is `mac-draw-image-bridge`. `PICTURE_API_KEY` remains an optional temporary override for automation; it is not required for ordinary interactive use.

## Current boundary

- `mac-draw` / `picture draw` creates a new image and is live.
- `picture edit` is intentionally unavailable until the bridge translates the client’s request to Qwen’s required multipart edit API.
- Tool adapters such as `draw_picture` for coding/chat harnesses are future integration work; they should call this same bridge contract rather than duplicate image code.
