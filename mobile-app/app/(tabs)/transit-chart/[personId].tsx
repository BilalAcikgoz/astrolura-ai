import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, SafeAreaView, ScrollView,
  TouchableOpacity, Alert, ActivityIndicator, TextInput,
} from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../../../constants/colors';
import { usePersons } from '../../../hooks/usePersons';
import { useAuth } from '../../../context/AuthContext';
import LoadingSpinner from '../../../components/ui/LoadingSpinner';
import AstroButton from '../../../components/ui/AstroButton';
import TransitChartWheel from '../../../components/chart/TransitChartWheel';
import HousesTable from '../../../components/tables/HousesTable';
import PlanetsTable from '../../../components/tables/PlanetsTable';
import DiginitiesTable from '../../../components/tables/DiginitiesTable';
import TransitPlanetsTable from '../../../components/tables/TransitPlanetsTable';
import TransitAspectsTable from '../../../components/tables/TransitAspectsTable';
import MarkdownRenderer from '../../../components/ui/MarkdownRenderer';
import { calculateBirthChart } from '../../../services/api/birthChart';
import { calculateTransitChart, interpretTransitChart } from '../../../services/api/transitChart';
import {
  saveBirthChart, loadBirthChart,
  saveTransitChart as saveTransitChartCache,
  loadTransitChart,
} from '../../../services/storage/chartCache';
import {
  saveNatalChart,
  getNatalChart,
  saveTransitChart as saveTransitChartFS,
  getTransitChart,
  saveTransitInterpretation,
} from '../../../services/firebase/charts';
import { BirthChartData, TransitChartResponse } from '../../../types/chart.types';

const TABS = ['Harita', 'Tablolar', 'Astrology-AI'] as const;
type Tab = typeof TABS[number];

/** Bugünün tarih stringini YYYY-MM-DD formatında döndür */
function todayStr() {
  return new Date().toISOString().split('T')[0];
}

/** Şu anın saat stringini HH:MM formatında döndür */
function nowTimeStr() {
  const d = new Date();
  const h = String(d.getHours()).padStart(2, '0');
  const m = String(d.getMinutes()).padStart(2, '0');
  return `${h}:${m}`;
}

/** Date'den {year, month, day, hour, minute} objesi çıkar */
function dateToFields(d: Date) {
  return {
    year:   String(d.getFullYear()),
    month:  String(d.getMonth() + 1).padStart(2, '0'),
    day:    String(d.getDate()).padStart(2, '0'),
    hour:   String(d.getHours()).padStart(2, '0'),
    minute: String(d.getMinutes()).padStart(2, '0'),
  };
}

interface DateFields { year: string; month: string; day: string; hour: string; minute: string }

/** DateFields → 'YYYY-MM-DD' */
function fieldsToDateStr(f: DateFields) {
  return `${f.year}-${f.month.padStart(2,'0')}-${f.day.padStart(2,'0')}`;
}

/** DateFields → 'HH:MM' */
function fieldsToTimeStr(f: DateFields) {
  return `${f.hour.padStart(2,'0')}:${f.minute.padStart(2,'0')}`;
}

