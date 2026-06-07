import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { colors } from '../../constants/colors';
import { HouseInfo } from '../../types/chart.types';
import { getSignSymbol } from '../../constants/zodiac';

interface Props { houses: HouseInfo[] }

const COL_EV  = 60;
const COL_BUR = 130;
const COL_DEG = 100;

export default function HousesTable({ houses }: Props) {
  return (
    <View style={styles.container}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <View>
          {/* Header */}
          <View style={styles.header}>
            <Text style={[styles.cell, styles.headerText, { width: COL_EV }]}>Ev</Text>
            <Text style={[styles.cell, styles.headerText, { width: COL_BUR }]}>Burç</Text>
            <Text style={[styles.cell, styles.headerText, { width: COL_DEG }]}>Derece</Text>
          </View>
          {/* Rows */}
          {houses.map((h) => {
            // Doğru sembolü burç adından türet
            const signSym = getSignSymbol(h.sign_symbol || h.sign_en || h.sign);
            return (
              <View key={h.number} style={[styles.row, h.number % 2 === 0 && styles.rowAlt]}>
                <Text style={[styles.cell, styles.evCell, { width: COL_EV }]}>{h.number}</Text>
                <Text style={[styles.cell, styles.value, { width: COL_BUR }]}>
                  {signSym ? `${signSym} ` : ''}{h.sign}
                </Text>
                <Text style={[styles.cell, styles.value, { width: COL_DEG }]}>{h.degree_display}</Text>
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
  evCell: { color: colors.accent, fontWeight: '700' },
  value: { color: colors.text },
});
