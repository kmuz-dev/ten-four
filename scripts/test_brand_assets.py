#!/usr/bin/env python3
"""Small deterministic checks for the generated Ten-Four brand assets."""

import unittest
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops

from gen_brand_assets import BLACK, ROOT, TALLY, WHITE, app_icon, tray


class BrandAssetTests(unittest.TestCase):
    def test_app_icon_has_safe_area_and_tally_details(self):
        icon = app_icon(256)
        self.assertEqual(icon.size, (256, 256))
        self.assertEqual(icon.mode, "RGBA")

        pixels = np.array(icon)
        opaque = Image.fromarray((pixels[:, :, 3] >= 240).astype("uint8") * 255)
        opaque_box = opaque.getbbox()
        self.assertIsNotNone(opaque_box)
        self.assertGreaterEqual(opaque_box[0], 20)
        self.assertGreaterEqual(opaque_box[1], 20)
        self.assertLessEqual(opaque_box[2], 236)
        self.assertLessEqual(opaque_box[3], 236)

        tally = np.all(pixels == np.array(TALLY), axis=2)
        self.assertGreater(int(tally.sum()), 100)

    def test_tray_states_keep_recording_semantics(self):
        idle = np.array(tray(WHITE, state="idle"))
        recording = np.array(tray(WHITE, state="recording"))
        transcribing = np.array(tray(WHITE, state="transcribing"))

        tally = np.array(TALLY)
        self.assertFalse(np.any(np.all(idle == tally, axis=2)))
        self.assertTrue(np.any(np.all(recording == tally, axis=2)))
        self.assertFalse(np.any(np.all(transcribing == tally, axis=2)))

        dark_idle = tray(BLACK, state="idle")
        self.assertIsNotNone(dark_idle.getchannel("A").getbbox())

    def test_committed_master_matches_generator(self):
        committed_path = Path(ROOT) / "src-tauri" / "icons" / "app-icon.png"
        committed = Image.open(committed_path).convert("RGBA")
        difference = ImageChops.difference(committed, app_icon())
        self.assertIsNone(difference.getbbox())


if __name__ == "__main__":
    unittest.main()
