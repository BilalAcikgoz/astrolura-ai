import React from 'react';
import { View, Dimensions, StyleSheet } from 'react-native';
import Svg, { Circle, Line, G, Text as SvgText } from 'react-native-svg';
import { BirthChartData, TransitChartResponse } from '../../types/chart.types';
import { ZODIAC_SIGNS } from '../../constants/zodiac';
import { getPlanetColor } from '../../constants/planets';
import { colors } from '../../constants/colors';

const W = Math.min(Dimensions.get('window').width - 32, 380);
const SIZE = W;
const CX = SIZE / 2;
const CY = SIZE / 2;

const R_OUTER = SIZE / 2 - 4;
const R_ZODIAC_INNER = R_OUTER * 0.82;
const R_TRANSIT_PLANET = R_OUTER * 0.72;
const R_HOUSE = R_ZODIAC_INNER;
const R_HOUSE_INNER = R_OUTER * 0.55;
const R_NATAL_PLANET = R_OUTER * 0.47;
const R_ASPECT = R_OUTER * 0.42;

function polarXY(angleDeg: number, r: number) {
  const rad = (angleDeg - 90) * (Math.PI / 180);
  return { x: CX + r * Math.cos(rad), y: CY + r * Math.sin(rad) };
}

interface Props {
  natalData: BirthChartData;
  transitData: TransitChartResponse;
}

export default function TransitChartWheel({ natalData, transitData }: Props) {
  const { planets: natalPlanets, houses, aspects: natalAspects } = natalData;
  const { transit_planets, transit_aspects } = transitData;

  const ascLongitude = houses[0]?.cusp_longitude ?? 0;
  const rotate = 180 - ascLongitude;

  function lonToAngle(lon: number) {
    return (lon + rotate + 360) % 360;
  }

  return (
    <View style={styles.container}>
      <Svg width={SIZE} height={SIZE}>
        {/* Arka plan */}
        <Circle cx={CX} cy={CY} r={R_OUTER} fill={colors.background} stroke={colors.border} strokeWidth={1} />

        {/* Burç halkası (dış) */}
        {ZODIAC_SIGNS.map((sign, i) => {
          const startDeg = lonToAngle(i * 30);
          const endDeg = lonToAngle((i + 1) * 30);
          const midAngle = lonToAngle(i * 30 + 15);
          const midPos = polarXY(midAngle, (R_OUTER + R_ZODIAC_INNER) / 2);
          return (
            <G key={sign.id}>
              <SvgText
                x={midPos.x}
                y={midPos.y}
                fill={sign.color}
                fontSize={9}
                textAnchor="middle"
                alignmentBaseline="middle"
              >
                {sign.symbol}
              </SvgText>
            </G>
          );
        })}

        {/* İç çemberler */}
        <Circle cx={CX} cy={CY} r={R_ZODIAC_INNER} fill={colors.card} stroke={colors.border} strokeWidth={1} />
        <Circle cx={CX} cy={CY} r={R_HOUSE_INNER} fill={colors.surface} stroke={colors.border} strokeWidth={0.5} />
        <Circle cx={CX} cy={CY} r={R_ASPECT} fill={colors.background} stroke={colors.border} strokeWidth={0.5} />

        {/* Transit-Natal aspect çizgileri */}
        {transit_aspects.slice(0, 20).map((asp, i) => {
          const tp = transit_planets.find(
            (p) => p.name_tr === asp.transit_planet_tr ||
                   p.name_en === asp.transit_planet_en
          );
          const np = natalPlanets.find(
            (p) => p.name === asp.natal_planet_tr || p.name_en === asp.natal_planet_en
          );
          if (!tp || !np) return null;
          const tpLon = tp.longitude ?? 0;
          const pos1 = polarXY(lonToAngle(tpLon), R_ASPECT);
          const pos2 = polarXY(lonToAngle(np.longitude), R_ASPECT * 0.7);
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
            <Line
              key={house.number}
              x1={inner.x} y1={inner.y}
              x2={outer.x} y2={outer.y}
              stroke={isAngle ? colors.accent : colors.border}
              strokeWidth={isAngle ? 1.5 : 0.8}
            />
          );
        })}

        {/* Natal gezegenler (iç) */}
        {natalPlanets.map((planet, i) => {
          const angle = lonToAngle(planet.longitude);
          const pos = polarXY(angle, R_NATAL_PLANET);
          const col = getPlanetColor(planet.name);
          return (
            <G key={i}>
              <Circle cx={pos.x} cy={pos.y} r={7} fill={colors.surface} stroke={col} strokeWidth={1} />
              <SvgText
                x={pos.x} y={pos.y}
                fill={col} fontSize={8}
                textAnchor="middle" alignmentBaseline="middle"
              >
                {planet.symbol}
              </SvgText>
            </G>
          );
        })}

        {/* Transit gezegenler (dış halka) */}
        {transit_planets.map((planet, i) => {
          const lon = planet.longitude ?? 0;
          const angle = lonToAngle(lon);
          const pos = polarXY(angle, R_TRANSIT_PLANET);
          const col = getPlanetColor(planet.name_tr || planet.name_en);
          return (
            <G key={i}>
              <Circle cx={pos.x} cy={pos.y} r={7} fill={colors.card} stroke={col + 'BB'} strokeWidth={1.2} strokeDasharray="3,1" />
              <SvgText
                x={pos.x} y={pos.y}
                fill={col + 'BB'} fontSize={8}
                textAnchor="middle" alignmentBaseline="middle"
              >
                {planet.symbol}
              </SvgText>
            </G>
          );
        })}

        <Circle cx={CX} cy={CY} r={3} fill={colors.accent} />
      </Svg>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { alignItems: 'center', justifyContent: 'center' },
});
