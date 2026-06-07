import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { colors } from '../../constants/colors';
import { TransitAspect } from '../../types/chart.types';
import { getPlanetSymbol, normalizePlanetName } from '../../constants/planets';

interface Props {
  aspects: TransitAspect[];
  personName?: string;
}

function natureColor(nature: string) {
  if (nature === 'harmonious') return colors.harmonious;
  if (nature === 'challenging') return colors.challenging;
  return colors.neutral;
}

/** Açı sütunu: "Kare 90°" formatında hem isim hem derece göster */
function aspectLabel(aspectName: string, angle: number): string {
  const name = aspectName?.trim() || '';
  return name ? `${name} ${Math.round(angle)}°` : `${Math.round(angle)}°`;
}

function renderPlanetText(raw: string): string {
  if (!raw) return '-';
  const name = normalizePlanetName(raw);
  const sym  = getPlanetSymbol(raw) || getPlanetSymbol(name) || '';
  return sym ? `${sym} ${name}` : name;
}

const COL_GEZ1 = 150;  // Transit gezegen
const COL_ACK  = 160;  // Açı (isim + derece)
const COL_GEZ2 = 150;  // Natal gezegen
const COL_ORB  = 65;

export default function TransitAspectsTable({ aspects, personName }: Props) {
  const title = personName
    ? `Açılar (${personName} - Transit)`
    : 'Transit Açılar';

  return (
    <View style={styles.container}>
      <Text style={styles.tableTitle}>{title}</Text>
      {(!aspects || aspects.length === 0) ? (
        <Text style={styles.empty}>Transit açı verisi bulunamadı.</Text>
      ) : (
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <View>
            <View style={styles.header}>
              <Text style={[styles.cell, styles.headerText, { width: COL_GEZ1 }]}>Gezegen</Text>
              <Text style={[styles.cell, styles.headerText, { width: COL_ACK }]}>Açı</Text>
              <Text style={[styles.cell, styles.headerText, { width: COL_GEZ2 }]}>Gezegen</Text>
              <Text style={[styles.cell, styles.headerText, { width: COL_ORB }]}>Orb</Text>
            </View>
            {aspects.map((a, i) => (
              <View key={i} style={[styles.row, i % 2 === 0 && styles.rowAlt]}>
                {/* Transit gezegen — backend: transit_planet_tr */}
                <Text style={[styles.cell, { width: COL_GEZ1 }]}>
                  {renderPlanetText(a.transit_planet_tr || '')}
                </Text>
                {/* Açı: isim + derece — backend: aspect_tr + angle */}
                <Text style={[styles.cell, { width: COL_ACK, color: natureColor(a.nature || '') }]}>
                  {aspectLabel(a.aspect_tr || '', a.angle)}
                </Text>
                {/* Natal gezegen — backend: natal_planet_tr */}
                <Text style={[styles.cell, { width: COL_GEZ2 }]}>
                  {renderPlanetText(a.natal_planet_tr || '')}
                </Text>
                <Text style={[styles.cell, styles.orb, { width: COL_ORB }]}>
                  {a.orb != null ? a.orb.toFixed(2) : '-'}
                </Text>
              </View>
            ))}
          </View>
        </ScrollView>
      )}
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
  orb: { color: colors.textSecondary },
  empty: { color: colors.textMuted, fontSize: 13, paddingVertical: 12, paddingHorizontal: 16 },
});
