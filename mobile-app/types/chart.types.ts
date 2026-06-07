export interface LocationInfo {
  city: string;
  country: string;
  latitude: number;
  longitude: number;
  timezone: string;
}

export interface ChartInfo {
  name: string;
  birth_date: string;
  birth_time: string;
  birth_place: string;
  house_system: string;
  julian_day: number;
  location: LocationInfo;
}

export interface PlanetPosition {
  name: string;
  name_en: string;
  symbol: string;
  longitude: number;
  latitude: number;
  distance: number;
  speed: number;
  speed_display?: string;
  sign: string;
  sign_en: string;
  sign_symbol: string;
  degree_in_sign: number;
  degree_display?: string;
  house: number;
  retrograde: boolean;
  dignity: string;
}

export interface HouseInfo {
  number: number;
  name: string;
  cusp_longitude: number;
  sign: string;
  sign_en?: string;
  sign_symbol: string;
  degree_in_sign: number;
  degree_display: string;
}

export interface AspectInfo {
  planet1: string;
  planet2: string;
  aspect: string;
  aspect_en: string;
  aspect_symbol: string;
  orb: number;
  angle: number;
  nature: string;
}

export interface ElementBalance {
  fire: number;
  earth: number;
  air: number;
  water: number;
}

export interface QualityBalance {
  cardinal: number;
  fixed: number;
  mutable: number;
}

export interface EssentialDignityRow {
  planet: string;
  planet_en: string;
  ruler: string[];
  exaltation: string[];
  triplicity: string[];
  term: string[];
  face: string[];
  detriment: string[];
  fall: string[];
  score: number;
}

export interface EssentialDignitiesTable {
  rows: EssentialDignityRow[];
  total_score: number;
}

export interface BirthChartData {
  chart_info: ChartInfo;
  planets: PlanetPosition[];
  houses: HouseInfo[];
  aspects: AspectInfo[];
  elements: ElementBalance;
  qualities: QualityBalance;
  dignities: EssentialDignitiesTable;
}

export interface BirthChartResponse {
  success: boolean;
  chart_id: string;
  chart_data: BirthChartData;
  generated_at: string;
}

export interface InterpretationResponse {
  success: boolean;
  chart_id: string;
  interpretation: string;
  interpretation_style: string;
  language: string;
  generated_at: string;
}

// Transit types — alan adları backend API (response.py) ile birebir eşleşir
export interface TransitPlanet {
  name_tr: string;
  name_en: string;
  symbol: string;
  sign_tr: string;        // backend: sign_tr (Türkçe burç adı)
  sign_en: string;        // backend: sign_en (İngilizce burç adı)
  degree_display: string; // backend: degree_display ("8°57'")
  speed: number;
  speed_display: string;
  retrograde: boolean;
  house: number;
  // frontend-only convenience (backend göndermiyor)
  longitude?: number;
}

export interface TransitAspect {
  transit_planet_tr: string;   // backend: transit_planet_tr
  transit_planet_en: string;   // backend: transit_planet_en
  natal_planet_tr: string;     // backend: natal_planet_tr
  natal_planet_en: string;     // backend: natal_planet_en
  aspect_tr: string;           // backend: aspect_tr (Türkçe açı adı, örn "Kare")
  aspect_en: string;           // backend: aspect_en
  aspect_symbol: string;       // backend: aspect_symbol
  angle: number;               // backend: angle (60, 90, 120 vb.)
  orb: number;
  applying: boolean;
  nature: string;              // "harmonious" | "challenging" | "neutral"
}

export interface TransitChartResponse {
  success: boolean;
  transit_id: string;
  natal_chart_id: string;
  transit_date: string;
  transit_time: string;
  transit_planets: TransitPlanet[];
  transit_aspects: TransitAspect[];
  generated_at: string;
}

export interface TransitInterpretationResponse {
  success: boolean;
  transit_id: string;
  natal_chart_id: string;
  transit_date: string;
  interpretation: string;
  language: string;
  generated_at: string;
}
