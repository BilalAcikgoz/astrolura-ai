import client from './client';
import { TransitChartResponse, TransitInterpretationResponse } from '../../types/chart.types';

export async function calculateTransitChart(
  chartId: string,
  transitDate?: string,
  transitTime?: string
): Promise<TransitChartResponse> {
  const res = await client.post('/api/v1/transit-chart/calculate', {
    chart_id: chartId,
    ...(transitDate && { transit_date: transitDate }),
    ...(transitTime && { transit_time: transitTime }),
  });
  return res.data;
}

export async function interpretTransitChart(
  transitId: string,
  language = 'tr'
): Promise<TransitInterpretationResponse> {
  const res = await client.post('/api/v1/transit-chart/interpret', {
    transit_id: transitId,
    language,
  });
  return res.data;
}

export async function getTransitChart(transitId: string): Promise<TransitChartResponse> {
  const res = await client.get(`/api/v1/transit-chart/${transitId}`);
  return res.data;
}
