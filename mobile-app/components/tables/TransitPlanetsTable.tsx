import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { colors } from '../../constants/colors';
import { TransitPlanet } from '../../types/chart.types';
import { getPlanetColor, getPlanetSymbol, normalizePlanetName } from '../../constants/planets';
import { getSignSymbol } from '../../constants/zodiac';

interface Props { planets: TransitPlanet[] }

const COL_PLN = 160;
const COL_BUR = 120;
const COL_DEG = 100;
const COL_EV  = 50;
const COL_HIZ = 110;

/** Hız değeri tamamen sıfırsa boş göster */
function formatSpeed(speedDisplay?: string, speed?: number): string {
  if (speedDisplay) {
    const digits = speedDisplay.replace(/[^0-9]/g, '');
    if (digits && Number(digits) === 0) return '';
    return speedDisplay;
  }
  if (speed == null) return '-';
  if (speed === 0) return '';
  return `${speed >= 0 ? '+' : ''}${speed.toFixed(2)}°`;
}

export default function TransitPlanetsTable({ planets }: Props) {
  return (
    <View style={styles.container}>
      <Text style={styles.tableTitle}>Transit</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <View>
          <View style={styles.header}>
            <Text style={[styles.cell, styles.headerText, { width: COL_PLN }]}>Gezegen</Text>
            <Text style={[styles.cell, styles.headerText, { width: COL_BUR }]}>Burç</Text>
            <Text style={[styles.cell, styles.headerText, { width: COL_DEG }]}>Derece</Text>
            <Text style={[styles.cell, styles.headerText, { width: COL_EV }]}>Ev</Text>
            <Text style={[styles.cell, styles.headerText, { width: COL_HIZ }]}>Hız</Text>
          </View>
          {planets.map((p, i) => {
            const rawName = p.name_tr || p.name_en || '';
            const displayName = normalizePlanetName(rawName);
            const sym = getPlanetSymbol(rawName) || p.symbol || '';
            // Backend sign_tr (Türkçe burç adı) veya sign_en'den sembol türet
            const signSym = getSignSymbol(p.sign_en || p.sign_tr);
            const signName = p.sign_tr || p.sign_en || '-';
            const degreeStr = p.degree_display || '-';
            const speedStr = formatSpeed(p.speed_display, p.speed);
            return (
              <View key={i} style={[styles.row, i % 2 === 0 && styles.rowAlt]}>
                <View style={[{ width: COL_PLN }, styles.planetCell]}>
                  <Text style={[styles.cell, { color: getPlanetColor(rawName) }]}>
                    {sym} {displayName}
                  </Text>
                  {p.retrograde && <Text style={styles.retro}>℞</Text>}
                </View>
                <Text style={[styles.cell, { width: COL_BUR }]}>
                  {signSym ? `${signSym} ` : ''}{signName}
                </Text>
                <Text style={[styles.cell, { width: COL_DEG }]}>{degreeStr}</Text>
                <Text style={[styles.cell, { width: COL_EV }]}>{p.house ?? '-'}</Text>
                <Text style={[styles.cell, styles.speed, { width: COL_HIZ }]}>{speedStr}</Text>
              </View>
            );
          })}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { marginBottom: 24 },
  tableTitle: { fontSize: 18, fontWeight: '700', color: colors.text, marginBottom: 10, textAlign: 'center' },
  header: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginBottom: 2,
  },
  row: {
    flexDirection: 'row',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 6,
    alignItems: 'center',
  },
  rowAlt: { backgroundColor: colors.card },
  cell: { fontSize: 13, color: colors.text, paddingRight: 8 },
  headerText: { fontWeight: '700', color: colors.textSecondary, fontSize: 12 },
  planetCell: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  retro: { color: colors.retrograde, fontSize: 11, fontWeight: '700' },
  speed: { color: colors.textSecondary, fontSize: 12 },
});
