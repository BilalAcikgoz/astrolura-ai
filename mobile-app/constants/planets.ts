import { colors } from './colors';

// ─── İsim normalizasyonu ────────────────────────────────────────────────────
// Backend'den Türkçe isimler gelir; bunlar tabloda belirtilen kurallara göre
// görüntülük isimlerine dönüştürülür.
const NAME_MAP: Record<string, string> = {
  // Düğümler & özel noktalar
  'Kuzey Düğüm': 'Kad',
  'Kuzey Düğümü': 'Kad',
  'Kuzey dugum': 'Kad',
  'North Node': 'Kad',
  'Güney Düğüm': 'Gad',
  'Güney Düğümü': 'Gad',
  'Güney dugum': 'Gad',
  'South Node': 'Gad',
  // Ascendant / Midheaven
  'Yükselen': 'Ascendant',
  'Ascendant': 'Ascendant',
  'AC': 'Ascendant',
  'Orta Gök': 'Midheaven',
  'MC': 'Midheaven',
  'Midheaven': 'Midheaven',
  // Pluto
  'Plüton': 'Pluto',
  'Pluton': 'Pluto',
  'Pluto': 'Pluto',
};

/** Backend'den gelen ham gezegen adını görüntülük ada dönüştürür. */
export function normalizePlanetName(raw: string): string {
  return NAME_MAP[raw] ?? raw;
}

// ─── Renkler ────────────────────────────────────────────────────────────────
export const PLANET_COLORS: Record<string, string> = {
  // Türkçe
  'Güneş':       '#F59E0B',
  'Ay':          '#C0C0C0',
  'Merkür':      '#22D3EE',
  'Venüs':       '#EC4899',
  'Mars':        '#EF4444',
  'Jüpiter':     '#F97316',
  'Satürn':      '#84CC16',
  'Uranüs':      '#06B6D4',
  'Neptün':      '#6366F1',
  'Pluto':       '#A855F7',
  'Plüton':      '#A855F7',
  'Pluton':      '#A855F7',
  'Kuzey Düğüm': '#FCD34D',
  'Güney Düğüm': '#FCD34D',
  'Kad':         '#FCD34D',
  'Gad':         '#FCD34D',
  'Yükselen':    '#7C3AED',
  'Ascendant':   '#7C3AED',
  'Orta Gök':    '#7C3AED',
  'Midheaven':   '#7C3AED',
  // İngilizce
  'Sun':     '#F59E0B',
  'Moon':    '#C0C0C0',
  'Mercury': '#22D3EE',
  'Venus':   '#EC4899',
  'Jupiter': '#F97316',
  'Saturn':  '#84CC16',
  'Uranus':  '#06B6D4',
  'Neptune': '#6366F1',
};

// ─── Semboller ───────────────────────────────────────────────────────────────
export const PLANET_SYMBOLS: Record<string, string> = {
  // Türkçe
  'Güneş':       '☉',
  'Ay':          '☽',
  'Merkür':      '☿',
  'Venüs':       '♀',
  'Mars':        '♂',
  'Jüpiter':     '♃',
  'Satürn':      '♄',
  'Uranüs':      '♅',
  'Neptün':      '♆',
  'Pluto':       '♇',
  'Plüton':      '♇',
  'Pluton':      '♇',
  'Kuzey Düğüm': '☊',
  'Güney Düğüm': '☋',
  'Kad':         '☊',
  'Gad':         '☋',
  'Yükselen':    'AC',
  'Ascendant':   'AC',
  'Orta Gök':    'MC',
  'Midheaven':   'MC',
  // İngilizce
  'Sun':     '☉',
  'Moon':    '☽',
  'Mercury': '☿',
  'Venus':   '♀',
  'Jupiter': '♃',
  'Saturn':  '♄',
  'Uranus':  '♅',
  'Neptune': '♆',
};

export function getPlanetColor(name: string): string {
  return PLANET_COLORS[name] || PLANET_COLORS[normalizePlanetName(name)] || colors.textSecondary;
}

export function getPlanetSymbol(name: string): string {
  return PLANET_SYMBOLS[name] || PLANET_SYMBOLS[normalizePlanetName(name)] || '';
}
