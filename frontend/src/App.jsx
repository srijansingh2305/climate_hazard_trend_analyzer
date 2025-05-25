import React, { useState, useEffect } from 'react';
import ClimateMap from './components/ClimateMap';
import Chart from './components/Chart';
import { fetchHazardData, downloadHazardReport } from './utils/api';
import './App.css';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';

const predefinedRegions = {
  'Central India': [20, 75, 25, 80],
  'North India': [28, 76, 32, 81],
  'South India': [10, 76, 15, 80],
  'Custom': null,
};

function App() {
  const [bounds, setBounds] = useState(predefinedRegions['Central India']);
  const [selectedRegion, setSelectedRegion] = useState('Central India');
  const [range, setRange] = useState({ start: 1990, end: 2020 });
  const [threshold, setThreshold] = useState(33.5);
  const [hazard, setHazard] = useState('heatwave');
  const [data, setData] = useState([]);
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [downloadLinks, setDownloadLinks] = useState(null);

  useEffect(() => {
    if (hazard === 'heatwave') setThreshold(33.5);
    else if (hazard === 'rainfall' || hazard === 'flood') setThreshold(50);
    else if (hazard === 'drought') setThreshold(100);
  }, [hazard]);

  const fetchData = async () => {
    if (!bounds || bounds.length !== 4 || bounds.some(isNaN)) {
      setError('Please select a valid region.');
      return;
    }

    try {
      setLoading(true);
      setError('');
      const result = await fetchHazardData({ bounds, range, threshold, hazard });
      setData(result.trends || []);
      setSummary(result.summary || '');
    } catch (err) {
      console.error(err);
      setError('Failed to fetch data. Please try again.');
      setData([]);
      setSummary('');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadInsights = async () => {
    try {
      setError('');
      const result = await downloadHazardReport({ bounds, range, threshold, hazard });
      setDownloadLinks(result);
    } catch (err) {
      console.error(err);
      setError('Failed to generate report.');
    }
  };

  const handleRegionChange = (e) => {
    const region = e.target.value;
    setSelectedRegion(region);
    setBounds(predefinedRegions[region]);
  };

  return (
    <div className="container">
      <h1>Climate Hazard Analysis</h1>

      <div className="map-container">
        <ClimateMap onBoundsChange={(b) => {
          setBounds(b);
          setSelectedRegion('Custom');
        }} />
      </div>

      <div className="controls-panel">
        <div>
          <label>Region:</label>
          <select value={selectedRegion} onChange={handleRegionChange}>
            {Object.keys(predefinedRegions).map((region) => (
              <option key={region} value={region}>{region}</option>
            ))}
          </select>
        </div>

        <div>
          <label>Hazard:</label>
          <select value={hazard} onChange={(e) => setHazard(e.target.value)}>
            <option value="heatwave">Heatwave</option>
            <option value="rainfall">Heavy Rainfall</option>
            <option value="flood">Flood</option>
            <option value="drought">Drought</option>
          </select>
        </div>

        <div>
          <label>Year Range:</label>
          <input type="number" value={range.start} onChange={(e) => setRange({ ...range, start: +e.target.value })} />
          <span> - </span>
          <input type="number" value={range.end} onChange={(e) => setRange({ ...range, end: +e.target.value })} />
        </div>

        <div>
          <label>Threshold ({hazard === 'heatwave' ? '°C' : 'mm'}):</label>
          <input type="number" step="0.1" value={threshold} onChange={(e) => setThreshold(+e.target.value)} />
        </div>

        <div className="button-group">
          <button onClick={fetchData} disabled={loading}>
            {loading ? 'Loading...' : 'Fetch Data'}
          </button>
          <button onClick={handleDownloadInsights}>
            Download Insights
          </button>
        </div>
      </div>

      {error && <p className="text-red">{error}</p>}

      {!loading && data.length > 0 ? (
        <Chart data={data} />
      ) : (
        !loading && <p className="text-muted">No data available for this selection.</p>
      )}

      {summary && (
        <p className="summary-text">{summary}</p>
      )}

      {downloadLinks && (
        <div className="download-links">
          <a href={`http://localhost:8000${downloadLinks.csv_url}`} target="_blank" rel="noreferrer">Download CSV</a>
          <a href={`http://localhost:8000${downloadLinks.pdf_url}`} target="_blank" rel="noreferrer">Download PDF</a>
        </div>
      )}
    </div>
  );
}

export default App;