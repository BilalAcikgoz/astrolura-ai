import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, SafeAreaView, ScrollView,
  TouchableOpacity, Alert, ActivityIndicator,
} from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../../../constants/colors';
import { usePersons } from '../../../hooks/usePersons';
import { useAuth } from '../../../context/AuthContext';
import LoadingSpinner from '../../../components/ui/LoadingSpinner';
import AstroButton from '../../../components/ui/AstroButton';
import NatalChartWheel from '../../../components/chart/NatalChartWheel';
import HousesTable from '../../../components/tables/HousesTable';
import PlanetsTable from '../../../components/tables/PlanetsTable';
import DiginitiesTable from '../../../components/tables/DiginitiesTable';
import AspectsTable from '../../../components/tables/AspectsTable';
import ElementsPieChart from '../../../components/elements/ElementsPieChart';
import QualitiesPieChart from '../../../components/elements/QualitiesPieChart';
import MarkdownRenderer from '../../../components/ui/MarkdownRenderer';
import { calculateBirthChart, interpretBirthChart } from '../../../services/api/birthChart';
import { saveBirthChart, loadBirthChart } from '../../../services/storage/chartCache';
import {
  saveNatalChart,
  getNatalChart,
  saveNatalInterpretation,
} from '../../../services/firebase/charts';
import { BirthChartData } from '../../../types/chart.types';

const TABS = ['Harita', 'Tablolar', 'Elementler', 'Astrology-AI'] as const;
type Tab = typeof TABS[number];

