import client from './client';
import { BirthChartResponse, InterpretationResponse } from '../../types/chart.types';

export async function calculateBirthChart(
  name: string,
  birthDate: string,
  birthTime: string,
  birthPlace: string,
  houseSystem = 'placidus'
): Promise<BirthChartResponse> {
  const res = await client.post('/api/v1/birth-chart/calculate', {
    name,
    birth_date: birthDate,
    birth_time: birthTime,
    birth_place: birthPlace,
    house_system: houseSystem,
  });
  return res.data;
}

export async function interpretBirthChart(
  chartId: string,
  style = 'detailed',
  language = 'tr'
): Promise<InterpretationResponse> {
  const res = await client.post('/api/v1/birth-chart/interpret', {
    chart_id: chartId,
    interpretation_style: style,
    language,
  });
  return res.data;
}

export async function getBirthChart(chartId: string): Promise<BirthChartResponse> {
  const res = await client.get(`/api/v1/birth-chart/${chartId}`);
  return res.data;
}