export default function TransitChartDetail() {
  const { personId } = useLocalSearchParams<{ personId: string }>();
  const { persons, loading: personsLoading } = usePersons();
  const { user } = useAuth();

  const [activeTab, setActiveTab] = useState<Tab>('Harita');
  const [natalData, setNatalData] = useState<BirthChartData | null>(null);
  const [chartId, setChartId] = useState<string | null>(null);
  const [transitData, setTransitData] = useState<TransitChartResponse | null>(null);
  const [transitId, setTransitId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [interpretation, setInterpretation] = useState<string | null>(null);
  const [loadingAI, setLoadingAI] = useState(false);

  // Tarih & saat alanları — varsayılan: şu an
  const [dateFields, setDateFields] = useState<DateFields>(() => dateToFields(new Date()));

  const person = persons.find((p) => p.id === personId);

  const fetchData = useCallback(async (dateStr: string, timeStr: string) => {
    if (!person) return;
    setLoading(true);
    try {
      // ── Natal chart ──────────────────────────────────────
      let nChart: BirthChartData;
      let cId: string;

      const cachedNatal = await loadBirthChart(person.id);
      if (cachedNatal) {
        nChart = cachedNatal.data;
        cId = cachedNatal.chartId;
      } else if (user) {
        const stored = await getNatalChart(user.uid, person.id);
        if (stored) {
          nChart = stored.data;
          cId = stored.chartId;
          await saveBirthChart(person.id, cId, nChart);
        } else {
          const res = await calculateBirthChart(
            person.name, person.birthDate, person.birthTime, person.birthPlace
          );
          nChart = res.chart_data;
          cId = res.chart_id;
          await saveBirthChart(person.id, cId, nChart);
          await saveNatalChart(user.uid, person.id, cId, nChart);
        }
      } else {
        const res = await calculateBirthChart(
          person.name, person.birthDate, person.birthTime, person.birthPlace
        );
        nChart = res.chart_data;
        cId = res.chart_id;
        await saveBirthChart(person.id, cId, nChart);
      }
      setNatalData(nChart!);
      setChartId(cId!);

      // ── Transit chart — seçilen tarih & saat ile ──────────
      const tRes = await calculateTransitChart(cId!, dateStr, timeStr);
      setTransitData(tRes);
      setTransitId(tRes.transit_id);
      await saveTransitChartCache(person.id, dateStr, tRes.transit_id, tRes);
      if (user) await saveTransitChartFS(user.uid, person.id, tRes.transit_id, dateStr, tRes);

    } catch {
      Alert.alert('Hata', 'Harita hesaplanamadı. Backend çalışıyor mu?');
    } finally {
      setLoading(false);
    }
  }, [person, user]);

  useEffect(() => {
    if (person) {
      fetchData(fieldsToDateStr(dateFields), fieldsToTimeStr(dateFields));
    }
  }, [person]);

  async function handleInterpret() {
    if (!transitId) return;
    setLoadingAI(true);
    try {
      const res = await interpretTransitChart(transitId, 'tr');
      setInterpretation(res.interpretation);
      if (user && person) {
        await saveTransitInterpretation(user.uid, person.id, res.interpretation);
      }
    } catch {
      Alert.alert('Hata', 'Yorum alınamadı. Lütfen tekrar deneyin.');
    } finally {
      setLoadingAI(false);
    }
  }

  /** Tarih/saat değişince haritayı yeniden hesapla */
  function handleRecalculate() {
    fetchData(fieldsToDateStr(dateFields), fieldsToTimeStr(dateFields));
  }

  if (personsLoading || !person) return <LoadingSpinner message="Yükleniyor..." />;

  return (
    <SafeAreaView style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="chevron-back" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{person.name}</Text>
        <TouchableOpacity
          onPress={handleRecalculate}
          style={styles.refreshBtn}
          disabled={loading}
        >
          <Ionicons name="refresh" size={20} color={colors.textSecondary} />
        </TouchableOpacity>
      </View>

      {/* Kişi bilgi paneli */}
      <View style={styles.personPanel}>
        <View style={styles.personRow}>
          <Ionicons name="calendar-outline" size={13} color={colors.textSecondary} style={styles.panelIcon} />
          <Text style={styles.panelText}>{person.birthDate}</Text>
          <Text style={styles.panelSep}>•</Text>
          <Ionicons name="time-outline" size={13} color={colors.textSecondary} style={styles.panelIcon} />
          <Text style={styles.panelText}>{person.birthTime}</Text>
          <Text style={styles.panelSep}>•</Text>
          <Ionicons name="location-outline" size={13} color={colors.textSecondary} style={styles.panelIcon} />
          <Text style={styles.panelText} numberOfLines={1}>{person.birthPlace}</Text>
        </View>
      </View>

      {/* Tab Bar */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.tabScroll}
        contentContainerStyle={styles.tabContainer}
      >
        {TABS.map((tab) => (
          <TouchableOpacity
            key={tab}
            style={[styles.tab, activeTab === tab && styles.tabActive]}
            onPress={() => setActiveTab(tab)}
          >
            <Text style={[styles.tabText, activeTab === tab && styles.tabTextActive]}>{tab}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Content */}
      {loading ? (
        <LoadingSpinner message="Transit harita hesaplanıyor..." />
      ) : !natalData || !transitData ? (
        <View style={styles.errorView}>
          <Text style={styles.errorText}>Harita yüklenemedi.</Text>
          <AstroButton title="Tekrar Dene" onPress={handleRecalculate} variant="outline" style={{ marginTop: 16 }} />
        </View>
      ) : (
        <ScrollView style={styles.content} contentContainerStyle={styles.contentInner} showsVerticalScrollIndicator={false}>
          {activeTab === 'Harita' && (
            <View style={styles.chartWrap}>
              <TransitChartWheel natalData={natalData} transitData={transitData} />
              <View style={styles.chartLegend}>
                <View style={styles.legendItem}>
                  <View style={[styles.legendDot, { backgroundColor: '#888' }]} />
                  <Text style={styles.legendText}>Transit gezegenler (dış)</Text>
                </View>
                <View style={styles.legendItem}>
                  <View style={[styles.legendDot, { backgroundColor: colors.primary }]} />
                  <Text style={styles.legendText}>Natal gezegenler (iç)</Text>
                </View>
              </View>
            </View>
          )}

          {activeTab === 'Tablolar' && (
            <View style={styles.tableWrap}>
              <HousesTable houses={natalData.houses} />
              <PlanetsTable planets={natalData.planets} title="Natal" />
              <DiginitiesTable dignities={natalData.dignities} />
              <View style={styles.divider} />
              <TransitPlanetsTable planets={transitData.transit_planets} />
              <TransitAspectsTable
                aspects={transitData.transit_aspects}
                personName={person.name}
              />
            </View>
          )}

          {activeTab === 'Astrology-AI' && (
            <View style={styles.aiWrap}>
              {!interpretation && !loadingAI && (
                <View style={styles.aiPrompt}>
                  <Text style={styles.aiIcon}>✦</Text>
                  <Text style={styles.aiTitle}>Transit Yorumu Al</Text>
                  <Text style={styles.aiSub}>
                    Seçilen tarihin transit hareketlerinin natal haritaya etkisini yapay zeka ile analiz et.
                  </Text>
                  <AstroButton title="Transitlerimi Yorumla" onPress={handleInterpret} style={styles.aiBtn} />
                </View>
              )}
              {loadingAI && (
                <View style={styles.aiLoading}>
                  <ActivityIndicator size="large" color={colors.primary} />
                  <Text style={styles.aiLoadingText}>Transit yorumu oluşturuluyor...</Text>
                  <Text style={styles.aiLoadingSubText}>Bu işlem 15-30 saniye sürebilir</Text>
                </View>
              )}
              {interpretation && !loadingAI && (
                <View style={styles.aiResult}>
                  <View style={styles.aiResultHeader}>
                    <Text style={styles.aiResultTitle}>Transit Yorumu</Text>
                    <TouchableOpacity onPress={handleInterpret}>
                      <Ionicons name="refresh" size={18} color={colors.textSecondary} />
                    </TouchableOpacity>
                  </View>
                  <MarkdownRenderer content={interpretation} />
                </View>
              )}
            </View>
          )}
        </ScrollView>
      )}

      {/* Tarih & Saat Seçici — Ekranın Altında Sabit */}
      <View style={styles.dateBar}>
        <View style={styles.dateFields}>
          <View style={styles.fieldWrap}>
            <TextInput
              style={styles.fieldInput}
              value={dateFields.year}
              onChangeText={(v) => setDateFields((f) => ({ ...f, year: v }))}
              keyboardType="number-pad"
              maxLength={4}
              selectTextOnFocus
            />
          </View>
          <View style={styles.fieldWrap}>
            <TextInput
              style={styles.fieldInput}
              value={dateFields.month}
              onChangeText={(v) => setDateFields((f) => ({ ...f, month: v }))}
              keyboardType="number-pad"
              maxLength={2}
              selectTextOnFocus
            />
          </View>
          <View style={styles.fieldWrap}>
            <TextInput
              style={styles.fieldInput}
              value={dateFields.day}
              onChangeText={(v) => setDateFields((f) => ({ ...f, day: v }))}
              keyboardType="number-pad"
              maxLength={2}
              selectTextOnFocus
            />
          </View>
          <View style={styles.fieldWrap}>
            <TextInput
              style={styles.fieldInput}
              value={dateFields.hour}
              onChangeText={(v) => setDateFields((f) => ({ ...f, hour: v }))}
              keyboardType="number-pad"
              maxLength={2}
              selectTextOnFocus
            />
          </View>
          <View style={styles.fieldWrap}>
            <TextInput
              style={styles.fieldInput}
              value={dateFields.minute}
              onChangeText={(v) => setDateFields((f) => ({ ...f, minute: v }))}
              keyboardType="number-pad"
              maxLength={2}
              selectTextOnFocus
            />
          </View>
        </View>
        <View style={styles.dateActions}>
          <TouchableOpacity
            style={styles.nowBtn}
            onPress={() => setDateFields(dateToFields(new Date()))}
          >
            <Text style={styles.nowBtnText}>Şimdi</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.calcBtn, loading && styles.calcBtnDisabled]}
            onPress={handleRecalculate}
            disabled={loading}
          >
            {loading
              ? <ActivityIndicator size="small" color="#fff" />
              : <Text style={styles.calcBtnText}>Hesapla</Text>
            }
          </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.background },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    gap: 8,
  },
  backBtn: { padding: 4 },
  refreshBtn: { padding: 4 },
  headerTitle: { flex: 1, fontSize: 17, fontWeight: '700', color: colors.text },
  // Kişi bilgi paneli
  personPanel: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  personRow: { flexDirection: 'row', alignItems: 'center', flexWrap: 'wrap', gap: 4 },
  panelIcon: { marginRight: 2 },
  panelText: { fontSize: 12, color: colors.textSecondary },
  panelSep: { fontSize: 12, color: colors.border, marginHorizontal: 4 },
  // Tab bar
  tabScroll: { maxHeight: 48, borderBottomWidth: 1, borderBottomColor: colors.border },
  tabContainer: { paddingHorizontal: 16, gap: 4, alignItems: 'center', paddingVertical: 6 },
  tab: { paddingHorizontal: 16, paddingVertical: 7, borderRadius: 20, backgroundColor: colors.surface },
  tabActive: { backgroundColor: colors.accent },
  tabText: { fontSize: 13, fontWeight: '500', color: colors.textSecondary },
  tabTextActive: { color: '#fff', fontWeight: '700' },
  // Tarih & saat seçici — ekranın en altında sabit
  dateBar: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: colors.card,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    gap: 8,
  },
  dateFields: { flexDirection: 'row', justifyContent: 'space-between', gap: 6 },
  fieldWrap: { flex: 1, alignItems: 'center' },
  fieldInput: {
    backgroundColor: colors.surface,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
    color: colors.text,
    fontSize: 16,
    fontWeight: '700',
    textAlign: 'center',
    paddingVertical: 8,
    width: '100%',
  },
  dateActions: { flexDirection: 'row', gap: 8 },
  nowBtn: {
    flex: 1,
    backgroundColor: colors.surface,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'center',
    paddingVertical: 8,
  },
  nowBtnText: { fontSize: 13, fontWeight: '600', color: colors.textSecondary },
  calcBtn: {
    flex: 2,
    backgroundColor: colors.primary,
    borderRadius: 10,
    alignItems: 'center',
    paddingVertical: 8,
  },
  calcBtnDisabled: { opacity: 0.6 },
  calcBtnText: { fontSize: 13, fontWeight: '700', color: '#fff' },
  // Content
  content: { flex: 1 },
  contentInner: { padding: 16, paddingBottom: 24 },
  errorView: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  errorText: { color: colors.textSecondary, fontSize: 15 },
  chartWrap: { alignItems: 'center', gap: 16 },
  chartLegend: { flexDirection: 'row', gap: 16, paddingTop: 8, flexWrap: 'wrap', justifyContent: 'center' },
  legendItem: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  legendDot: { width: 8, height: 8, borderRadius: 4 },
  legendText: { fontSize: 12, color: colors.textSecondary },
  tableWrap: { paddingBottom: 16 },
  divider: { height: 1, backgroundColor: colors.border, marginVertical: 20 },
  aiWrap: { flex: 1, paddingBottom: 16 },
  aiPrompt: { alignItems: 'center', paddingTop: 32, gap: 12 },
  aiIcon: { fontSize: 48, color: colors.accent },
  aiTitle: { fontSize: 20, fontWeight: '700', color: colors.text },
  aiSub: { fontSize: 14, color: colors.textSecondary, textAlign: 'center', lineHeight: 20, paddingHorizontal: 16 },
  aiBtn: { marginTop: 8, minWidth: 220 },
  aiLoading: { alignItems: 'center', paddingTop: 48, gap: 12 },
  aiLoadingText: { fontSize: 16, color: colors.text, fontWeight: '600' },
  aiLoadingSubText: { fontSize: 13, color: colors.textSecondary },
  aiResult: { flex: 1 },
  aiResultHeader: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    marginBottom: 16, paddingBottom: 12, borderBottomWidth: 1, borderBottomColor: colors.border,
  },
  aiResultTitle: { fontSize: 16, fontWeight: '700', color: colors.accent },
});
