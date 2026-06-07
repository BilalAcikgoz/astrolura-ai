import React from 'react';
import { View, Text, StyleSheet, Dimensions } from 'react-native';
import Svg, { Path, G, Text as SvgText } from 'react-native-svg';
import { colors } from '../../constants/colors';
import { ELEMENT_COLORS, ELEMENT_NAMES } from '../../constants/zodiac';

interface Slice { label: string; value: number; color: string }

const W = Dimensions.get('window').width - 64;
const SIZE = Math.min(W, 220);
const CX = SIZE / 2;
const CY = SIZE / 2;
const R = SIZE / 2 - 16;

function polarToXY(angle: number, r: number) {
  const rad = (angle - 90) * (Math.PI / 180);
  return { x: CX + r * Math.cos(rad), y: CY + r * Math.sin(rad) };
}

function slicePath(startAngle: number, endAngle: number, r: number): string {
  const start = polarToXY(startAngle, r);
  const end = polarToXY(endAngle, r);
  const large = endAngle - startAngle > 180 ? 1 : 0;
  return `M ${CX} ${CY} L ${start.x} ${start.y} A ${r} ${r} 0 ${large} 1 ${end.x} ${end.y} Z`;
}

function PieChart({ slices }: { slices: Slice[] }) {
  const total = slices.reduce((s, sl) => s + sl.value, 0);
  let currentAngle = 0;
  return (
    <Svg width={SIZE} height={SIZE}>
      {slices.map((sl, i) => {
        const angle = (sl.value / total) * 360;
        const start = currentAngle;
        const end = currentAngle + angle;
        const labelAngle = start + angle / 2;
        const labelPos = polarToXY(labelAngle, R * 0.65);
        currentAngle += angle;
        if (sl.value === 0) return null;
        return (
          <G key={i}>
            <Path d={slicePath(start, end, R)} fill={sl.color} stroke={colors.background} strokeWidth={2} />
            <SvgText
              x={labelPos.x}
              y={labelPos.y}
              fill="#fff"
              fontSize={11}
              fontWeight="700"
              textAnchor="middle"
              alignmentBaseline="middle"
            >
              {sl.value > 5 ? `${sl.value.toFixed(0)}%` : ''}
            </SvgText>
          </G>
        );
      })}
    </Svg>
  );
}

interface Props {
  elements: { fire: number; earth: number; air: number; water: number };
}

export default function ElementsPieChart({ elements }: Props) {
  const slices: Slice[] = [
    { label: 'Ateş', value: elements.fire, color: ELEMENT_COLORS.fire },
    { label: 'Toprak', value: elements.earth, color: ELEMENT_COLORS.earth },
    { label: 'Hava', value: elements.air, color: ELEMENT_COLORS.air },
    { label: 'Su', value: elements.water, color: ELEMENT_COLORS.water },
  ];

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Elementler</Text>
      <View style={styles.row}>
        <PieChart slices={slices} />
        <View style={styles.legend}>
          {slices.map((sl) => (
            <View key={sl.label} style={styles.legendItem}>
              <View style={[styles.dot, { backgroundColor: sl.color }]} />
              <Text style={styles.legendLabel}>{sl.label}</Text>
              <Text style={styles.legendValue}>{sl.value.toFixed(1)}%</Text>
            </View>
          ))}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { marginBottom: 28 },
  title: { fontSize: 15, fontWeight: '700', color: colors.accent, marginBottom: 12 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 16 },
  legend: { flex: 1, gap: 10 },
  legendItem: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  dot: { width: 10, height: 10, borderRadius: 5 },
  legendLabel: { flex: 1, fontSize: 13, color: colors.text },
  legendValue: { fontSize: 13, fontWeight: '700', color: colors.text },
});
