/**
 * Custom scroll-wheel time picker for iOS.
 *
 * @react-native-community/datetimepicker v8.x has a known bug (#1007)
 * where the spinner time picker gets stuck after a date picker with
 * minimumDate/maximumDate is shown. This component replaces the buggy
 * native spinner with a pure-RN ScrollView-based wheel.
 */
import React, { useRef, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  NativeSyntheticEvent,
  NativeScrollEvent,
} from 'react-native';
import { colors } from '../../constants/colors';

const ITEM_HEIGHT = 44;
const VISIBLE_ITEMS = 5;
const PICKER_HEIGHT = ITEM_HEIGHT * VISIBLE_ITEMS;

// ── Tek sütun (saat veya dakika) ────────────────────────────────────
interface WheelColumnProps {
  data: number[];
  initial: number;
  onValueChange: (v: number) => void;
}

function WheelColumn({ data, initial, onValueChange }: WheelColumnProps) {
  const scrollRef = useRef<ScrollView>(null);
  const isInitialMount = useRef(true);
  const currentIndex = useRef(data.indexOf(initial));

  // Başlangıç konumuna scroll
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      const idx = data.indexOf(initial);
      if (idx >= 0) {
        setTimeout(() => {
          scrollRef.current?.scrollTo({ y: idx * ITEM_HEIGHT, animated: false });
        }, 50);
      }
    }
  }, []);

  const handleMomentumEnd = useCallback(
    (e: NativeSyntheticEvent<NativeScrollEvent>) => {
      const y = e.nativeEvent.contentOffset.y;
      const idx = Math.round(y / ITEM_HEIGHT);
      const clamped = Math.max(0, Math.min(idx, data.length - 1));

      if (clamped !== currentIndex.current) {
        currentIndex.current = clamped;
        onValueChange(data[clamped]);
      }
    },
    [data, onValueChange],
  );

  // Pad with empty slots so first & last can center
  const padCount = Math.floor(VISIBLE_ITEMS / 2);

  return (
    <View style={wstyles.column}>
      {/* Selection highlight bar */}
      <View style={wstyles.selectionBar} pointerEvents="none" />

      <ScrollView
        ref={scrollRef}
        showsVerticalScrollIndicator={false}
        snapToInterval={ITEM_HEIGHT}
        decelerationRate="fast"
        onMomentumScrollEnd={handleMomentumEnd}
        contentContainerStyle={{ paddingVertical: padCount * ITEM_HEIGHT }}
      >
        {data.map((val, i) => {
          const label = String(val).padStart(2, '0');
          return (
            <View key={i} style={wstyles.item}>
              <Text style={wstyles.itemText}>{label}</Text>
            </View>
          );
        })}
      </ScrollView>
    </View>
  );
}

// ── Ana bileşen ─────────────────────────────────────────────────────
interface TimeWheelPickerProps {
  initialHour?: number;
  initialMinute?: number;
  onTimeChange?: (h: number, m: number) => void;
}

const HOURS = Array.from({ length: 24 }, (_, i) => i);
const MINUTES = Array.from({ length: 60 }, (_, i) => i);

export default function TimeWheelPicker({
  initialHour = 12,
  initialMinute = 0,
  onTimeChange,
}: TimeWheelPickerProps) {
  const hourRef = useRef(initialHour);
  const minuteRef = useRef(initialMinute);

  const onHourChange = useCallback(
    (h: number) => {
      hourRef.current = h;
      onTimeChange?.(h, minuteRef.current);
    },
    [onTimeChange],
  );

  const onMinuteChange = useCallback(
    (m: number) => {
      minuteRef.current = m;
      onTimeChange?.(hourRef.current, m);
    },
    [onTimeChange],
  );

  return (
    <View style={wstyles.container}>
      <WheelColumn data={HOURS} initial={initialHour} onValueChange={onHourChange} />
      <Text style={wstyles.separator}>:</Text>
      <WheelColumn data={MINUTES} initial={initialMinute} onValueChange={onMinuteChange} />
    </View>
  );
}

const wstyles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: PICKER_HEIGHT,
    overflow: 'hidden',
  },
  column: {
    width: 70,
    height: PICKER_HEIGHT,
  },
  selectionBar: {
    position: 'absolute',
    top: ITEM_HEIGHT * Math.floor(VISIBLE_ITEMS / 2),
    left: 0,
    right: 0,
    height: ITEM_HEIGHT,
    backgroundColor: colors.card,
    borderRadius: 8,
    zIndex: 0,
  },
  item: {
    height: ITEM_HEIGHT,
    alignItems: 'center',
    justifyContent: 'center',
  },
  itemText: {
    fontSize: 22,
    fontWeight: '600',
    color: colors.text,
    fontVariant: ['tabular-nums'],
  },
  separator: {
    fontSize: 24,
    fontWeight: '700',
    color: colors.text,
    marginHorizontal: 8,
  },
});
