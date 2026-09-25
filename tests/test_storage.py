import json
import tempfile
import unittest
from pathlib import Path

from mac_draw.config import ClientConfig
from mac_draw.storage import save_asset


class StorageTests(unittest.TestCase):
    def test_saves_png_and_reproducibility_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            config = ClientConfig(
                bridge_url="https://bridge.example",
                api_key="test-key",
                vault_path=vault,
            )
            asset = save_asset(
                config,
                image_bytes=b"not-a-real-png",
                prompt="A red dragon",
                seed=42,
                session_id="dragon-01",
                parent_image=None,
                bridge_metadata={"model": "test"},
            )
            self.assertTrue((vault / asset.path).is_file())
            metadata = json.loads((vault / asset.metadata_path).read_text())
            self.assertEqual(metadata["prompt"], "A red dragon")
            self.assertEqual(metadata["seed"], 42)
            self.assertEqual(metadata["embed"], asset.embed)


if __name__ == "__main__":
    unittest.main()
