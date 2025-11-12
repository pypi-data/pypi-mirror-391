"""
Tests for fallback resampling path when rasterio is unavailable.
"""

import unittest
import numpy as np

from myreze.viz.tiles import xyz as xyz_mod


class TestXYZFallbackResampling(unittest.TestCase):
    def setUp(self):
        # Simple deterministic grid to make sampling stable
        self.grid = np.arange(100 * 100, dtype=np.float32).reshape(100, 100)
        self.metadata = {
            "bounds": [-74.1, 40.6, -73.8, 40.9],
            "crs": "EPSG:4326",
            "colormap": "viridis",
        }

    def test_render_with_fallback(self):
        # Force fallback path by disabling rasterio
        original_has_rio = xyz_mod.HAS_RASTERIO
        try:
            xyz_mod.HAS_RASTERIO = False
            rgba_tile = xyz_mod.render_xyz_tile(
                data={"grid": self.grid},
                metadata=self.metadata,
                x=301,
                y=384,
                z=10,
                tile_size=256,
            )

            self.assertEqual(rgba_tile.shape, (256, 256, 4))
            self.assertEqual(rgba_tile.dtype, np.uint8)
        finally:
            xyz_mod.HAS_RASTERIO = original_has_rio


if __name__ == "__main__":
    unittest.main(verbosity=2)
