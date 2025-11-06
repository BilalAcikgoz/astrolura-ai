# -*- coding: utf-8 -*-
"""
SVG Birth Chart Visualization Generator

Creates professional astrological birth charts in SVG format with:
- Zodiac wheel with 12 signs
- House divisions (Placidus or other systems)
- Planet positions with symbols
- Aspect lines between planets
- Degree markings
- Color-coded elements
"""

import math
from typing import List, Tuple, Optional
import svgwrite
from svgwrite import Drawing
from svgwrite.shapes import Circle, Line, Polygon
from svgwrite.text import Text
from svgwrite.path import Path

from app.api.models.response import BirthChartData, PlanetPosition, HouseInfo, AspectInfo


# Chart dimensions
CHART_SIZE = 800
CENTER_X = CHART_SIZE // 2
CENTER_Y = CHART_SIZE // 2

# Radii for different chart elements
RADIUS_OUTER = 380          # Outer edge of zodiac ring
RADIUS_ZODIAC_INNER = 330   # Inner edge of zodiac ring
RADIUS_DEGREE = 320         # Degree markings
RADIUS_HOUSES_OUTER = 310   # Outer edge of houses
RADIUS_HOUSES_INNER = 120   # Inner edge of houses (planet ring)
RADIUS_PLANETS = 220        # Where planets are placed
RADIUS_ASPECTS = 100        # Inner circle for aspect lines

# Colors
COLOR_BACKGROUND = "#FFFFFF"
COLOR_ZODIAC_BORDER = "#333333"
COLOR_HOUSE_LINE = "#666666"
COLOR_DEGREE_LINE = "#AAAAAA"
COLOR_TEXT = "#000000"
COLOR_PLANET_TEXT = "#000000"

# Zodiac colors (by element)
ZODIAC_COLORS = {
    "ates": "#FF6B6B",      # Fire - Red
    "toprak": "#8BC34A",    # Earth - Green
    "hava": "#FFEB3B",      # Air - Yellow
    "su": "#2196F3",        # Water - Blue
}

# Planet colors
PLANET_COLORS = {
    "Sun": "#FFD700",       # Gold
    "Moon": "#C0C0C0",      # Silver
    "Mercury": "#FFA500",   # Orange
    "Venus": "#FF69B4",     # Pink
    "Mars": "#FF0000",      # Red
    "Jupiter": "#4169E1",   # Royal Blue
    "Saturn": "#8B4513",    # Brown
    "Uranus": "#00CED1",    # Turquoise
    "Neptune": "#9370DB",   # Purple
    "Pluto": "#8B0000",     # Dark Red
    "North Node": "#808080",# Gray
}

# Aspect colors
ASPECT_COLORS = {
    "uyumlu": "#4CAF50",        # Green - harmonious
    "zorlayici": "#F44336",     # Red - challenging
    "notr": "#9E9E9E",          # Gray - neutral
    "karmasik": "#FF9800",      # Orange - complex
    "hafif": "#03A9F4",         # Light Blue - minor
    "hafif zorlayici": "#FF5722" # Deep Orange - minor challenging
}

# Zodiac symbols (Unicode)
ZODIAC_SYMBOLS = {
    "Aries": "♈", "Taurus": "♉", "Gemini": "♊", "Cancer": "♋",
    "Leo": "♌", "Virgo": "♍", "Libra": "♎", "Scorpio": "♏",
    "Sagittarius": "♐", "Capricorn": "♑", "Aquarius": "♒", "Pisces": "♓"
}

# Planet symbols (Unicode)
PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅",
    "Neptune": "♆", "Pluto": "♇", "North Node": "☊"
}

# Element mapping for zodiac signs
ZODIAC_ELEMENTS = {
    "Aries": "ates", "Taurus": "toprak", "Gemini": "hava", "Cancer": "su",
    "Leo": "ates", "Virgo": "toprak", "Libra": "hava", "Scorpio": "su",
    "Sagittarius": "ates", "Capricorn": "toprak", "Aquarius": "hava", "Pisces": "su"
}


