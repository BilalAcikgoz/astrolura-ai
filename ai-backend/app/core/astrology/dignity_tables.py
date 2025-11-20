# -*- coding: utf-8 -*-
from typing import Optional, Dict, List

class TraditionalDignityTables:
    def __init__(self):
        # Rulership (Yönetici) - which planet rules which sign (+5 points)
        self.rulerships = {
            "Koc": "Mars",          # Aries
            "Boga": "Venus",        # Taurus  
            "Ikizler": "Merkur",    # Gemini
            "Yengec": "Ay",         # Cancer
            "Aslan": "Gunes",       # Leo
            "Basak": "Merkur",      # Virgo
            "Terazi": "Venus",      # Libra
            "Akrep": "Mars",        # Scorpio (traditional) / Pluto (modern)
            "Yay": "Jupiter",       # Sagittarius
            "Oglak": "Saturn",      # Capricorn
            "Kova": "Saturn",       # Aquarius (traditional) / Uranus (modern)
            "Balik": "Jupiter"      # Pisces (traditional) / Neptune (modern)
        }
        
        # Modern co-rulers
        self.modern_rulerships = {
            "Akrep": "Pluto",
            "Kova": "Uranus", 
            "Balik": "Neptun"
        }
        
        # Exaltation (Yücelme) - where planets are exalted (+4 points)
        self.exaltations = {
            "Gunes": "Koc",         # Sun exalted in Aries
            "Ay": "Boga",           # Moon exalted in Taurus
            "Merkur": "Basak",      # Mercury exalted in Virgo
            "Venus": "Balik",       # Venus exalted in Pisces
            "Mars": "Oglak",        # Mars exalted in Capricorn
            "Jupiter": "Yengec",    # Jupiter exalted in Cancer
            "Saturn": "Terazi",     # Saturn exalted in Libra
            # Modern planets (not traditionally used but included)
            "Uranus": "Akrep",      # Uranus exalted in Scorpio
            "Neptun": "Yengec",     # Neptune exalted in Cancer
            "Pluto": "Koc"          # Pluto exalted in Aries
        }
        
        # Detriment (Zarar/Sürgün) - opposite of rulership (-5 points)
        self.detriments = {
            "Gunes": "Kova",        # Sun in detriment in Aquarius
            "Ay": "Oglak",          # Moon in detriment in Capricorn
            "Merkur": ["Yay", "Balik"],  # Mercury in detriment in Sagittarius and Pisces
            "Venus": ["Koc", "Akrep"],   # Venus in detriment in Aries and Scorpio
            "Mars": ["Terazi", "Boga"],  # Mars in detriment in Libra and Taurus
            "Jupiter": ["Ikizler", "Basak"],  # Jupiter in detriment in Gemini and Virgo
            "Saturn": ["Yengec", "Aslan"],    # Saturn in detriment in Cancer and Leo
            "Uranus": "Aslan",      # Uranus in detriment in Leo
            "Neptun": "Basak",      # Neptune in detriment in Virgo
            "Pluto": "Boga"         # Pluto in detriment in Taurus
        }
        
        # Fall (Düşüş) - opposite of exaltation (-4 points)
        self.falls = {
            "Gunes": "Terazi",      # Sun in fall in Libra
            "Ay": "Akrep",          # Moon in fall in Scorpio
            "Merkur": "Balik",      # Mercury in fall in Pisces
            "Venus": "Basak",       # Venus in fall in Virgo
            "Mars": "Yengec",       # Mars in fall in Cancer
            "Jupiter": "Oglak",     # Jupiter in fall in Capricorn
            "Saturn": "Koc",        # Saturn in fall in Aries
            "Uranus": "Boga",       # Uranus in fall in Taurus
            "Neptun": "Oglak",      # Neptune in fall in Capricorn
            "Pluto": "Terazi"       # Pluto in fall in Libra
        }
        
        # Triplicity rulers by element (+3 points)
        # Day/Night rulers for each element (Traditional Ptolemaic system)
        self.triplicities = {
            "ates": {"day": "Gunes", "night": "Jupiter"},     # Fire signs
            "toprak": {"day": "Venus", "night": "Ay"},        # Earth signs
            "hava": {"day": "Saturn", "night": "Merkur"},     # Air signs
            "su": {"day": "Venus", "night": "Mars"}          # Water signs
        }
        
        # Element mapping for signs
        self.sign_elements = {
            "Koc": "ates", "Aslan": "ates", "Yay": "ates",
            "Boga": "toprak", "Basak": "toprak", "Oglak": "toprak",
            "Ikizler": "hava", "Terazi": "hava", "Kova": "hava",
            "Yengec": "su", "Akrep": "su", "Balik": "su"
        }
        
        # Terms (Hadde) - specific degree ranges ruled by planets (+2 points)
        # Each sign divided into 5 unequal parts
        self.terms = self._initialize_terms()
        
        # Faces/Decans - each sign divided into 3 equal 10-degree parts (+1 point)
        self.faces = self._initialize_faces()
    
    def _initialize_terms(self) -> Dict[str, List[tuple]]:
        """Initialize the terms table (Egyptian/Ptolemaic bounds)"""
        return {
            "Koc": [
                (0, 6, "Jupiter"),
                (6, 12, "Venus"),
                (12, 20, "Merkur"),
                (20, 25, "Mars"),
                (25, 30, "Saturn")
            ],
            "Boga": [
                (0, 8, "Venus"),
                (8, 14, "Merkur"),
                (14, 22, "Jupiter"),
                (22, 27, "Saturn"),
                (27, 30, "Mars")
            ],
            "Ikizler": [
                (0, 6, "Merkur"),
                (6, 12, "Jupiter"),
                (12, 17, "Venus"),
                (17, 24, "Mars"),
                (24, 30, "Saturn")
            ],
            "Yengec": [
                (0, 7, "Mars"),
                (7, 13, "Venus"),
                (13, 19, "Merkur"),
                (19, 26, "Jupiter"),
                (26, 30, "Saturn")
            ],
            "Aslan": [
                (0, 6, "Jupiter"),
                (6, 11, "Venus"),
                (11, 18, "Saturn"),
                (18, 24, "Merkur"),
                (24, 30, "Mars")
            ],
            "Basak": [
                (0, 7, "Merkur"),
                (7, 17, "Venus"),
                (17, 21, "Jupiter"),
                (21, 28, "Mars"),
                (28, 30, "Saturn")
            ],
            "Terazi": [
                (0, 6, "Saturn"),
                (6, 14, "Merkur"),
                (14, 21, "Jupiter"),
                (21, 28, "Venus"),
                (28, 30, "Mars")
            ],
            "Akrep": [
                (0, 7, "Mars"),
                (7, 11, "Venus"),
                (11, 19, "Merkur"),
                (19, 24, "Jupiter"),
                (24, 30, "Saturn")
            ],
            "Yay": [
                (0, 12, "Jupiter"),
                (12, 17, "Venus"),
                (17, 21, "Merkur"),
                (21, 26, "Saturn"),
                (26, 30, "Mars")
            ],
            "Oglak": [
                (0, 7, "Merkur"),
                (7, 14, "Jupiter"),
                (14, 22, "Venus"),
                (22, 26, "Saturn"),
                (26, 30, "Mars")
            ],
            "Kova": [
                (0, 8, "Merkur"),
                (8, 13, "Venus"),
                (13, 20, "Jupiter"),
                (20, 25, "Mars"),
                (25, 30, "Saturn")
            ],
            "Balik": [
                (0, 12, "Venus"),
                (12, 16, "Jupiter"),
                (16, 19, "Merkur"),
                (19, 28, "Mars"),
                (28, 30, "Saturn")
            ]
        }
    
    def _initialize_faces(self) -> Dict[str, List[tuple]]:
        """Initialize the faces/decans table"""
        # Chaldean decan system - follows the order of planets by speed
        planet_order = ["Mars", "Gunes", "Venus", "Merkur", "Ay", "Saturn", "Jupiter"]
        
        faces = {}
        planet_index = 0
        
        signs = ["Koc", "Boga", "Ikizler", "Yengec", "Aslan", "Basak", 
                 "Terazi", "Akrep", "Yay", "Oglak", "Kova", "Balik"]
        
        for sign in signs:
            sign_faces = []
            for decan in range(3):
                start = decan * 10
                end = start + 10
                ruler = planet_order[planet_index % 7]
                sign_faces.append((start, end, ruler))
                planet_index += 1
            faces[sign] = sign_faces

        # Specific correction for Terazi (Libra) first decan
        # Should be Sun (Gunes) instead of Moon (Ay)
        faces["Terazi"][0] = (0, 10, "Gunes")

        return faces
    
    def is_ruler(self, planet: str, sign: str) -> bool:
        """Check if planet rules the sign"""
        traditional_ruler = self.rulerships.get(sign) == planet
        modern_ruler = self.modern_rulerships.get(sign) == planet
        return traditional_ruler or modern_ruler
    
    def is_exalted(self, planet: str, sign: str) -> bool:
        """Check if planet is exalted in the sign"""
        return self.exaltations.get(planet) == sign
    
    def is_in_detriment(self, planet: str, sign: str) -> bool:
        """Check if planet is in detriment in the sign"""
        detriment = self.detriments.get(planet)
        if isinstance(detriment, list):
            return sign in detriment
        return detriment == sign
    
    def is_in_fall(self, planet: str, sign: str) -> bool:
        """Check if planet is in fall in the sign"""
        return self.falls.get(planet) == sign
    
    def get_triplicity_ruler(self, sign: str, is_day_chart: bool = True) -> Optional[str]:
        """Get the triplicity ruler for a sign"""
        element = self.sign_elements.get(sign)
        if element:
            triplicity = self.triplicities.get(element)
            if triplicity:
                return triplicity["day"] if is_day_chart else triplicity["night"]
        return None
    
    def get_term_ruler(self, sign: str, degree: float) -> Optional[str]:
        """Get the term ruler for a specific degree in a sign"""
        terms = self.terms.get(sign, [])
        for start, end, ruler in terms:
            if start <= degree < end:
                return ruler
        return None
    
    def get_face_ruler(self, sign: str, degree: float) -> Optional[str]:
        """Get the face/decan ruler for a specific degree in a sign"""
        faces = self.faces.get(sign, [])
        for start, end, ruler in faces:
            if start <= degree < end:
                return ruler
        return None


# Global instance
_dignity_tables: Optional[TraditionalDignityTables] = None

def get_traditional_dignities() -> TraditionalDignityTables:
    """Get or create the global dignity tables instance"""
    global _dignity_tables
    if _dignity_tables is None:
        _dignity_tables = TraditionalDignityTables()
    return _dignity_tables