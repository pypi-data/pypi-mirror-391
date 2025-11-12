from myreze.viz.threejs.threejs import ThreeJSRenderer
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import json
from shapely.geometry import shape, Point, LineString, Polygon, MultiPolygon
from shapely.ops import transform
import pyproj
from functools import partial


@ThreeJSRenderer.register
class GeoJSONRenderer(ThreeJSRenderer):
    """
    Render GeoJSON data for ThreeJS visualization.
    
    This renderer converts GeoJSON features into ThreeJS-compatible format,
    handling polygons, lines, and points with styling and text labels.
    """

    def render(
        self, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Render GeoJSON data package for ThreeJS.

        Args:
            data: Data dictionary containing GeoJSON features
            params: Optional rendering parameters:
                - resolution: Output resolution for rasterized fallback (default: 1024)
                - style_overrides: Override default styling
                - include_labels: Whether to include text labels (default: True)
                - coordinate_precision: Decimal places for coordinates (default: 6)

        Returns:
            Dict containing ThreeJS-compatible geometry and styling data
        """
        if params is None:
            params = {}

        # Extract features and metadata
        features = data.get("features", [])
        bounds = data.get("bounds")
        crs = data.get("crs", "EPSG:4326")
        style_config = data.get("style", {})
        
        # Merge with parameter overrides
        style_config.update(params.get("style_overrides", {}))
        
        # Set defaults
        resolution = params.get("resolution", 1024)
        include_labels = params.get("include_labels", True)
        coord_precision = params.get("coordinate_precision", 6)

        # Calculate bounds if not provided
        if bounds is None:
            bounds = self._calculate_bounds(features)

        # Process features into ThreeJS format
        processed_features = []
        for feature in features:
            processed_feature = self._process_feature(
                feature, style_config, coord_precision, include_labels
            )
            if processed_feature:
                processed_features.append(processed_feature)

        # Create the ThreeJS-compatible output
        result = {
            "type": "geojson_threejs",
            "features": processed_features,
            "bounds": bounds,
            "crs": crs,
            "metadata": {
                "feature_count": len(processed_features),
                "bounds": bounds,
                "coordinate_system": crs,
                "has_labels": include_labels,
            }
        }

        return result

    def _calculate_bounds(self, features: List[Dict[str, Any]]) -> List[float]:
        """Calculate bounding box from GeoJSON features."""
        min_lon, min_lat = float('inf'), float('inf')
        max_lon, max_lat = float('-inf'), float('-inf')

        for feature in features:
            geom = shape(feature.get("geometry", {}))
            bounds = geom.bounds  # (minx, miny, maxx, maxy)
            
            min_lon = min(min_lon, bounds[0])
            min_lat = min(min_lat, bounds[1])
            max_lon = max(max_lon, bounds[2])
            max_lat = max(max_lat, bounds[3])

        return [min_lon, min_lat, max_lon, max_lat]

    def _process_feature(
        self, 
        feature: Dict[str, Any], 
        style_config: Dict[str, Any],
        coord_precision: int,
        include_labels: bool
    ) -> Optional[Dict[str, Any]]:
        """Process a single GeoJSON feature into ThreeJS format."""
        geometry = feature.get("geometry", {})
        properties = feature.get("properties", {})
        
        if not geometry:
            return None

        geom_type = geometry.get("type")
        coordinates = geometry.get("coordinates", [])

        # Convert shapely geometry for easier processing
        try:
            geom = shape(geometry)
        except Exception:
            return None

        # Determine styling based on geometry type and properties
        style = self._get_feature_style(geom_type, properties, style_config)

        # Process coordinates based on geometry type
        processed_geom = None
        
        if geom_type in ["Polygon", "MultiPolygon"]:
            processed_geom = self._process_polygon(geom, coord_precision)
        elif geom_type in ["LineString", "MultiLineString"]:
            processed_geom = self._process_linestring(geom, coord_precision)
        elif geom_type in ["Point", "MultiPoint"]:
            processed_geom = self._process_point(geom, coord_precision)

        if not processed_geom:
            return None

        # Create the processed feature
        result = {
            "type": geom_type,
            "geometry": processed_geom,
            "properties": properties,
            "style": style,
        }

        # Add text labels if requested and available
        if include_labels and properties:
            label_text = self._extract_label_text(properties)
            if label_text:
                label_position = self._get_label_position(geom)
                result["label"] = {
                    "text": label_text,
                    "position": [
                        round(label_position[0], coord_precision),
                        round(label_position[1], coord_precision)
                    ],
                    "style": style.get("label", {})
                }

        return result

    def _process_polygon(self, geom: Polygon, precision: int) -> Dict[str, Any]:
        """Process polygon geometry for ThreeJS."""
        if isinstance(geom, MultiPolygon):
            # Handle MultiPolygon by processing each polygon
            polygons = []
            for poly in geom.geoms:
                polygons.append(self._polygon_to_coords(poly, precision))
            return {"type": "MultiPolygon", "coordinates": polygons}
        else:
            return {"type": "Polygon", "coordinates": self._polygon_to_coords(geom, precision)}

    def _polygon_to_coords(self, poly: Polygon, precision: int) -> List[List[List[float]]]:
        """Convert Polygon to coordinate arrays."""
        # Exterior ring
        exterior = [[round(x, precision), round(y, precision)] 
                   for x, y in poly.exterior.coords]
        
        # Interior rings (holes)
        interiors = []
        for interior in poly.interiors:
            interior_coords = [[round(x, precision), round(y, precision)] 
                             for x, y in interior.coords]
            interiors.append(interior_coords)
        
        return [exterior] + interiors

    def _process_linestring(self, geom: LineString, precision: int) -> Dict[str, Any]:
        """Process linestring geometry for ThreeJS."""
        coordinates = [[round(x, precision), round(y, precision)] 
                      for x, y in geom.coords]
        return {"type": "LineString", "coordinates": coordinates}

    def _process_point(self, geom: Point, precision: int) -> Dict[str, Any]:
        """Process point geometry for ThreeJS."""
        return {
            "type": "Point", 
            "coordinates": [round(geom.x, precision), round(geom.y, precision)]
        }

    def _get_feature_style(
        self, 
        geom_type: str, 
        properties: Dict[str, Any], 
        style_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine styling for a feature based on its type and properties."""
        # Default styles by geometry type
        default_styles = {
            "Polygon": {
                "fill": True,
                "fillColor": "#3388ff",
                "fillOpacity": 0.2,
                "stroke": True,
                "color": "#3388ff",
                "weight": 2,
                "opacity": 1.0
            },
            "MultiPolygon": {
                "fill": True,
                "fillColor": "#3388ff", 
                "fillOpacity": 0.2,
                "stroke": True,
                "color": "#3388ff",
                "weight": 2,
                "opacity": 1.0
            },
            "LineString": {
                "stroke": True,
                "color": "#3388ff",
                "weight": 3,
                "opacity": 1.0
            },
            "MultiLineString": {
                "stroke": True,
                "color": "#3388ff",
                "weight": 3,
                "opacity": 1.0
            },
            "Point": {
                "radius": 5,
                "fillColor": "#3388ff",
                "color": "#ffffff",
                "weight": 2,
                "opacity": 1.0,
                "fillOpacity": 0.8
            },
            "MultiPoint": {
                "radius": 5,
                "fillColor": "#3388ff",
                "color": "#ffffff", 
                "weight": 2,
                "opacity": 1.0,
                "fillOpacity": 0.8
            }
        }

        # Start with default style for geometry type
        style = default_styles.get(geom_type, {}).copy()

        # Apply global style overrides
        if "default" in style_config:
            style.update(style_config["default"])

        # Apply geometry-type specific overrides
        geom_style_key = geom_type.lower()
        if geom_style_key in style_config:
            style.update(style_config[geom_style_key])

        # Apply property-based styling
        if "property_styles" in style_config:
            for prop_name, prop_styles in style_config["property_styles"].items():
                if prop_name in properties:
                    prop_value = properties[prop_name]
                    if prop_value in prop_styles:
                        style.update(prop_styles[prop_value])

        # Add label styling
        style["label"] = {
            "fontSize": 12,
            "fontFamily": "Arial, sans-serif",
            "color": "#000000",
            "backgroundColor": "#ffffff",
            "padding": 2,
            "borderRadius": 3,
            **style_config.get("label", {})
        }

        return style

    def _extract_label_text(self, properties: Dict[str, Any]) -> Optional[str]:
        """Extract text for labeling from feature properties."""
        # Common property names for labels
        label_fields = [
            "name", "label", "title", "text", "description", 
            "id", "risk_level", "category", "type", "alert_type"
        ]
        
        for field in label_fields:
            if field in properties and properties[field]:
                return str(properties[field])
        
        return None

    def _get_label_position(self, geom) -> Tuple[float, float]:
        """Get the best position for placing a label on the geometry."""
        if hasattr(geom, 'centroid'):
            centroid = geom.centroid
            return (centroid.x, centroid.y)
        elif hasattr(geom, 'coords'):
            # For LineString, use midpoint
            coords = list(geom.coords)
            mid_idx = len(coords) // 2
            return coords[mid_idx]
        else:
            # Fallback to bounds center
            bounds = geom.bounds
            return ((bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2)


@ThreeJSRenderer.register  
class GeoJSONToRasterRenderer(ThreeJSRenderer):
    """
    Render GeoJSON data as a rasterized texture for ThreeJS.
    
    This renderer converts vector GeoJSON data into a raster format
    for cases where vector rendering is not suitable or for fallback compatibility.
    """

    def render(
        self, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Render GeoJSON data as a rasterized texture.

        Args:
            data: Data dictionary containing GeoJSON features
            params: Optional rendering parameters:
                - resolution: Output resolution (default: 1024)
                - background_color: Background color (default: transparent)
                - antialias: Enable antialiasing (default: True)

        Returns:
            Dict containing rasterized texture data compatible with flat_overlay renderers
        """
        if params is None:
            params = {}

        try:
            from rasterio.features import rasterize
            from rasterio.transform import from_bounds
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            from matplotlib.collections import PatchCollection
            import io
            from PIL import Image
        except ImportError as e:
            raise ImportError(
                f"Required dependencies not available for rasterization: {e}. "
                "Install with: pip install rasterio matplotlib pillow"
            )

        # Extract parameters
        resolution = params.get("resolution", 1024)
        background_color = params.get("background_color", (0, 0, 0, 0))  # Transparent
        antialias = params.get("antialias", True)

        # Get data
        features = data.get("features", [])
        bounds = data.get("bounds")
        
        if bounds is None:
            bounds = self._calculate_bounds(features)

        # Create rasterized version
        west, south, east, north = bounds
        width = height = resolution

        # Create matplotlib figure
        fig, ax = plt.subplots(1, 1, figsize=(10, 10), dpi=resolution/10)
        ax.set_xlim(west, east)
        ax.set_ylim(south, north)
        ax.set_aspect('equal')
        ax.axis('off')
        
        if background_color[3] > 0:  # If not transparent
            fig.patch.set_facecolor(background_color[:3])
            ax.set_facecolor(background_color[:3])

        # Render features
        for feature in features:
            self._render_feature_to_matplotlib(feature, ax, data.get("style", {}))

        # Convert to PNG bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, 
                   transparent=(background_color[3] == 0), dpi=resolution/10)
        buf.seek(0)
        plt.close(fig)

        # Convert to numpy array
        img = Image.open(buf)
        img_array = np.array(img)

        # Ensure RGBA format
        if img_array.ndim == 2:  # Grayscale
            img_array = np.stack([img_array] * 3 + [np.full_like(img_array, 255)], axis=-1)
        elif img_array.shape[2] == 3:  # RGB
            alpha = np.full((img_array.shape[0], img_array.shape[1], 1), 255, dtype=img_array.dtype)
            img_array = np.concatenate([img_array, alpha], axis=-1)

        return {
            "type": "geojson_raster",
            "texture": img_array.tolist(),
            "array_shape": img_array.shape,
            "bounds": bounds,
            "resolution": resolution,
            "features": features,  # Keep original vector data
            "metadata": {
                "rasterized": True,
                "original_type": "geojson_data",
                "feature_count": len(features)
            }
        }

    def _render_feature_to_matplotlib(self, feature: Dict[str, Any], ax, style_config: Dict[str, Any]):
        """Render a single feature to matplotlib axes."""
        geometry = feature.get("geometry", {})
        properties = feature.get("properties", {})
        
        try:
            geom = shape(geometry)
        except Exception:
            return

        # Get styling
        geom_type = geometry.get("type")
        style = self._get_matplotlib_style(geom_type, properties, style_config)

        # Render based on geometry type
        if geom_type in ["Polygon", "MultiPolygon"]:
            self._render_polygon_matplotlib(geom, ax, style)
        elif geom_type in ["LineString", "MultiLineString"]:
            self._render_linestring_matplotlib(geom, ax, style)
        elif geom_type in ["Point", "MultiPoint"]:
            self._render_point_matplotlib(geom, ax, style)

    def _render_polygon_matplotlib(self, geom, ax, style):
        """Render polygon to matplotlib."""
        from matplotlib.patches import Polygon as MPLPolygon
        
        if hasattr(geom, 'geoms'):  # MultiPolygon
            for poly in geom.geoms:
                self._add_polygon_patch(poly, ax, style)
        else:  # Single Polygon
            self._add_polygon_patch(geom, ax, style)

    def _add_polygon_patch(self, poly, ax, style):
        """Add a single polygon patch to matplotlib axes."""
        from matplotlib.patches import Polygon as MPLPolygon
        
        # Exterior coordinates
        exterior_coords = list(poly.exterior.coords)
        
        patch = MPLPolygon(
            exterior_coords,
            closed=True,
            facecolor=style.get("fillColor", "#3388ff"),
            edgecolor=style.get("color", "#3388ff"),
            alpha=style.get("fillOpacity", 0.2),
            linewidth=style.get("weight", 2)
        )
        ax.add_patch(patch)

    def _render_linestring_matplotlib(self, geom, ax, style):
        """Render linestring to matplotlib."""
        coords = list(geom.coords)
        x_coords = [coord[0] for coord in coords]
        y_coords = [coord[1] for coord in coords]
        
        ax.plot(
            x_coords, y_coords,
            color=style.get("color", "#3388ff"),
            linewidth=style.get("weight", 3),
            alpha=style.get("opacity", 1.0)
        )

    def _render_point_matplotlib(self, geom, ax, style):
        """Render point to matplotlib."""
        if hasattr(geom, 'geoms'):  # MultiPoint
            for point in geom.geoms:
                ax.scatter(
                    point.x, point.y,
                    s=style.get("radius", 5) ** 2,
                    c=style.get("fillColor", "#3388ff"),
                    edgecolors=style.get("color", "#ffffff"),
                    linewidth=style.get("weight", 2),
                    alpha=style.get("fillOpacity", 0.8)
                )
        else:  # Single Point
            ax.scatter(
                geom.x, geom.y,
                s=style.get("radius", 5) ** 2,
                c=style.get("fillColor", "#3388ff"),
                edgecolors=style.get("color", "#ffffff"),
                linewidth=style.get("weight", 2),
                alpha=style.get("fillOpacity", 0.8)
            )

    def _get_matplotlib_style(self, geom_type: str, properties: Dict[str, Any], style_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get matplotlib-compatible styling."""
        # Use the same style logic as the vector renderer
        renderer = GeoJSONRenderer()
        return renderer._get_feature_style(geom_type, properties, style_config)

    def _calculate_bounds(self, features: List[Dict[str, Any]]) -> List[float]:
        """Calculate bounding box from GeoJSON features."""
        renderer = GeoJSONRenderer()
        return renderer._calculate_bounds(features)
