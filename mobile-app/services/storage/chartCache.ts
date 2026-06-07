import AsyncStorage from '@react-native-async-storage/async-storage';
import { BirthChartData, TransitChartResponse } from '../../types/chart.types';

const BIRTH_KEY = (personId: string) => `birth_chart_${personId}`;
const TRANSIT_KEY = (personId: string, date: string) => `transit_chart_${personId}_${date}`;

export async function saveBirthChart(personId: string, chartId: string, data: BirthChartData) {
  await AsyncStorage.setItem(BIRTH_KEY(personId), JSON.stringify({ chartId, data }));
}

export async function loadBirthChart(personId: string): Promise<{ chartId: string; data: BirthChartData } | null> {
  const raw = await AsyncStorage.getItem(BIRTH_KEY(personId));
  return raw ? JSON.parse(raw) : null;
}

export async function saveTransitChart(personId: string, date: string, transitId: string, data: TransitChartResponse) {
  await AsyncStorage.setItem(TRANSIT_KEY(personId, date), JSON.stringify({ transitId, data }));
}

export async function loadTransitChart(personId: string, date: string): Promise<{ transitId: string; data: TransitChartResponse } | null> {
  const raw = await AsyncStorage.getItem(TRANSIT_KEY(personId, date));
  return raw ? JSON.parse(raw) : null;
}

export async function clearBirthChart(personId: string) {
  await AsyncStorage.removeItem(BIRTH_KEY(personId));
}
