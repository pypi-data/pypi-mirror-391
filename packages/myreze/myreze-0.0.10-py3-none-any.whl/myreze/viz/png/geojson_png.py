from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import json
import base64
import io
from shapely.geometry import shape, Point, LineString, Polygon, MultiPolygon


class GeoJSONPNGRenderer:
    """
    Render GeoJSON data as PNG images.
    
    This renderer converts GeoJSON features into PNG format for static visualization,
    web display, or embedding in documents.
    """

    def __init__(self):
        """Initialize the PNG renderer."""
        pass

    def render(
        self, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Render GeoJSON data as PNG.

        Args:
            data: Data dictionary containing GeoJSON features
            params: Optional rendering parameters:
                - width: Image width in pixels (default: 1024)
                - height: Image height in pixels (default: 1024)
                - background_color: Background color as (R,G,B,A) tuple (default: transparent)
                - dpi: Dots per inch for high-quality output (default: 150)
                - format: Output format - 'png' or 'base64' (default: 'base64')
                - include_labels: Whether to render text labels (default: True)
                - style_overrides: Override default styling

        Returns:
            Dict containing PNG data and metadata
        """
        if params is None:
            params = {}

        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            from matplotlib.collections import PatchCollection
            from PIL import Image, ImageDraw, ImageFont
        except ImportError as e:
            raise ImportError(
                f"Required dependencies not available for PNG rendering: {e}. "
                "Install with: pip install matplotlib pillow"
            )

        # Extract parameters
        width = params.get("width", 1024)
        height = params.get("height", 1024)
        background_color = params.get("background_color", (255, 255, 255, 0))  # Transparent white
        dpi = params.get("dpi", 150)
        output_format = params.get("format", "base64")
        include_labels = params.get("include_labels", True)
        style_overrides = params.get("style_overrides", {})

        # Get data
        features = data.get("features", [])
        bounds = data.get("bounds")
        style_config = data.get("style", {})
        style_config.update(style_overrides)
        
        if bounds is None:
            bounds = self._calculate_bounds(features)

        if not bounds or len(features) == 0:
            return self._create_empty_png(width, height, background_color, output_format)

        # Create the PNG using matplotlib
        png_data = self._render_matplotlib(
            features, bounds, style_config, width, height, 
            background_color, dpi, include_labels
        )

        # Prepare result
        result = {
            "type": "geojson_png",
            "png_data": png_data,
            "format": output_format,
            "dimensions": {"width": width, "height": height},
            "bounds": bounds,
            "metadata": {
                "feature_count": len(features),
                "has_labels": include_labels,
                "dpi": dpi,
                "background_transparent": background_color[3] == 0
            }
        }

        return result

    def _render_matplotlib(
        self, 
        features: List[Dict[str, Any]], 
        bounds: List[float],
        style_config: Dict[str, Any],
        width: int, 
        height: int,
        background_color: Tuple[int, int, int, int],
        dpi: int,
        include_labels: bool
    ) -> str:
        """Render using matplotlib and return PNG data."""
        import matplotlib.pyplot as plt
        from matplotlib.patches import Polygon as MPLPolygon
        
        west, south, east, north = bounds
        
        # Calculate figure size to match desired pixel dimensions
        fig_width = width / dpi
        fig_height = height / dpi
        
        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=(fig_width, fig_height), dpi=dpi)
        ax.set_xlim(west, east)
        ax.set_ylim(south, north)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Set background
        if background_color[3] > 0:  # If not transparent
            bg_color = tuple(c/255.0 for c in background_color[:3])
            fig.patch.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)

        # Render features
        labels_to_render = []
        for feature in features:
            label_info = self._render_feature_matplotlib(feature, ax, style_config)
            if include_labels and label_info:
                labels_to_render.append(label_info)

        # Render labels on top
        for label_info in labels_to_render:
            self._render_label_matplotlib(label_info, ax)

        # Convert to PNG bytes
        buf = io.BytesIO()
        plt.savefig(
            buf, 
            format='png', 
            bbox_inches='tight', 
            pad_inches=0,
            transparent=(background_color[3] == 0),
            dpi=dpi,
            facecolor='none' if background_color[3] == 0 else fig.get_facecolor()
        )
        buf.seek(0)
        plt.close(fig)

        # Convert to base64 string
        png_bytes = buf.getvalue()
        return base64.b64encode(png_bytes).decode('utf-8')

    def _render_feature_matplotlib(
        self, 
        feature: Dict[str, Any], 
        ax, 
        style_config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Render a single feature to matplotlib axes and return label info if any."""
        geometry = feature.get("geometry", {})
        properties = feature.get("properties", {})
        
        try:
            geom = shape(geometry)
        except Exception:
            return None

        # Get styling
        geom_type = geometry.get("type")
        style = self._get_feature_style(geom_type, properties, style_config)

        # Render based on geometry type
        if geom_type in ["Polygon", "MultiPolygon"]:
            self._render_polygon_matplotlib(geom, ax, style)
        elif geom_type in ["LineString", "MultiLineString"]:
            self._render_linestring_matplotlib(geom, ax, style)
        elif geom_type in ["Point", "MultiPoint"]:
            self._render_point_matplotlib(geom, ax, style)

        # Extract label information
        label_text = self._extract_label_text(properties)
        if label_text:
            label_position = self._get_label_position(geom)
            return {
                "text": label_text,
                "position": label_position,
                "style": style.get("label", {})
            }

        return None

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
        
        # Convert color strings to matplotlib format
        fill_color = self._color_to_mpl(style.get("fillColor", "#3388ff"))
        edge_color = self._color_to_mpl(style.get("color", "#3388ff"))
        
        patch = MPLPolygon(
            exterior_coords,
            closed=True,
            facecolor=fill_color,
            edgecolor=edge_color,
            alpha=style.get("fillOpacity", 0.2),
            linewidth=style.get("weight", 2)
        )
        ax.add_patch(patch)

        # Handle holes (interior rings)
        for interior in poly.interiors:
            interior_coords = list(interior.coords)
            hole_patch = MPLPolygon(
                interior_coords,
                closed=True,
                facecolor='white',  # Punch hole by using background color
                edgecolor=edge_color,
                alpha=1.0,
                linewidth=style.get("weight", 2)
            )
            ax.add_patch(hole_patch)

    def _render_linestring_matplotlib(self, geom, ax, style):
        """Render linestring to matplotlib."""
        if hasattr(geom, 'geoms'):  # MultiLineString
            for line in geom.geoms:
                self._plot_single_line(line, ax, style)
        else:  # Single LineString
            self._plot_single_line(geom, ax, style)

    def _plot_single_line(self, line, ax, style):
        """Plot a single linestring."""
        coords = list(line.coords)
        x_coords = [coord[0] for coord in coords]
        y_coords = [coord[1] for coord in coords]
        
        color = self._color_to_mpl(style.get("color", "#3388ff"))
        
        ax.plot(
            x_coords, y_coords,
            color=color,
            linewidth=style.get("weight", 3),
            alpha=style.get("opacity", 1.0),
            solid_capstyle='round',
            solid_joinstyle='round'
        )

    def _render_point_matplotlib(self, geom, ax, style):
        """Render point to matplotlib."""
        if hasattr(geom, 'geoms'):  # MultiPoint
            for point in geom.geoms:
                self._plot_single_point(point, ax, style)
        else:  # Single Point
            self._plot_single_point(geom, ax, style)

    def _plot_single_point(self, point, ax, style):
        """Plot a single point."""
        fill_color = self._color_to_mpl(style.get("fillColor", "#3388ff"))
        edge_color = self._color_to_mpl(style.get("color", "#ffffff"))
        
        ax.scatter(
            point.x, point.y,
            s=(style.get("radius", 5) * 2) ** 2,  # matplotlib uses area, not radius
            c=fill_color,
            edgecolors=edge_color,
            linewidth=style.get("weight", 2),
            alpha=style.get("fillOpacity", 0.8),
            zorder=10  # Ensure points are on top
        )

    def _render_label_matplotlib(self, label_info: Dict[str, Any], ax):
        """Render text label to matplotlib axes."""
        text = label_info["text"]
        position = label_info["position"]
        style = label_info["style"]
        
        # Extract text styling
        font_size = style.get("fontSize", 12)
        font_family = style.get("fontFamily", "Arial")
        text_color = self._color_to_mpl(style.get("color", "#000000"))
        bg_color = self._color_to_mpl(style.get("backgroundColor", "#ffffff"))
        
        # Add text with background
        text_obj = ax.text(
            position[0], position[1], text,
            fontsize=font_size,
            fontfamily=font_family,
            color=text_color,
            ha='center', va='center',
            bbox=dict(
                boxstyle=f"round,pad={style.get('padding', 2)}",
                facecolor=bg_color,
                edgecolor='none',
                alpha=0.8
            ),
            zorder=20  # Ensure labels are on top
        )

    def _color_to_mpl(self, color_str: str) -> str:
        """Convert color string to matplotlib-compatible format."""
        if color_str.startswith('#'):
            return color_str
        elif color_str.startswith('rgb'):
            # Handle rgb(r,g,b) or rgba(r,g,b,a) format
            # For simplicity, just return as-is (matplotlib can handle many formats)
            return color_str
        else:
            # Named colors
            return color_str

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
                "fillOpacity": 0.3,
                "stroke": True,
                "color": "#3388ff",
                "weight": 2,
                "opacity": 1.0
            },
            "MultiPolygon": {
                "fill": True,
                "fillColor": "#3388ff", 
                "fillOpacity": 0.3,
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
                "radius": 8,
                "fillColor": "#3388ff",
                "color": "#ffffff",
                "weight": 2,
                "opacity": 1.0,
                "fillOpacity": 0.8
            },
            "MultiPoint": {
                "radius": 8,
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

        # Apply property-based styling (e.g., color by risk level)
        if "property_styles" in style_config:
            for prop_name, prop_styles in style_config["property_styles"].items():
                if prop_name in properties:
                    prop_value = properties[prop_name]
                    if prop_value in prop_styles:
                        style.update(prop_styles[prop_value])

        # Add label styling
        style["label"] = {
            "fontSize": 10,
            "fontFamily": "Arial",
            "color": "#000000",
            "backgroundColor": "#ffffff",
            "padding": 3,
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

    def _calculate_bounds(self, features: List[Dict[str, Any]]) -> List[float]:
        """Calculate bounding box from GeoJSON features."""
        if not features:
            return [0, 0, 1, 1]  # Default bounds
            
        min_lon, min_lat = float('inf'), float('inf')
        max_lon, max_lat = float('-inf'), float('-inf')

        for feature in features:
            try:
                geom = shape(feature.get("geometry", {}))
                bounds = geom.bounds  # (minx, miny, maxx, maxy)
                
                min_lon = min(min_lon, bounds[0])
                min_lat = min(min_lat, bounds[1])
                max_lon = max(max_lon, bounds[2])
                max_lat = max(max_lat, bounds[3])
            except Exception:
                continue

        # Handle case where no valid geometries were found
        if min_lon == float('inf'):
            return [0, 0, 1, 1]

        return [min_lon, min_lat, max_lon, max_lat]

    def _create_empty_png(
        self, 
        width: int, 
        height: int, 
        background_color: Tuple[int, int, int, int],
        output_format: str
    ) -> Dict[str, Any]:
        """Create an empty PNG for cases with no features."""
        try:
            from PIL import Image
        except ImportError:
            raise ImportError("PIL (Pillow) is required for PNG generation")

        # Create empty image
        img = Image.new('RGBA', (width, height), background_color)
        
        # Convert to base64
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        png_data = base64.b64encode(buf.getvalue()).decode('utf-8')

        return {
            "type": "geojson_png",
            "png_data": png_data,
            "format": output_format,
            "dimensions": {"width": width, "height": height},
            "bounds": [0, 0, 1, 1],
            "metadata": {
                "feature_count": 0,
                "empty": True
            }
        }
