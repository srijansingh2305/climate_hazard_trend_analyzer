import axios from 'axios';

const BASE_URL = 'https://climate-hazard-trend-analyzer.onrender.com';

export async function fetchHazardData({ bounds, range, threshold, hazard }) {
  const response = await axios.post(`${BASE_URL}/api/hazards`, {
    bounds,
    range,
    threshold,
    hazard,
  }, {
    headers: { 'Content-Type': 'application/json' }
  });

  return response.data;
}

export async function downloadHazardReport({ bounds, range, threshold, hazard }) {
  const response = await fetch(`${BASE_URL}/api/hazards/export`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ bounds, range, threshold, hazard }),
  });

  if (!response.ok) {
    throw new Error('Failed to generate report.');
  }

  return await response.json(); // contains csv_url and pdf_url
}
