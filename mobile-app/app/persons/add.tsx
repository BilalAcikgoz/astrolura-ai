import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  Alert,
  Platform,
  Modal,
  ActivityIndicator,
} from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';
import { router, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../../constants/colors';
import AstroButton from '../../components/ui/AstroButton';
import TimeWheelPicker from '../../components/ui/TimeWheelPicker';
import { usePersons } from '../../hooks/usePersons';

function formatDate(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function displayDate(str: string): string {
  if (!str) return '';
  const [y, m, d] = str.split('-');
  return `${d}.${m}.${y}`;
}

// iOS saat picker'ı — custom scroll-wheel bileşeni kullanır.
// @react-native-community/datetimepicker v8.x'de bilinen bir bug (#1007) yüzünden
// native spinner, date picker (min/maxDate) açıldıktan sonra donuyor.
function TimeSheet({
  onConfirm,
  initialHour = 12,
  initialMinute = 0,
}: {
  onConfirm: (h: number, m: number) => void;
  initialHour?: number;
  initialMinute?: number;
}) {
  const selectedRef = React.useRef({ h: initialHour, m: initialMinute });

  return (
    <Modal transparent animationType="slide">
      <View style={styles.overlay}>
        <View style={styles.sheet}>
          <View style={styles.sheetHeader}>
            <Text style={styles.sheetTitle}>Doğum Saati</Text>
            <TouchableOpacity onPress={() => onConfirm(selectedRef.current.h, selectedRef.current.m)}>
              <Text style={styles.doneBtn}>Tamam</Text>
            </TouchableOpacity>
          </View>
          <TimeWheelPicker
            initialHour={initialHour}
            initialMinute={initialMinute}
            onTimeChange={(h, m) => {
              selectedRef.current = { h, m };
            }}
          />
        </View>
      </View>
    </Modal>
  );
}

export default function AddPersonScreen() {
  const { returnTo } = useLocalSearchParams<{ returnTo?: string }>();
  const { createPerson } = usePersons();

  const [name, setName] = useState('');
  const [birthDate, setBirthDate] = useState('');
  const [birthTime, setBirthTime] = useState('');
  const [birthPlace, setBirthPlace] = useState('');
  const [saving, setSaving] = useState(false);

  // Date picker — öğlen saati ile başlat (gece yarısı + DST = gün kayması bug'ını önler)
  const [showDate, setShowDate] = useState(false);
  const [dateVal, setDateVal] = useState(new Date(1990, 0, 1, 12, 0, 0));
  const pendingDateRef = useRef(new Date(1990, 0, 1, 12, 0, 0));

  // Time picker
  const [showTime, setShowTime] = useState(false);
  // Son seçilen saat/dakika — picker tekrar açıldığında bu değerle başlar
  const [lastHour, setLastHour] = useState(12);
  const [lastMinute, setLastMinute] = useState(0);
  // Android: sabit başlangıç değeri (her render'da new Date() üretmemek için)
  const [timeVal, setTimeVal] = useState<Date>(() => {
    const d = new Date();
    d.setHours(12, 0, 0, 0);
    return d;
  });

  // City search
  const [cityQuery, setCityQuery] = useState('');
  const [cityResults, setCityResults] = useState<string[]>([]);
  const [cityLoading, setCityLoading] = useState(false);
  const [searchTimer, setSearchTimer] = useState<ReturnType<typeof setTimeout> | null>(null);

  function onDateChange(_: any, selected?: Date) {
    if (Platform.OS === 'android') {
      setShowDate(false);
      if (selected) {
        const d = new Date(selected.getFullYear(), selected.getMonth(), selected.getDate(), 12, 0, 0);
        setDateVal(d);
        setBirthDate(formatDate(d));
      }
    } else {
      // iOS: sadece ref güncelle, state güncelleme → re-render olmaz, picker kaymaz
      if (selected) pendingDateRef.current = selected;
    }
  }

  function onDateDone() {
    const sel = pendingDateRef.current;
    // Öğle saatine normalize et → UTC/yerel saat farkından kaynaklanan +1 gün hatasını önler
    const d = new Date(sel.getFullYear(), sel.getMonth(), sel.getDate(), 12, 0, 0);
    setDateVal(d);
    setBirthDate(formatDate(d));
    setShowDate(false);
  }

  function onCityInput(text: string) {
    setCityQuery(text);
    setBirthPlace(text);
    setCityResults([]);
    if (searchTimer) clearTimeout(searchTimer);
    if (text.length < 2) return;
    const t = setTimeout(() => fetchCities(text), 400);
    setSearchTimer(t);
  }

  async function fetchCities(q: string) {
    setCityLoading(true);
    try {
      const url =
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(q)}` +
        `&format=json&limit=8&addressdetails=1&featuretype=city`;
      const res = await fetch(url, {
        headers: { 'Accept-Language': 'tr,en', 'User-Agent': 'AstroluraAI/1.0' },
      });
      const data = await res.json();
      const results: string[] = [];
      for (const item of data) {
        const addr = item.address || {};
        const city = addr.city || addr.town || addr.village || addr.municipality || '';
        const country = addr.country || '';
        if (city && country) {
          const label = `${city}, ${country}`;
          if (!results.includes(label)) results.push(label);
        }
      }
      setCityResults(results);
    } catch {
      // ağ hatası — sessizce geç
    } finally {
      setCityLoading(false);
    }
  }

  function selectCity(city: string) {
    setBirthPlace(city);
    setCityQuery(city);
    setCityResults([]);
  }

  async function handleSave() {
    if (!name.trim() || !birthDate || !birthTime || !birthPlace.trim()) {
      Alert.alert('Eksik Bilgi', 'Lütfen tüm alanları doldurun.');
      return;
    }
    setSaving(true);
    const person = await createPerson({
      name: name.trim(),
      birthDate,
      birthTime,
      birthPlace: birthPlace.trim(),
    });
    setSaving(false);
    if (person) {
      router.replace((returnTo as any) ?? '/(tabs)');
    } else {
      Alert.alert('Hata', 'Kişi kaydedilemedi. Lütfen tekrar deneyin.');
    }
  }

  return (
    <SafeAreaView style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.iconBtn}>
          <Ionicons name="close" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={styles.title}>Kişi Ekle</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView
        contentContainerStyle={styles.container}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        {/* İsim */}
        <View style={styles.fieldWrap}>
          <Text style={styles.label}>İsim Soyisim</Text>
          <TextInput
            style={styles.input}
            placeholder="Ahmet Yılmaz"
            placeholderTextColor={colors.textMuted}
            value={name}
            onChangeText={setName}
          />
        </View>

        {/* Doğum Tarihi */}
        <View style={styles.fieldWrap}>
          <Text style={styles.label}>Doğum Tarihi</Text>
          <TouchableOpacity style={styles.pickerBtn} onPress={() => setShowDate(true)}>
            <Ionicons name="calendar-outline" size={18} color={colors.textSecondary} />
            <Text style={[styles.pickerText, !birthDate && styles.placeholder]}>
              {birthDate ? displayDate(birthDate) : 'Tarih seç'}
            </Text>
            <Ionicons name="chevron-down" size={16} color={colors.textSecondary} />
          </TouchableOpacity>
        </View>

        {/* Doğum Saati */}
        <View style={styles.fieldWrap}>
          <Text style={styles.label}>Doğum Saati</Text>
          <TouchableOpacity style={styles.pickerBtn} onPress={() => setShowTime(true)}>
            <Ionicons name="time-outline" size={18} color={colors.textSecondary} />
            <Text style={[styles.pickerText, !birthTime && styles.placeholder]}>
              {birthTime || 'Saat seç'}
            </Text>
            <Ionicons name="chevron-down" size={16} color={colors.textSecondary} />
          </TouchableOpacity>
        </View>

        {/* Doğum Şehri */}
        <View style={styles.fieldWrap}>
          <Text style={styles.label}>Doğum Şehri</Text>
          <View>
            <View style={styles.cityInputRow}>
              <TextInput
                style={[styles.input, { flex: 1 }]}
                placeholder="Şehir ara... (örn: Ankara)"
                placeholderTextColor={colors.textMuted}
                value={cityQuery}
                onChangeText={onCityInput}
                autoCorrect={false}
                autoCapitalize="words"
              />
              {cityLoading && (
                <ActivityIndicator
                  size="small"
                  color={colors.primary}
                  style={styles.citySpinner}
                />
              )}
            </View>
            {cityResults.length > 0 && (
              <View style={styles.dropdown}>
                {cityResults.map((city, i) => (
                  <TouchableOpacity
                    key={i}
                    style={[styles.dropItem, i < cityResults.length - 1 && styles.dropBorder]}
                    onPress={() => selectCity(city)}
                  >
                    <Ionicons name="location-outline" size={13} color={colors.primary} />
                    <Text style={styles.dropText}>{city}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            )}
          </View>
        </View>

        <AstroButton title="Kaydet" onPress={handleSave} loading={saving} style={styles.saveBtn} />
      </ScrollView>

      {/* iOS Date Picker Modal */}
      {Platform.OS === 'ios' && showDate && (
        <Modal transparent animationType="slide">
          <View style={styles.overlay}>
            <View style={styles.sheet}>
              <View style={styles.sheetHeader}>
                <Text style={styles.sheetTitle}>Doğum Tarihi</Text>
                <TouchableOpacity onPress={onDateDone}>
                  <Text style={styles.doneBtn}>Tamam</Text>
                </TouchableOpacity>
              </View>
              <DateTimePicker
                value={dateVal}
                mode="date"
                display="spinner"
                onChange={onDateChange}
                maximumDate={new Date()}
                minimumDate={new Date(1900, 0, 1)}
                style={styles.picker}
              />
            </View>
          </View>
        </Modal>
      )}

      {/* Android Date Picker */}
      {Platform.OS === 'android' && showDate && (
        <DateTimePicker
          value={dateVal}
          mode="date"
          display="default"
          onChange={onDateChange}
          maximumDate={new Date()}
          minimumDate={new Date(1900, 0, 1)}
        />
      )}

      {/* iOS Time Picker — ayrı component, parent re-render'dan izole */}
      {Platform.OS === 'ios' && showTime && (
        <TimeSheet
          initialHour={lastHour}
          initialMinute={lastMinute}
          onConfirm={(h, m) => {
            setLastHour(h);
            setLastMinute(m);
            setBirthTime(`${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`);
            setShowTime(false);
          }}
        />
      )}

      {/* Android Time Picker */}
      {Platform.OS === 'android' && showTime && (
        <DateTimePicker
          value={timeVal}
          mode="time"
          display="default"
          is24Hour
          onChange={(_, selected) => {
            setShowTime(false);
            if (selected) {
              const h = selected.getHours();
              const m = selected.getMinutes();
              setTimeVal(selected);
              setLastHour(h);
              setLastMinute(m);
              setBirthTime(
                `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
              );
            }
          }}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.background },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  iconBtn: { width: 40, height: 40, alignItems: 'center', justifyContent: 'center' },
  title: { fontSize: 17, fontWeight: '700', color: colors.text },
  container: { padding: 24, paddingBottom: 48 },
  fieldWrap: { marginBottom: 20 },
  label: { fontSize: 13, color: colors.textSecondary, marginBottom: 8, fontWeight: '500' },
  input: {
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.cardBorder,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    color: colors.text,
    fontSize: 15,
  },
  pickerBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.cardBorder,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    gap: 10,
  },
  pickerText: { flex: 1, fontSize: 15, color: colors.text },
  placeholder: { color: colors.textMuted },
  cityInputRow: { flexDirection: 'row', alignItems: 'center' },
  citySpinner: { position: 'absolute', right: 14 },
  dropdown: {
    marginTop: 4,
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.cardBorder,
    borderRadius: 12,
    overflow: 'hidden',
  },
  dropItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    paddingVertical: 13,
    gap: 8,
  },
  dropBorder: { borderBottomWidth: 1, borderBottomColor: colors.border },
  dropText: { fontSize: 14, color: colors.text, flex: 1 },
  saveBtn: { marginTop: 8 },

  // Modal
  overlay: {
    flex: 1,
    justifyContent: 'flex-end',
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  sheet: {
    backgroundColor: colors.surface,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    paddingBottom: 32,
  },
  sheetHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  sheetTitle: { fontSize: 16, fontWeight: '600', color: colors.text },
  doneBtn: { fontSize: 16, fontWeight: '700', color: colors.primary },
  picker: { backgroundColor: colors.surface },
});
