# -*- coding: utf-8 -*-
import math
from typing import List, Tuple, Optional

from app.api.models import BirthChartData, PlanetPosition, HouseInfo, AspectInfo

# Color scheme matching the provided design
COLORS = {
    'background': '#1a1a2e',  # Dark blue-black
    'chart_bg': '#ffffff',     # White chart background
    'text': '#2d2d2d',         # Dark gray text
    'text_light': '#666666',   # Light gray text
    'house_lines': '#e0e0e0',  # Light gray for house divisions
    'zodiac_line': '#cccccc',  # Zodiac circle line
    
    # Aspect colors
    'conjunction': '#000000',   # Black
    'opposition': '#dc143c',    # Crimson red
    'trine': '#228b22',         # Forest green
    'square': '#dc143c',        # Crimson red
    'sextile': '#4169e1',       # Royal blue
    
    # Planet colors
    'sun': '#ff9500',
    'moon': '#a8a8a8',
    'mercury': '#ffcc00',
    'venus': '#ff69b4',
    'mars': '#ff0000',
    'jupiter': '#ff8c00',
    'saturn': '#8b4513',
    'uranus': '#00ced1',
    'neptune': '#0000ff',
    'pluto': '#8b008b',
}

# Planet symbols (Unicode)
PLANET_SYMBOLS = {
    'Sun': '☉',
    'Moon': '☽',
    'Mercury': '☿',
    'Venus': '♀',
    'Mars': '♂',
    'Jupiter': '♃',
    'Saturn': '♄',
    'Uranus': '♅',
    'Neptune': '♆',
    'Pluto': '♇',
}

# Zodiac symbols (Unicode)
ZODIAC_SYMBOLS = {
    'Aries': '♈',
    'Taurus': '♉',
    'Gemini': '♊',
    'Cancer': '♋',
    'Leo': '♌',
    'Virgo': '♍',
    'Libra': '♎',
    'Scorpio': '♏',
    'Sagittarius': '♐',
    'Capricorn': '♑',
    'Aquarius': '♒',
    'Pisces': '♓',
}

