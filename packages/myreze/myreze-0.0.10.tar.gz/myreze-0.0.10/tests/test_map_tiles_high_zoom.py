"""
Tests for high-zoom behavior in XYZ tile rendering.
"""

import unittest
import numpy as np
from PIL import Image
import io
import base64

from myreze.data import MyrezeDataPackage, Time


class TestHighZoomTiles(unittest.TestCase):
    def setUp(self):
        # Small grid with nonzero values to detect content
        self.grid_data = {"grid": np.ones((32, 32), dtype=np.float32)}
        self.grid_metadata = {
            "bounds": [-74.1, 40.6, -73.8, 40.9],
            "crs": "EPSG:4326",
            "colormap": "viridis",
        }

        self.pkg = MyrezeDataPackage(
            id="zoom-test",
            data=self.grid_data,
            time=Time.timestamp("2023-06-15T14:30:00Z"),
            metadata=self.grid_metadata,
            visualization_type="map_tile",
        )

    def test_extreme_zoom_tiles_have_content(self):
        # Use tile that overlaps at reasonable zoom
        x, y, z = 301, 384, 10
        # Excessive zoom should still produce some content, not empty
        rgba_bytes = self.pkg.map_tile(x=x * 32, y=y * 32, z=z + 5)
        self.assertTrue(rgba_bytes.startswith(b"\x89PNG"))
        img = Image.open(io.BytesIO(rgba_bytes))
        arr = np.array(img)
        # Should not be entirely transparent
        self.assertTrue(np.any(arr[:, :, 3] > 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