class BirthChartSVG:
    """Generate SVG birth chart visualization"""

    def __init__(self, chart_data: BirthChartData, language: str = "en"):
        """
        Initialize chart generator

        Args:
            chart_data: Birth chart calculation data
            language: Language for labels ("en" or "tr")
        """
        self.chart_data = chart_data
        self.language = language
        self.dwg = Drawing(size=(CHART_SIZE, CHART_SIZE))

    def generate(self) -> str:
        """
        Generate complete SVG birth chart

        Returns:
            SVG as string
        """
        # Add background
        self.dwg.add(self.dwg.rect(
            insert=(0, 0),
            size=(CHART_SIZE, CHART_SIZE),
            fill=COLOR_BACKGROUND
        ))

        # Draw chart elements in order (back to front)
        self._draw_zodiac_wheel()
        self._draw_degree_markers()
        self._draw_houses()
        self._draw_aspects()
        self._draw_planets()
        self._draw_angles()
        self._draw_chart_info()

        return self.dwg.tostring()

    def _draw_zodiac_wheel(self):
        """Draw the outer zodiac wheel with 12 signs"""
        # Draw each zodiac sign section
        for i in range(12):
            # Calculate angles (starting from Aries at 0�, counterclockwise)
            start_angle = i * 30
            end_angle = (i + 1) * 30

            # Get zodiac sign info
            sign_name = list(ZODIAC_SYMBOLS.keys())[i]
            element = ZODIAC_ELEMENTS[sign_name]
            color = ZODIAC_COLORS[element]

            # Draw zodiac section (arc segment)
            path_data = self._create_arc_path(
                CENTER_X, CENTER_Y,
                RADIUS_ZODIAC_INNER, RADIUS_OUTER,
                start_angle, end_angle
            )

            self.dwg.add(Path(
                d=path_data,
                fill=color,
                fill_opacity=0.2,
                stroke=COLOR_ZODIAC_BORDER,
                stroke_width=1
            ))

            # Add zodiac symbol in the middle of the section
            mid_angle = start_angle + 15
            symbol_radius = (RADIUS_ZODIAC_INNER + RADIUS_OUTER) / 2
            sx, sy = self._polar_to_cartesian(CENTER_X, CENTER_Y, symbol_radius, mid_angle)

            self.dwg.add(Text(
                ZODIAC_SYMBOLS[sign_name],
                insert=(sx, sy),
                text_anchor="middle",
                dominant_baseline="middle",
                font_size="24px",
                font_weight="bold",
                fill=COLOR_TEXT
            ))

    def _draw_degree_markers(self):
        """Draw degree markers around the chart"""
        # Draw major degree lines (every 5�)
        for degree in range(0, 360, 5):
            if degree % 30 == 0:
                # Skip zodiac boundaries (already drawn)
                continue

            angle = degree
            x1, y1 = self._polar_to_cartesian(CENTER_X, CENTER_Y, RADIUS_ZODIAC_INNER, angle)

            if degree % 10 == 0:
                # Longer line for every 10�
                x2, y2 = self._polar_to_cartesian(CENTER_X, CENTER_Y, RADIUS_ZODIAC_INNER - 10, angle)
                width = 1.5
            else:
                # Shorter line for every 5�
                x2, y2 = self._polar_to_cartesian(CENTER_X, CENTER_Y, RADIUS_ZODIAC_INNER - 5, angle)
                width = 1

            self.dwg.add(Line(
                start=(x1, y1),
                end=(x2, y2),
                stroke=COLOR_DEGREE_LINE,
                stroke_width=width
            ))

    def _draw_houses(self):
        """Draw house divisions"""
        # Draw house boundary lines
        for house in self.chart_data.houses:
            angle = 180 - house.cusp_longitude  # Convert to chart angle

            # Draw house cusp line
            x1, y1 = self._polar_to_cartesian(CENTER_X, CENTER_Y, RADIUS_HOUSES_INNER, angle)
            x2, y2 = self._polar_to_cartesian(CENTER_X, CENTER_Y, RADIUS_HOUSES_OUTER, angle)

            # Thicker line for angular houses (1, 4, 7, 10)
            line_width = 2.5 if house.number in [1, 4, 7, 10] else 1.5

            self.dwg.add(Line(
                start=(x1, y1),
                end=(x2, y2),
                stroke=COLOR_HOUSE_LINE,
                stroke_width=line_width
            ))

            # Add house number
            next_house = self.chart_data.houses[house.number % 12]
            mid_angle = angle + (180 - next_house.cusp_longitude - angle) / 2

            # Normalize angle
            while mid_angle < 0:
                mid_angle += 360
            while mid_angle >= 360:
                mid_angle -= 360

            text_radius = (RADIUS_HOUSES_INNER + RADIUS_HOUSES_OUTER) / 2
            tx, ty = self._polar_to_cartesian(CENTER_X, CENTER_Y, text_radius, mid_angle)

            self.dwg.add(Text(
                str(house.number),
                insert=(tx, ty),
                text_anchor="middle",
                dominant_baseline="middle",
                font_size="16px",
                font_weight="bold",
                fill=COLOR_HOUSE_LINE
            ))

    def _draw_aspects(self):
        """Draw aspect lines between planets"""
        # Only draw major aspects
        major_aspects = ["Kavusum", "Karsitlik", "Ucgen", "Kare", "Altigen",
                        "Conjunction", "Opposition", "Trine", "Square", "Sextile"]

        for aspect in self.chart_data.aspects:
            # Check if this is a major aspect
            if aspect.aspect not in major_aspects and aspect.aspect_en not in major_aspects:
                continue

            # Find planet positions
            planet1_pos = None
            planet2_pos = None

            for planet in self.chart_data.planets:
                name_to_check = planet.name if self.language == "tr" else planet.name_en
                if name_to_check == aspect.planet1 or planet.name == aspect.planet1:
                    planet1_pos = planet
                if name_to_check == aspect.planet2 or planet.name == aspect.planet2:
                    planet2_pos = planet

            if not planet1_pos or not planet2_pos:
                continue

            # Calculate positions on inner aspect circle
            angle1 = 180 - planet1_pos.longitude
            angle2 = 180 - planet2_pos.longitude

            x1, y1 = self._polar_to_cartesian(CENTER_X, CENTER_Y, RADIUS_ASPECTS, angle1)
            x2, y2 = self._polar_to_cartesian(CENTER_X, CENTER_Y, RADIUS_ASPECTS, angle2)

            # Get aspect color
            aspect_color = ASPECT_COLORS.get(aspect.nature, "#999999")

            # Draw aspect line
            self.dwg.add(Line(
                start=(x1, y1),
                end=(x2, y2),
                stroke=aspect_color,
                stroke_width=1,
                opacity=0.4
            ))

    def _draw_planets(self):
        """Draw planets on the chart"""
        # Track used positions to avoid overlaps
        used_positions = []

        for planet in self.chart_data.planets:
            # Calculate position
            angle = 180 - planet.longitude

            # Adjust position if too close to other planets
            adjusted_angle = self._adjust_planet_position(angle, used_positions)
            used_positions.append(adjusted_angle)

            # Get planet position
            px, py = self._polar_to_cartesian(CENTER_X, CENTER_Y, RADIUS_PLANETS, adjusted_angle)

            # Draw planet circle
            planet_color = PLANET_COLORS.get(planet.symbol, "#888888")
            self.dwg.add(Circle(
                center=(px, py),
                r=12,
                fill=planet_color,
                stroke=COLOR_PLANET_TEXT,
                stroke_width=1.5
            ))

            # Draw planet symbol
            symbol = PLANET_SYMBOLS.get(planet.symbol, planet.symbol[0])

            # Add retrograde marker if needed
            if planet.retrograde:
                symbol = symbol + " "

            self.dwg.add(Text(
                symbol,
                insert=(px, py),
                text_anchor="middle",
                dominant_baseline="middle",
                font_size="14px",
                font_weight="bold",
                fill=COLOR_BACKGROUND
            ))

            # Draw line from planet to zodiac degree
            lx, ly = self._polar_to_cartesian(CENTER_X, CENTER_Y, RADIUS_HOUSES_OUTER, angle)
            self.dwg.add(Line(
                start=(px, py),
                end=(lx, ly),
                stroke=planet_color,
                stroke_width=1,
                opacity=0.5,
                stroke_dasharray="2,2"
            ))

    def _draw_angles(self):
        """Draw Ascendant and Midheaven markers"""
        # Draw Ascendant (always at 1st house cusp)
        asc_angle = 180 - self.chart_data.ascendant.longitude
        self._draw_angle_marker(asc_angle, "ASC", "#FF0000")

        # Draw Midheaven (always at 10th house cusp)
        mc_angle = 180 - self.chart_data.midheaven.longitude
        self._draw_angle_marker(mc_angle, "MC", "#0000FF")

    def _draw_angle_marker(self, angle: float, label: str, color: str):
        """Draw a special marker for chart angles"""
        # Draw line from center to outer edge
        x1, y1 = self._polar_to_cartesian(CENTER_X, CENTER_Y, RADIUS_HOUSES_INNER, angle)
        x2, y2 = self._polar_to_cartesian(CENTER_X, CENTER_Y, RADIUS_HOUSES_OUTER + 20, angle)

        self.dwg.add(Line(
            start=(x1, y1),
            end=(x2, y2),
            stroke=color,
            stroke_width=3
        ))

        # Add label
        tx, ty = self._polar_to_cartesian(CENTER_X, CENTER_Y, RADIUS_HOUSES_OUTER + 35, angle)
        self.dwg.add(Text(
            label,
            insert=(tx, ty),
            text_anchor="middle",
            dominant_baseline="middle",
            font_size="12px",
            font_weight="bold",
            fill=color
        ))

    def _draw_chart_info(self):
        """Draw chart information (name, date, location)"""
        info = self.chart_data.chart_info

        # Title
        self.dwg.add(Text(
            info.name,
            insert=(CHART_SIZE // 2, 30),
            text_anchor="middle",
            font_size="20px",
            font_weight="bold",
            fill=COLOR_TEXT
        ))

        # Birth info
        birth_info = f"{info.birth_date} {info.birth_time}"
        self.dwg.add(Text(
            birth_info,
            insert=(CHART_SIZE // 2, 55),
            text_anchor="middle",
            font_size="14px",
            fill=COLOR_TEXT
        ))

        # Location
        location_info = f"{info.location.city}, {info.location.country}"
        self.dwg.add(Text(
            location_info,
            insert=(CHART_SIZE // 2, 75),
            text_anchor="middle",
            font_size="12px",
            fill=COLOR_TEXT
        ))

    def _create_arc_path(self, cx: float, cy: float, r_inner: float, r_outer: float,
                         start_angle: float, end_angle: float) -> str:
        """
        Create SVG path for an arc segment (ring section)

        Args:
            cx, cy: Center coordinates
            r_inner: Inner radius
            r_outer: Outer radius
            start_angle: Start angle in degrees
            end_angle: End angle in degrees

        Returns:
            SVG path data string
        """
        # Convert to radians for calculation
        start_outer_x, start_outer_y = self._polar_to_cartesian(cx, cy, r_outer, start_angle)
        end_outer_x, end_outer_y = self._polar_to_cartesian(cx, cy, r_outer, end_angle)
        start_inner_x, start_inner_y = self._polar_to_cartesian(cx, cy, r_inner, start_angle)
        end_inner_x, end_inner_y = self._polar_to_cartesian(cx, cy, r_inner, end_angle)

        # Large arc flag (1 if angle > 180°)
        large_arc = 1 if (end_angle - start_angle) > 180 else 0

        # Build path (use single line to avoid whitespace issues)
        path_data = (
            f"M {start_outer_x} {start_outer_y} "
            f"A {r_outer} {r_outer} 0 {large_arc} 1 {end_outer_x} {end_outer_y} "
            f"L {end_inner_x} {end_inner_y} "
            f"A {r_inner} {r_inner} 0 {large_arc} 0 {start_inner_x} {start_inner_y} "
            f"Z"
        )

        return path_data

    def _polar_to_cartesian(self, cx: float, cy: float, radius: float, angle_degrees: float) -> Tuple[float, float]:
        """
        Convert polar coordinates to Cartesian

        Args:
            cx, cy: Center point
            radius: Distance from center
            angle_degrees: Angle in degrees (0� = right, counter-clockwise)

        Returns:
            (x, y) coordinates
        """
        angle_radians = math.radians(angle_degrees)
        x = cx + radius * math.cos(angle_radians)
        y = cy - radius * math.sin(angle_radians)  # Negative because SVG Y increases downward
        return x, y

    def _adjust_planet_position(self, angle: float, used_positions: List[float],
                                min_separation: float = 8.0) -> float:
        """
        Adjust planet angle to avoid overlapping with other planets

        Args:
            angle: Desired angle
            used_positions: List of already used angles
            min_separation: Minimum angular separation in degrees

        Returns:
            Adjusted angle
        """
        if not used_positions:
            return angle

        # Check if position is too close to any used position
        for used_angle in used_positions:
            diff = abs(angle - used_angle)
            if diff > 180:
                diff = 360 - diff

            if diff < min_separation:
                # Try shifting slightly
                angle = used_angle + min_separation
                if angle >= 360:
                    angle -= 360

        return angle


def generate_birth_chart_svg(chart_data: BirthChartData, language: str = "en") -> str:
    """
    Generate SVG birth chart

    Args:
        chart_data: Birth chart calculation data
        language: Language for labels ("en" or "tr")

    Returns:
        SVG as string
    """
    generator = BirthChartSVG(chart_data, language)
    return generator.generate()