class BirthChartSVG:    
    def __init__(self, chart_data: BirthChartData, language: str = "en"):
        self.chart_data = chart_data
        self.language = language
        
        # Canvas dimensions
        self.width = 1200
        self.height = 900
        
        # Chart wheel dimensions
        self.center_x = 450
        self.center_y = 450
        self.outer_radius = 380
        self.zodiac_radius = 350
        self.inner_radius = 300
        self.planet_radius = 250
        self.aspect_radius = 200
        
        # Info panel
        self.panel_x = 920
        self.panel_y = 50
        
    def generate(self) -> str:
        svg_parts = []
        
        # SVG header
        svg_parts.append(f'''<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">''')
        
        # Background
        svg_parts.append(f'<rect width="{self.width}" height="{self.height}" fill="{COLORS["background"]}"/>')
        
        # Main chart circle (white background)
        svg_parts.append(f'<circle cx="{self.center_x}" cy="{self.center_y}" r="{self.outer_radius}" fill="{COLORS["chart_bg"]}" stroke="{COLORS["zodiac_line"]}" stroke-width="2"/>')
        
        # Draw components in order (back to front)
        svg_parts.append(self._draw_aspects())
        svg_parts.append(self._draw_houses())
        svg_parts.append(self._draw_zodiac_ring())
        svg_parts.append(self._draw_planets())
        svg_parts.append(self._draw_center_point())
        svg_parts.append(self._draw_info_panel())
        
        # Close SVG
        svg_parts.append('</svg>')
        
        return ''.join(svg_parts)
    
    def _draw_zodiac_ring(self) -> str:
        # Draw outer zodiac ring with symbols
        svg = []
        
        # Zodiac circle
        svg.append(f'<circle cx="{self.center_x}" cy="{self.center_y}" r="{self.zodiac_radius}" fill="none" stroke="{COLORS["zodiac_line"]}" stroke-width="1.5"/>')
        
        # Draw 12 zodiac signs
        zodiac_signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                       'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        
        for i, sign in enumerate(zodiac_signs):
            # Each sign occupies 30 degrees
            angle_start = i * 30
            angle_mid = angle_start + 15
            
            # Draw division line
            x1, y1 = self._polar_to_cartesian(self.zodiac_radius, angle_start)
            x2, y2 = self._polar_to_cartesian(self.outer_radius, angle_start)
            svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{COLORS["house_lines"]}" stroke-width="1"/>')
            
            # Place zodiac symbol
            symbol_x, symbol_y = self._polar_to_cartesian(self.zodiac_radius + 20, angle_mid)
            svg.append(f'<text x="{symbol_x}" y="{symbol_y}" text-anchor="middle" dominant-baseline="middle" font-size="24" fill="{COLORS["text"]}">{ZODIAC_SYMBOLS.get(sign, sign[:2])}</text>')
        
        return ''.join(svg)
    
    def _draw_houses(self) -> str:
        # Draw house divisions
        svg = []
        
        # Inner circle for houses
        svg.append(f'<circle cx="{self.center_x}" cy="{self.center_y}" r="{self.inner_radius}" fill="none" stroke="{COLORS["house_lines"]}" stroke-width="1"/>')
        
        # Draw house cusps
        for house in self.chart_data.houses:
            angle = house.cusp_longitude
            
            # Draw house line
            x1, y1 = self._polar_to_cartesian(self.inner_radius, angle)
            x2, y2 = self._polar_to_cartesian(self.aspect_radius, angle)
            
            # Thicker line for cardinal houses (1, 4, 7, 10)
            stroke_width = "2" if house.number in [1, 4, 7, 10] else "1"
            svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{COLORS["house_lines"]}" stroke-width="{stroke_width}"/>')
            
            # House number
            mid_angle = (angle + self.chart_data.houses[(house.number) % 12].cusp_longitude) / 2
            if house.number == 12:
                mid_angle = (angle + self.chart_data.houses[0].cusp_longitude + 360) / 2
            
            text_x, text_y = self._polar_to_cartesian(self.inner_radius - 20, mid_angle)
            svg.append(f'<text x="{text_x}" y="{text_y}" text-anchor="middle" dominant-baseline="middle" font-size="14" font-weight="bold" fill="{COLORS["text_light"]}">{house.number}</text>')
        
        return ''.join(svg)
    
    def _draw_planets(self) -> str:
        # Draw planets on the chart
        svg = []
        
        for planet in self.chart_data.planets:
            angle = planet.longitude
            
            # Planet position
            px, py = self._polar_to_cartesian(self.planet_radius, angle)
            
            # Get planet symbol
            symbol = PLANET_SYMBOLS.get(planet.name_en, planet.symbol)
            
            # Get planet color
            color = COLORS.get(planet.name_en.lower(), COLORS['text'])
            
            # Draw planet symbol
            svg.append(f'<circle cx="{px}" cy="{py}" r="16" fill="white" stroke="{color}" stroke-width="2"/>')
            svg.append(f'<text x="{px}" y="{py}" text-anchor="middle" dominant-baseline="middle" font-size="18" font-weight="bold" fill="{color}">{symbol}</text>')
            
            # Draw degree marker (use degree_display if available, otherwise format degree_in_sign)
            degree_text = planet.degree_display if hasattr(planet, 'degree_display') else f"{planet.degree_in_sign:.0f}°"
            degree_x, degree_y = self._polar_to_cartesian(self.planet_radius - 35, angle)
            svg.append(f'<text x="{degree_x}" y="{degree_y}" text-anchor="middle" font-size="10" fill="{COLORS["text_light"]}">{degree_text}</text>')
            
            # Retrograde indicator
            if planet.retrograde:
                rx, ry = self._polar_to_cartesian(self.planet_radius + 25, angle)
                svg.append(f'<text x="{rx}" y="{ry}" text-anchor="middle" font-size="12" fill="{COLORS["text"]}" font-weight="bold">℞</text>')
        
        # Draw Ascendant and Midheaven
        # Find Ascendant and Midheaven from planets list
        ascendant = next((p for p in self.chart_data.planets if p.name_en == "Ascendant"), None)
        midheaven = next((p for p in self.chart_data.planets if p.name_en == "Midheaven"), None)

        if ascendant:
            # Ascendant (left point)
            asc_angle = ascendant.longitude
            asc_x1, asc_y1 = self._polar_to_cartesian(self.inner_radius, asc_angle)
            asc_x2, asc_y2 = self._polar_to_cartesian(self.zodiac_radius, asc_angle)
            svg.append(f'<line x1="{asc_x1}" y1="{asc_y1}" x2="{asc_x2}" y2="{asc_y2}" stroke="{COLORS["text"]}" stroke-width="3"/>')
            svg.append(f'<text x="{asc_x2 - 30}" y="{asc_y2}" font-size="16" font-weight="bold" fill="{COLORS["text"]}">ASC</text>')

        if midheaven:
            # Midheaven (top point)
            mc_angle = midheaven.longitude
            mc_x1, mc_y1 = self._polar_to_cartesian(self.inner_radius, mc_angle)
            mc_x2, mc_y2 = self._polar_to_cartesian(self.zodiac_radius, mc_angle)
            svg.append(f'<line x1="{mc_x1}" y1="{mc_y1}" x2="{mc_x2}" y2="{mc_y2}" stroke="{COLORS["text"]}" stroke-width="3"/>')
            svg.append(f'<text x="{mc_x2}" y="{mc_y2 - 10}" text-anchor="middle" font-size="16" font-weight="bold" fill="{COLORS["text"]}">MC</text>')
        
        return ''.join(svg)
    
    def _draw_aspects(self) -> str:
        # Draw aspect lines between planets
        svg = []
        
        for aspect in self.chart_data.aspects:
            # Find planets
            planet1 = next((p for p in self.chart_data.planets if p.name == aspect.planet1), None)
            planet2 = next((p for p in self.chart_data.planets if p.name == aspect.planet2), None)
            
            if not planet1 or not planet2:
                continue
            
            # Get positions
            x1, y1 = self._polar_to_cartesian(self.aspect_radius, planet1.longitude)
            x2, y2 = self._polar_to_cartesian(self.aspect_radius, planet2.longitude)
            
            # Get aspect color and style
            aspect_name = aspect.aspect_en.lower().replace(" ", "_")
            color = COLORS.get(aspect_name, COLORS['text_light'])
            
            # Line style based on nature
            if aspect.nature in ['uyumlu', 'harmonious']:
                stroke_dasharray = "none"
                opacity = "0.4"
            elif aspect.nature in ['zorlayici', 'challenging']:
                stroke_dasharray = "5,5"
                opacity = "0.6"
            else:
                stroke_dasharray = "2,2"
                opacity = "0.3"
            
            svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5" stroke-dasharray="{stroke_dasharray}" opacity="{opacity}"/>')
        
        return ''.join(svg)
    
    def _draw_center_point(self) -> str:
        # Draw center point of chart
        return f'<circle cx="{self.center_x}" cy="{self.center_y}" r="4" fill="{COLORS["text"]}"/>'
    
    def _draw_info_panel(self) -> str:
        # Draw information panel on the right side
        svg = []
        
        # Panel background
        svg.append(f'<rect x="{self.panel_x}" y="{self.panel_y}" width="260" height="800" fill="{COLORS["chart_bg"]}" stroke="{COLORS["zodiac_line"]}" stroke-width="2" rx="10"/>')
        
        y = self.panel_y + 30
        x = self.panel_x + 15
        
        # Name
        svg.append(f'<text x="{x}" y="{y}" font-size="20" font-weight="bold" fill="{COLORS["text"]}">{self.chart_data.chart_info.name}</text>')
        y += 30
        
        # Birth date and time
        svg.append(f'<text x="{x}" y="{y}" font-size="12" fill="{COLORS["text_light"]}">{self.chart_data.chart_info.birth_date} {self.chart_data.chart_info.birth_time}</text>')
        y += 20
        
        # Birth place
        location = self.chart_data.chart_info.location
        svg.append(f'<text x="{x}" y="{y}" font-size="12" fill="{COLORS["text_light"]}">{location.city}, {location.country}</text>')
        y += 15
        
        # Coordinates
        svg.append(f'<text x="{x}" y="{y}" font-size="10" fill="{COLORS["text_light"]}">Lat: {location.latitude:.2f} Lng: {location.longitude:.2f}</text>')
        y += 15
        
        # House system
        svg.append(f'<text x="{x}" y="{y}" font-size="10" fill="{COLORS["text_light"]}">Geocentric, Tropical</text>')
        y += 15
        svg.append(f'<text x="{x}" y="{y}" font-size="10" fill="{COLORS["text_light"]}">{self.chart_data.chart_info.house_system}</text>')
        y += 35
        
        # Divider
        svg.append(f'<line x1="{x}" y1="{y}" x2="{self.panel_x + 245}" y2="{y}" stroke="{COLORS["house_lines"]}" stroke-width="1"/>')
        y += 25
        
        # Planet list
        svg.append(f'<text x="{x}" y="{y}" font-size="14" font-weight="bold" fill="{COLORS["text"]}">Planets</text>')
        y += 20
        
        for planet in self.chart_data.planets[:10]:  # Main planets only
            symbol = PLANET_SYMBOLS.get(planet.name_en, planet.symbol)
            color = COLORS.get(planet.name_en.lower(), COLORS['text'])
            
            # Planet symbol
            svg.append(f'<text x="{x}" y="{y}" font-size="16" fill="{color}">{symbol}</text>')

            # Planet name and position (use degree_display if available)
            retro = " ℞" if planet.retrograde else ""
            sign_symbol = ZODIAC_SYMBOLS.get(planet.sign_en, planet.sign_en[:3])
            degree_text = planet.degree_display if hasattr(planet, 'degree_display') else f"{planet.degree_in_sign:.0f}°"
            svg.append(f'<text x="{x + 25}" y="{y}" font-size="11" fill="{COLORS["text"]}">{planet.name_en}: {sign_symbol} {degree_text}{retro}</text>')
            y += 18
        
        y += 15
        
        # Divider
        svg.append(f'<line x1="{x}" y1="{y}" x2="{self.panel_x + 245}" y2="{y}" stroke="{COLORS["house_lines"]}" stroke-width="1"/>')
        y += 25
        
        # Elements
        svg.append(f'<text x="{x}" y="{y}" font-size="14" font-weight="bold" fill="{COLORS["text"]}">Elements</text>')
        y += 20
        
        svg.append(f'<text x="{x}" y="{y}" font-size="11" fill="{COLORS["text"]}">Fire: {self.chart_data.elements.fire}%  Earth: {self.chart_data.elements.earth}%</text>')
        y += 15
        svg.append(f'<text x="{x}" y="{y}" font-size="11" fill="{COLORS["text"]}">Air: {self.chart_data.elements.air}%  Water: {self.chart_data.elements.water}%</text>')
        y += 25
        
        # Qualities
        svg.append(f'<text x="{x}" y="{y}" font-size="14" font-weight="bold" fill="{COLORS["text"]}">Qualities</text>')
        y += 20
        
        svg.append(f'<text x="{x}" y="{y}" font-size="11" fill="{COLORS["text"]}">Cardinal: {self.chart_data.qualities.cardinal}%</text>')
        y += 15
        svg.append(f'<text x="{x}" y="{y}" font-size="11" fill="{COLORS["text"]}">Fixed: {self.chart_data.qualities.fixed}%</text>')
        y += 15
        svg.append(f'<text x="{x}" y="{y}" font-size="11" fill="{COLORS["text"]}">Mutable: {self.chart_data.qualities.mutable}%</text>')
        
        return ''.join(svg)
    
    def _polar_to_cartesian(self, radius: float, angle_degrees: float) -> Tuple[float, float]:
        """
        Convert polar coordinates to Cartesian.
        In astrology: 0° = 9 o'clock position (left), moves counter-clockwise
        """
        # Convert to standard mathematical angle (0° = 3 o'clock, counter-clockwise)
        # Astrological 0° (Aries) starts at 9 o'clock (180° in math)
        angle_math = 180 - angle_degrees
        angle_rad = math.radians(angle_math)
        
        x = self.center_x + radius * math.cos(angle_rad)
        y = self.center_y - radius * math.sin(angle_rad)
        
        return round(x, 2), round(y, 2)


def generate_birth_chart_svg(chart_data: BirthChartData, language: str = "en") -> str:
    # Generate a professional birth chart SVG visualization.
    generator = BirthChartSVG(chart_data, language)
    return generator.generate()