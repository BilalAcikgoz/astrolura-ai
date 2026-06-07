import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { colors } from '../../constants/colors';
import { EssentialDignitiesTable } from '../../types/chart.types';
import { getPlanetColor, getPlanetSymbol, normalizePlanetName } from '../../constants/planets';

interface Props { dignities: EssentialDignitiesTable }

const COL_PLN  = 160;
const COL_STD  = 90;
const COL_SKOR = 70;

const COL_HEADERS = ['Gezegen', 'Yönetici', 'Yücelme', 'Üçlü', 'Terim', 'Dekan', 'Zarar', 'Düşüş', 'Skor'];

export default function DiginitiesTable({ dignities }: Props) {
  return (
    <View style={styles.container}>
      <Text style={styles.tableTitle}>Asaletler</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <View>
          {/* Header */}
          <View style={styles.header}>
            {COL_HEADERS.map((h, i) => (
              <Text
                key={h}
                style={[
                  styles.cell,
                  styles.headerText,
                  { width: i === 0 ? COL_PLN : i === COL_HEADERS.length - 1 ? COL_SKOR : COL_STD },
                ]}
              >
                {h}
              </Text>
            ))}
          </View>
          {/* Rows */}
          {dignities.rows.map((row, i) => {
            const displayName = normalizePlanetName(row.planet);
            const sym = getPlanetSymbol(row.planet) || '';
            return (
              <View key={i} style={[styles.row, i % 2 === 0 && styles.rowAlt]}>
                {/* Gezegen: sembol + isim */}
                <Text style={[styles.cell, { width: COL_PLN, color: getPlanetColor(row.planet), fontWeight: '600' }]}>
                  {sym ? `${sym} ` : ''}{displayName}
                </Text>
                <Text style={[styles.cell, { width: COL_STD }]}>{row.ruler.join(', ') || '-'}</Text>
                <Text style={[styles.cell, { width: COL_STD }]}>{row.exaltation.join(', ') || '-'}</Text>
                <Text style={[styles.cell, { width: COL_STD }]}>{row.triplicity.join(', ') || '-'}</Text>
                <Text style={[styles.cell, { width: COL_STD }]}>{row.term.join(', ') || '-'}</Text>
                <Text style={[styles.cell, { width: COL_STD }]}>{row.face.join(', ') || '-'}</Text>
                <Text style={[styles.cell, { width: COL_STD, color: colors.challenging }]}>
                  {row.detriment.join(', ') || '-'}
                </Text>
                <Text style={[styles.cell, { width: COL_STD, color: colors.challenging }]}>
                  {row.fall.join(', ') || '-'}
                </Text>
                <Text style={[styles.cell, styles.score, { width: COL_SKOR }, row.score >= 0 ? styles.pos : styles.neg]}>
                  {row.score > 0 ? '+' : ''}{row.score}
                </Text>
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
  score: { fontWeight: '700', fontSize: 13 },
  pos: { color: colors.harmonious },
  neg: { color: colors.challenging },
});
