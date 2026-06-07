import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { colors } from '../../constants/colors';
import { PlanetPosition } from '../../types/chart.types';
import { getPlanetColor, getPlanetSymbol, normalizePlanetName } from '../../constants/planets';
import { getSignSymbol } from '../../constants/zodiac';

interface Props { planets: PlanetPosition[]; title?: string }

const COL_PLN = 160;
const COL_BUR = 120;
const COL_DEG = 100;
const COL_EV  = 50;
const COL_HIZ = 110;

/** Hız değeri tamamen sıfırsa boş göster */
function formatSpeed(speedDisplay?: string, speed?: number): string {
  if (speedDisplay) {
    // "00°00'00''" veya "+00°00'00''" gibi tüm rakamlar sıfırsa boş bırak
    const digits = speedDisplay.replace(/[^0-9]/g, '');
    if (digits && Number(digits) === 0) return '';
    return speedDisplay;
  }
  if (speed == null) return '-';
  if (speed === 0) return '';
  return `${speed >= 0 ? '+' : ''}${speed.toFixed(2)}°`;
}

export default function PlanetsTable({ planets, title = 'Natal' }: Props) {
  return (
    <View style={styles.container}>
      <Text style={styles.tableTitle}>{title}</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <View>
          {/* Header */}
          <View style={styles.header}>
            <Text style={[styles.cell, styles.headerText, { width: COL_PLN }]}>Gezegen</Text>
            <Text style={[styles.cell, styles.headerText, { width: COL_BUR }]}>Burç</Text>
            <Text style={[styles.cell, styles.headerText, { width: COL_DEG }]}>Derece</Text>
            <Text style={[styles.cell, styles.headerText, { width: COL_EV }]}>Ev</Text>
            <Text style={[styles.cell, styles.headerText, { width: COL_HIZ }]}>Hız</Text>
          </View>
          {/* Rows */}
          {planets.map((p, i) => {
            const displayName = normalizePlanetName(p.name);
            const sym = getPlanetSymbol(p.name) || p.symbol || '';
            // Doğru sembolü burç adından türet (backend'den gelen sign_symbol güvenilmez)
            const signSym = getSignSymbol(p.sign_symbol || p.sign_en || p.sign);
            const degreeStr = p.degree_display
              ?? (p.degree_in_sign != null ? `${p.degree_in_sign.toFixed(1)}°` : '-');
            const speedStr = formatSpeed(p.speed_display, p.speed);
            return (
              <View key={i} style={[styles.row, i % 2 === 0 && styles.rowAlt]}>
                {/* Gezegen: sembol + isim + ℞ */}
                <View style={[{ width: COL_PLN }, styles.planetCell]}>
                  <Text style={[styles.cell, { color: getPlanetColor(p.name) }]}>
                    {sym} {displayName}
                  </Text>
                  {p.retrograde && <Text style={styles.retro}>℞</Text>}
                </View>
                {/* Burç: güvenilir sembol (zodiac mapping) + Türkçe isim */}
                <Text style={[styles.cell, { width: COL_BUR }]}>
                  {signSym ? `${signSym} ` : ''}{p.sign}
                </Text>
                <Text style={[styles.cell, { width: COL_DEG }]}>{degreeStr}</Text>
                <Text style={[styles.cell, { width: COL_EV }]}>{p.house}</Text>
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
