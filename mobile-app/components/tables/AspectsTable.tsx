import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { colors } from '../../constants/colors';
import { AspectInfo } from '../../types/chart.types';
import { getPlanetColor, getPlanetSymbol, normalizePlanetName } from '../../constants/planets';

interface Props { aspects: AspectInfo[] }

function natureColor(nature: string) {
  if (nature === 'harmonious') return colors.harmonious;
  if (nature === 'challenging') return colors.challenging;
  return colors.neutral;
}

const COL_PLN1 = 150;  // Gezegen 1
const COL_ACK  = 150;  // Açı (isim + derece)
const COL_PLN2 = 150;  // Gezegen 2
const COL_ORB  = 60;   // Orb

/** "Karşıt" + angle → "Karşıt 180°" */
function aspectLabel(aspectName: string, angle?: number): string {
  if (angle != null) return `${aspectName} ${Math.round(angle)}°`;
  return aspectName;
}

/** Gezegen adından sembol + normalleştirilmiş isim */
function renderPlanetText(raw: string): string {
  const name = normalizePlanetName(raw);
  const sym  = getPlanetSymbol(raw) || getPlanetSymbol(name) || '';
  return sym ? `${sym} ${name}` : name;
}

export default function AspectsTable({ aspects }: Props) {
  return (
    <View style={styles.container}>
      <Text style={styles.tableTitle}>Açılar</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <View>
          {/* Header */}
          <View style={styles.header}>
            <Text style={[styles.cell, styles.headerText, { width: COL_PLN1 }]}>Gezegen</Text>
            <Text style={[styles.cell, styles.headerText, { width: COL_ACK }]}>Açı</Text>
            <Text style={[styles.cell, styles.headerText, { width: COL_PLN2 }]}>Gezegen</Text>
            <Text style={[styles.cell, styles.headerText, { width: COL_ORB }]}>Orb</Text>
          </View>
          {/* Rows */}
          {aspects.map((a, i) => (
            <View key={i} style={[styles.row, i % 2 === 0 && styles.rowAlt]}>
              {/* Gezegen 1 */}
              <Text style={[styles.cell, { width: COL_PLN1 }]}>
                {renderPlanetText(a.planet1)}
              </Text>
              {/* Açı: yalnızca isim + derece — sembol yok */}
              <Text style={[styles.cell, { width: COL_ACK, color: natureColor(a.nature) }]}>
                {aspectLabel(a.aspect, a.angle)}
              </Text>
              {/* Gezegen 2 */}
              <Text style={[styles.cell, { width: COL_PLN2 }]}>
                {renderPlanetText(a.planet2)}
              </Text>
              <Text style={[styles.cell, styles.orb, { width: COL_ORB }]}>
                {a.orb != null ? a.orb.toFixed(2) : '-'}
              </Text>
            </View>
          ))}
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
  aspectCell: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  aspectSymbol: { fontSize: 16, fontWeight: '700' },
  orb: { color: colors.textSecondary },
});
