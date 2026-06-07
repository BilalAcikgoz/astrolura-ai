import React from 'react';
import { View, Dimensions, StyleSheet } from 'react-native';
import Svg, {
  Circle, Line, Path, Text as SvgText, G
} from 'react-native-svg';
import { BirthChartData } from '../../types/chart.types';
import { ZODIAC_SIGNS } from '../../constants/zodiac';
import { getPlanetColor } from '../../constants/planets';
import { colors } from '../../constants/colors';

const W = Math.min(Dimensions.get('window').width - 32, 380);
const SIZE = W;
const CX = SIZE / 2;
const CY = SIZE / 2;

const R_OUTER = SIZE / 2 - 4;   // Dış kenar
const R_ZODIAC_OUTER = R_OUTER;
const R_ZODIAC_INNER = R_OUTER * 0.82;
const R_HOUSE = R_ZODIAC_INNER;
const R_HOUSE_INNER = R_OUTER * 0.55;
const R_PLANET = R_OUTER * 0.68;
const R_ASPECT = R_OUTER * 0.52;

function toRad(deg: number) { return (deg - 90) * (Math.PI / 180); }

function polarXY(angleDeg: number, r: number) {
  // Astrolojide 0° (Koç başlangıcı) sola denk gelir, saat yönünün tersine gider
  // SVG'de ASC noktasına göre rotate edeceğiz
  const rad = toRad(angleDeg);
  return { x: CX + r * Math.cos(rad), y: CY + r * Math.sin(rad) };
}

