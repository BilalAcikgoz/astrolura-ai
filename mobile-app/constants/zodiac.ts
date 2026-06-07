import { colors } from './colors';

export const ZODIAC_SIGNS = [
  { id: 0, name: 'Koç', nameEn: 'Aries', symbol: '♈', element: 'fire', color: '#EF4444' },
  { id: 1, name: 'Boğa', nameEn: 'Taurus', symbol: '♉', element: 'earth', color: '#F59E0B' },
  { id: 2, name: 'İkizler', nameEn: 'Gemini', symbol: '♊', element: 'air', color: '#22C55E' },
  { id: 3, name: 'Yengeç', nameEn: 'Cancer', symbol: '♋', element: 'water', color: '#3B82F6' },
  { id: 4, name: 'Aslan', nameEn: 'Leo', symbol: '♌', element: 'fire', color: '#EF4444' },
  { id: 5, name: 'Başak', nameEn: 'Virgo', symbol: '♍', element: 'earth', color: '#F59E0B' },
  { id: 6, name: 'Terazi', nameEn: 'Libra', symbol: '♎', element: 'air', color: '#22C55E' },
  { id: 7, name: 'Akrep', nameEn: 'Scorpio', symbol: '♏', element: 'water', color: '#3B82F6' },
  { id: 8, name: 'Yay', nameEn: 'Sagittarius', symbol: '♐', element: 'fire', color: '#EF4444' },
  { id: 9, name: 'Oğlak', nameEn: 'Capricorn', symbol: '♑', element: 'earth', color: '#F59E0B' },
  { id: 10, name: 'Kova', nameEn: 'Aquarius', symbol: '♒', element: 'air', color: '#22C55E' },
  { id: 11, name: 'Balık', nameEn: 'Pisces', symbol: '♓', element: 'water', color: '#3B82F6' },
];

export const ELEMENT_COLORS: Record<string, string> = {
  fire:  '#EF4444',  // kırmızı
  earth: '#F59E0B',  // sarı-turuncu
  air:   '#22C55E',  // yeşil
  water: '#3B82F6',  // mavi
};

export const ELEMENT_NAMES: Record<string, string> = {
  fire: 'Ateş',
  earth: 'Toprak',
  air: 'Hava',
  water: 'Su',
};

export const QUALITY_NAMES: Record<string, string> = {
  cardinal: 'Kardinal',
  fixed: 'Sabit',
  mutable: 'Değişken',
};

export const QUALITY_COLORS: Record<string, string> = {
  cardinal: '#F59E0B',  // sarı-turuncu (öncü = toprak ile aynı)
  fixed:    '#22C55E',  // yeşil (sabit)
  mutable:  '#EF4444',  // kırmızı (değişken)
};

export function getZodiacByName(name: string) {
  return ZODIAC_SIGNS.find(
    (z) =>
      z.name === name ||
      z.nameEn.toLowerCase() === name.toLowerCase() ||
      z.symbol === name
  );
}

/**
 * Bir burç isminden (Türkçe, İngilizce veya zaten sembol) doğru Unicode sembolü döndürür.
 * Backend'in sign_symbol alanına güvenmek yerine burç adından türetir.
 * Örnek: "Aries" → "♈", "Koç" → "♈", "cancer" → "♋"
 */
export function getSignSymbol(signNameOrSymbol: string): string {
  if (!signNameOrSymbol) return '';
  const found = ZODIAC_SIGNS.find(
    (z) =>
      z.name === signNameOrSymbol ||
      z.nameEn.toLowerCase() === signNameOrSymbol.toLowerCase() ||
      z.symbol === signNameOrSymbol
  );
  return found?.symbol ?? signNameOrSymbol;
}