export default function BirthChartDetail() {
  const { personId } = useLocalSearchParams<{ personId: string }>();
  const { persons, loading: personsLoading } = usePersons();
  const { user } = useAuth();

  const [activeTab, setActiveTab] = useState<Tab>('Harita');
  const [chartData, setChartData] = useState<BirthChartData | null>(null);
  const [chartId, setChartId] = useState<string | null>(null);
  const [loadingChart, setLoadingChart] = useState(false);
  const [interpretation, setInterpretation] = useState<string | null>(null);
  const [loadingAI, setLoadingAI] = useState(false);

  const person = persons.find((p) => p.id === personId);

  const fetchChart = useCallback(async () => {
    if (!person) return;
    setLoadingChart(true);
    try {
      // 1. AsyncStorage cache
      const cached = await loadBirthChart(person.id);
      if (cached) {
        setChartData(cached.data);
        setChartId(cached.chartId);
        setLoadingChart(false);
        return;
      }
      // 2. Firestore
      if (user) {
        const stored = await getNatalChart(user.uid, person.id);
        if (stored) {
          setChartData(stored.data);
          setChartId(stored.chartId);
          if (stored.interpretation) setInterpretation(stored.interpretation);
          await saveBirthChart(person.id, stored.chartId, stored.data);
          setLoadingChart(false);
          return;
        }
      }
      // 3. Backend'den hesapla
      const res = await calculateBirthChart(
        person.name, person.birthDate, person.birthTime, person.birthPlace
      );
      setChartData(res.chart_data);
      setChartId(res.chart_id);
      await saveBirthChart(person.id, res.chart_id, res.chart_data);
      if (user) await saveNatalChart(user.uid, person.id, res.chart_id, res.chart_data);
    } catch {
      Alert.alert('Hata', 'Harita hesaplanamadı. Backend çalışıyor mu? (.env dosyasındaki IP adresini kontrol edin)');
    } finally {
      setLoadingChart(false);
    }
  }, [person, user]);

  useEffect(() => {
    if (person) fetchChart();
  }, [person]);

  async function handleInterpret() {
    if (!chartId) return;
    setLoadingAI(true);
    try {
      const res = await interpretBirthChart(chartId, 'detailed', 'tr');
      setInterpretation(res.interpretation);
      if (user && person) {
        await saveNatalInterpretation(user.uid, person.id, res.interpretation);
      }
    } catch {
      Alert.alert('Hata', 'Yorum alınamadı. Lütfen tekrar deneyin.');
    } finally {
      setLoadingAI(false);
    }
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
        <TouchableOpacity onPress={fetchChart} style={styles.refreshBtn}>
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
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tabScroll} contentContainerStyle={styles.tabContainer}>
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
      {loadingChart ? (
        <LoadingSpinner message="Harita hesaplanıyor..." />
      ) : !chartData ? (
        <View style={styles.errorView}>
          <Text style={styles.errorText}>Harita yüklenemedi.</Text>
          <AstroButton title="Tekrar Dene" onPress={fetchChart} variant="outline" style={{ marginTop: 16 }} />
        </View>
      ) : (
        <ScrollView style={styles.content} contentContainerStyle={styles.contentInner} showsVerticalScrollIndicator={false}>
          {activeTab === 'Harita' && (
            <View style={styles.chartWrap}>
              <NatalChartWheel chartData={chartData} />
              <View style={styles.chartLegend}>
                <View style={styles.legendItem}>
                  <View style={[styles.legendDot, { backgroundColor: '#60A5FA' }]} />
                  <Text style={styles.legendText}>ASC (Yükselen)</Text>
                </View>
                <View style={styles.legendItem}>
                  <View style={[styles.legendDot, { backgroundColor: colors.accent }]} />
                  <Text style={styles.legendText}>MC (Orta Gök)</Text>
                </View>
              </View>
            </View>
          )}

          {activeTab === 'Tablolar' && (
            <View style={styles.tableWrap}>
              <HousesTable houses={chartData.houses} />
              <PlanetsTable planets={chartData.planets} />
              <DiginitiesTable dignities={chartData.dignities} />
              <AspectsTable aspects={chartData.aspects} />
            </View>
          )}

          {activeTab === 'Elementler' && (
            <View style={styles.elementsWrap}>
              <ElementsPieChart elements={chartData.elements} />
              <QualitiesPieChart qualities={chartData.qualities} />
            </View>
          )}

          {activeTab === 'Astrology-AI' && (
            <View style={styles.aiWrap}>
              {!interpretation && !loadingAI && (
                <View style={styles.aiPrompt}>
                  <Text style={styles.aiIcon}>✦</Text>
                  <Text style={styles.aiTitle}>Haritanı Yorumlat</Text>
                  <Text style={styles.aiSub}>
                    Yapay zeka, doğum haritanı astrolojik bilgi tabanıyla analiz ederek
                    kişiselleştirilmiş bir yorum oluşturacak.
                  </Text>
                  <AstroButton
                    title="Haritamı Yorumla"
                    onPress={handleInterpret}
                    style={styles.aiBtn}
                  />
                </View>
              )}
              {loadingAI && (
                <View style={styles.aiLoading}>
                  <ActivityIndicator size="large" color={colors.primary} />
                  <Text style={styles.aiLoadingText}>Yorum oluşturuluyor...</Text>
                  <Text style={styles.aiLoadingSubText}>Bu işlem 15-30 saniye sürebilir</Text>
                </View>
              )}
              {interpretation && !loadingAI && (
                <View style={styles.aiResult}>
                  <View style={styles.aiResultHeader}>
                    <Text style={styles.aiResultTitle}>Astroloji Yorumu</Text>
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
  tabScroll: { maxHeight: 48, borderBottomWidth: 1, borderBottomColor: colors.border },
  tabContainer: { paddingHorizontal: 16, gap: 4, alignItems: 'center', paddingVertical: 6 },
  tab: {
    paddingHorizontal: 16, paddingVertical: 7, borderRadius: 20,
    backgroundColor: colors.surface,
  },
  tabActive: { backgroundColor: colors.primary },
  tabText: { fontSize: 13, fontWeight: '500', color: colors.textSecondary },
  tabTextActive: { color: '#fff', fontWeight: '700' },
  content: { flex: 1 },
  contentInner: { padding: 16 },
  errorView: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  errorText: { color: colors.textSecondary, fontSize: 15 },
  chartWrap: { alignItems: 'center', gap: 16 },
  chartLegend: { flexDirection: 'row', gap: 20, paddingTop: 8 },
  legendItem: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  legendDot: { width: 8, height: 8, borderRadius: 4 },
  legendText: { fontSize: 12, color: colors.textSecondary },
  tableWrap: { paddingBottom: 16 },
  elementsWrap: { paddingBottom: 16 },
  aiWrap: { flex: 1, paddingBottom: 16 },
  aiPrompt: { alignItems: 'center', paddingTop: 32, gap: 12 },
  aiIcon: { fontSize: 48, color: colors.accent },
  aiTitle: { fontSize: 20, fontWeight: '700', color: colors.text },
  aiSub: { fontSize: 14, color: colors.textSecondary, textAlign: 'center', lineHeight: 20, paddingHorizontal: 16 },
  aiBtn: { marginTop: 8, minWidth: 200 },
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
