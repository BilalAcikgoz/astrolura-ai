import { doc, setDoc, getDoc, updateDoc } from 'firebase/firestore';
import { db } from '../../firebase.config';
import { BirthChartData, TransitChartResponse } from '../../types/chart.types';

// ─── Natal Chart ─────────────────────────────────────────────────────────────

function natalRef(uid: string, personId: string) {
  return doc(db, 'users', uid, 'natal_charts', personId);
}

export async function saveNatalChart(
  uid: string,
  personId: string,
  chartId: string,
  data: BirthChartData
): Promise<void> {
  await setDoc(natalRef(uid, personId), {
    chartId,
    chartInfo: data.chart_info,
    houses: data.houses,
    planets: data.planets,
    aspects: data.aspects,
    dignities: data.dignities,
    elements: data.elements,
    qualities: data.qualities,
    interpretation: null,
    interpretationDate: null,
    calculatedAt: Date.now(),
  });
}

export async function getNatalChart(
  uid: string,
  personId: string
): Promise<{ chartId: string; data: BirthChartData; interpretation: string | null } | null> {
  const snap = await getDoc(natalRef(uid, personId));
  if (!snap.exists()) return null;
  const d = snap.data();
  return {
    chartId: d.chartId,
    interpretation: d.interpretation ?? null,
    data: {
      chart_info: d.chartInfo,
      houses: d.houses,
      planets: d.planets,
      aspects: d.aspects,
      dignities: d.dignities,
      elements: d.elements,
      qualities: d.qualities,
    } as BirthChartData,
  };
}

export async function saveNatalInterpretation(
  uid: string,
  personId: string,
  text: string
): Promise<void> {
  await updateDoc(natalRef(uid, personId), {
    interpretation: text,
    interpretationDate: Date.now(),
  });
}

// ─── Transit Chart ────────────────────────────────────────────────────────────

function transitRef(uid: string, personId: string) {
  return doc(db, 'users', uid, 'transit_charts', personId);
}

export async function saveTransitChart(
  uid: string,
  personId: string,
  transitId: string,
  date: string,
  data: TransitChartResponse
): Promise<void> {
  await setDoc(transitRef(uid, personId), {
    transitId,
    transitDate: date,
    transitPlanets: data.transit_planets,
    transitAspects: data.transit_aspects,
    interpretation: null,
    interpretationDate: null,
    calculatedAt: Date.now(),
  });
}

export async function getTransitChart(
  uid: string,
  personId: string
): Promise<{ transitId: string; date: string; data: Partial<TransitChartResponse>; interpretation: string | null } | null> {
  const snap = await getDoc(transitRef(uid, personId));
  if (!snap.exists()) return null;
  const d = snap.data();
  return {
    transitId: d.transitId,
    date: d.transitDate,
    interpretation: d.interpretation ?? null,
    data: {
      transit_planets: d.transitPlanets,
      transit_aspects: d.transitAspects,
    },
  };
}

export async function saveTransitInterpretation(
  uid: string,
  personId: string,
  text: string
): Promise<void> {
  await updateDoc(transitRef(uid, personId), {
    interpretation: text,
    interpretationDate: Date.now(),
  });
}