function arcPath(r: number, startDeg: number, endDeg: number): string {
  const start = polarXY(startDeg, r);
  const end = polarXY(endDeg, r);
  const large = ((endDeg - startDeg + 360) % 360) > 180 ? 1 : 0;
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${large} 1 ${end.x} ${end.y}`;
}

interface Props {
  chartData: BirthChartData;
}

export default function NatalChartWheel({ chartData }: Props) {
  const { planets, houses, aspects } = chartData;

  // ASC longitude'u bul (1. ev cusp)
  const ascLongitude = houses[0]?.cusp_longitude ?? 0;
  // Rotasyon: ASC ekranın sol tarafında (180°) olacak şekilde
  const rotate = 180 - ascLongitude;

  function lonToAngle(lon: number) {
    return (lon + rotate + 360) % 360;
  }

  return (
    <View style={styles.container}>
      <Svg width={SIZE} height={SIZE}>
        {/* Arka plan */}
        <Circle cx={CX} cy={CY} r={R_OUTER} fill={colors.background} stroke={colors.border} strokeWidth={1} />

        {/* Burç dilimleri */}
        {ZODIAC_SIGNS.map((sign, i) => {
          const startDeg = lonToAngle(i * 30);
          const endDeg = lonToAngle((i + 1) * 30);
          const midAngle = lonToAngle(i * 30 + 15);
          const midPos = polarXY(midAngle, (R_ZODIAC_OUTER + R_ZODIAC_INNER) / 2);
          return (
            <G key={sign.id}>
              {/* Dilim arka planı */}
              <Path
                d={`M ${polarXY(startDeg, R_ZODIAC_INNER).x} ${polarXY(startDeg, R_ZODIAC_INNER).y}
                    A ${R_ZODIAC_INNER} ${R_ZODIAC_INNER} 0 0 1 ${polarXY(endDeg, R_ZODIAC_INNER).x} ${polarXY(endDeg, R_ZODIAC_INNER).y}
                    L ${polarXY(endDeg, R_ZODIAC_OUTER).x} ${polarXY(endDeg, R_ZODIAC_OUTER).y}
                    A ${R_ZODIAC_OUTER} ${R_ZODIAC_OUTER} 0 0 0 ${polarXY(startDeg, R_ZODIAC_OUTER).x} ${polarXY(startDeg, R_ZODIAC_OUTER).y} Z`}
                fill={sign.color + '22'}
                stroke={colors.border}
                strokeWidth={0.5}
              />
              {/* Burç sembolü */}
              <SvgText
                x={midPos.x}
                y={midPos.y}
                fill={sign.color}
                fontSize={10}
                textAnchor="middle"
                alignmentBaseline="middle"
              >
                {sign.symbol}
              </SvgText>
            </G>
          );
        })}

        {/* İç daire */}
        <Circle cx={CX} cy={CY} r={R_ZODIAC_INNER} fill={colors.card} stroke={colors.border} strokeWidth={1} />
        <Circle cx={CX} cy={CY} r={R_HOUSE_INNER} fill={colors.surface} stroke={colors.border} strokeWidth={0.5} />

        {/* Aspect çizgileri */}
        {aspects.map((asp, i) => {
          const p1 = planets.find((p) => p.name === asp.planet1 || p.name_en === asp.planet1);
          const p2 = planets.find((p) => p.name === asp.planet2 || p.name_en === asp.planet2);
          if (!p1 || !p2) return null;
          const pos1 = polarXY(lonToAngle(p1.longitude), R_ASPECT);
          const pos2 = polarXY(lonToAngle(p2.longitude), R_ASPECT);
          const col = asp.nature === 'harmonious' ? colors.harmonious
            : asp.nature === 'challenging' ? colors.challenging
            : colors.neutral;
          return (
            <Line
              key={i}
              x1={pos1.x} y1={pos1.y}
              x2={pos2.x} y2={pos2.y}
              stroke={col}
              strokeWidth={0.6}
              opacity={0.5}
            />
          );
        })}

        {/* Ev çizgileri */}
        {houses.map((house) => {
          const angle = lonToAngle(house.cusp_longitude);
          const inner = polarXY(angle, R_HOUSE_INNER);
          const outer = polarXY(angle, R_HOUSE);
          const isAngle = [1, 4, 7, 10].includes(house.number);
          return (
            <G key={house.number}>
              <Line
                x1={inner.x} y1={inner.y}
                x2={outer.x} y2={outer.y}
                stroke={isAngle ? colors.accent : colors.border}
                strokeWidth={isAngle ? 1.5 : 0.8}
              />
              {/* Ev numarası */}
              {(() => {
                const nextHouse = houses[(house.number % 12)];
                const midLon = nextHouse
                  ? (house.cusp_longitude + ((nextHouse.cusp_longitude - house.cusp_longitude + 360) % 360) / 2)
                  : house.cusp_longitude + 15;
                const numPos = polarXY(lonToAngle(midLon), (R_HOUSE + R_HOUSE_INNER) / 2);
                return (
                  <SvgText
                    x={numPos.x}
                    y={numPos.y}
                    fill={colors.textMuted}
                    fontSize={9}
                    textAnchor="middle"
                    alignmentBaseline="middle"
                  >
                    {house.number}
                  </SvgText>
                );
              })()}
            </G>
          );
        })}

        {/* ASC ok */}
        {(() => {
          const angle = lonToAngle(ascLongitude);
          const tip = polarXY(angle, R_ZODIAC_INNER - 2);
          const base = polarXY(angle, CX * 0.3);
          return (
            <Line
              x1={base.x} y1={base.y}
              x2={tip.x} y2={tip.y}
              stroke="#60A5FA"
              strokeWidth={2}
            />
          );
        })()}

        {/* MC ok */}
        {(() => {
          const mc = houses[9]; // 10. ev = MC
          if (!mc) return null;
          const angle = lonToAngle(mc.cusp_longitude);
          const tip = polarXY(angle, R_ZODIAC_INNER - 2);
          const base = polarXY(angle, CX * 0.3);
          return (
            <Line
              x1={base.x} y1={base.y}
              x2={tip.x} y2={tip.y}
              stroke={colors.accent}
              strokeWidth={2}
            />
          );
        })()}

        {/* Gezegenler */}
        {planets.map((planet, i) => {
          const angle = lonToAngle(planet.longitude);
          const pos = polarXY(angle, R_PLANET);
          const col = getPlanetColor(planet.name);
          return (
            <G key={i}>
              <Circle cx={pos.x} cy={pos.y} r={8} fill={colors.background} stroke={col} strokeWidth={1} />
              <SvgText
                x={pos.x}
                y={pos.y}
                fill={col}
                fontSize={9}
                textAnchor="middle"
                alignmentBaseline="middle"
              >
                {planet.symbol}
              </SvgText>
              {planet.retrograde && (
                <SvgText
                  x={pos.x + 8}
                  y={pos.y - 6}
                  fill={colors.retrograde}
                  fontSize={7}
                  textAnchor="middle"
                >
                  ℞
                </SvgText>
              )}
            </G>
          );
        })}

        {/* Merkez nokta */}
        <Circle cx={CX} cy={CY} r={3} fill={colors.accent} />
      </Svg>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { alignItems: 'center', justifyContent: 'center' },
});
