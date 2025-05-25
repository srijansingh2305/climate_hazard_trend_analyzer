import React, { useEffect, useState, useRef } from 'react';
import {
  MapContainer, TileLayer, useMap, FeatureGroup,
} from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import 'leaflet-draw';

import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend, ResponsiveContainer,
} from 'recharts';
import axios from 'axios';

const predefinedRegions = {
  'Central India': [[20, 75], [25, 80]],
  'North India': [[28, 76], [32, 81]],
  'South India': [[10, 76], [15, 80]],
  'Custom': null,
};

function DrawRectangle({ onBoundsChange }) {
  const map = useMap();
  const drawnItemsRef = useRef(new L.FeatureGroup());

  useEffect(() => {
    const drawnItems = drawnItemsRef.current;
    map.addLayer(drawnItems);

    const drawControl = new L.Control.Draw({
      draw: {
        rectangle: true,
        polygon: false,
        circle: false,
        polyline: false,
        marker: false,
        circlemarker: false,
      },
      edit: {
        featureGroup: drawnItems,
        edit: false,
        remove: true,
      },
    });

    map.addControl(drawControl);

    map.on(L.Draw.Event.CREATED, (e) => {
      drawnItems.clearLayers(); // Only keep one shape
      drawnItems.addLayer(e.layer);

      const bounds = e.layer.getBounds();
      const sw = bounds.getSouthWest();
      const ne = bounds.getNorthEast();
      onBoundsChange([[sw.lat, sw.lng], [ne.lat, ne.lng]]);
    });

    return () => {
      map.removeControl(drawControl);
      map.removeLayer(drawnItems);
    };
  }, [map, onBoundsChange]);

  return null;
}

function App() {
  const [data, setData] = useState([]);
  const [summary, setSummary] = useState('');
  const [bounds, setBounds] = useState(predefinedRegions['Central India']);
  const [selectedRegion, setSelectedRegion] = useState('Central India');
  const [range, setRange] = useState({ start: 1990, end: 2020 });
  const [threshold, setThreshold] = useState(33.5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hazard, setHazard] = useState('heatwave');

  useEffect(() => {
    if (hazard === 'heatwave') setThreshold(33.5);
    else if (hazard === 'rainfall' || hazard === 'flood') setThreshold(50);
    else if (hazard === 'drought') setThreshold(100);
  }, [hazard]);

  const fetchData = async () => {
    if (!bounds || bounds.flat().every(coord => coord === 0)) {
      setError('Please select a valid region.');
      return;
    }

    try {
      setLoading(true);
      setError('');
      const response = await axios.post('http://localhost:8000/api/hazards', {
        bounds: bounds.flat(),
        range,
        threshold,
        hazard,
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      setData(response.data.trends || []);
      setSummary(response.data.summary || '');
    } catch (err) {
      console.error(err);
      setError('Failed to fetch data. Please try again later.');
      setData([]);
      setSummary('');
    } finally {
      setLoading(false);
    }
  };

  const handleRegionChange = (e) => {
    const region = e.target.value;
    setSelectedRegion(region);
    setBounds(predefinedRegions[region]);
  };

  return (
    <div className="p-4 font-sans">
      <h1 className="text-xl font-bold mb-4">Climate Hazard Analysis</h1>

      <div style={{ height: '400px' }} className="mb-4 border border-dashed border-gray-400">
        <MapContainer center={[23, 77]} zoom={5} style={{ height: '100%' }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <DrawRectangle onBoundsChange={(b) => {
            setBounds(b);
            setSelectedRegion('Custom');
          }} />
        </MapContainer>
      </div>

      <div className="mb-4 flex flex-wrap items-center justify-center gap-3">
        <div className="flex items-center gap-2">
          <label>Region:</label>
          <select
            value={selectedRegion}
            onChange={handleRegionChange}
            className="p-1 rounded bg-gray-800 text-white"
          >
            {Object.keys(predefinedRegions).map((region) => (
              <option key={region} value={region}>{region}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2">
          <label>Hazard:</label>
          <select
            value={hazard}
            onChange={(e) => setHazard(e.target.value)}
            className="p-1 rounded bg-gray-800 text-white"
          >
            <option value="heatwave">Heatwave</option>
            <option value="rainfall">Heavy Rainfall</option>
            <option value="flood">Flood</option>
            <option value="drought">Drought</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <label>Year Range:</label>
          <input
            type="number"
            className="bg-gray-800 text-white p-1 rounded w-20"
            value={range.start}
            onChange={(e) => setRange({ ...range, start: +e.target.value })}
          />
          <span> - </span>
          <input
            type="number"
            className="bg-gray-800 text-white p-1 rounded w-20"
            value={range.end}
            onChange={(e) => setRange({ ...range, end: +e.target.value })}
          />
        </div>

        <div className="flex items-center gap-2">
          <label>Threshold ({hazard === 'heatwave' ? '°C' : 'mm'}):</label>
          <input
            type="number"
            step="0.1"
            className="bg-gray-800 text-white p-1 rounded w-24"
            value={threshold}
            onChange={(e) => setThreshold(+e.target.value)}
          />
        </div>

        <button
          onClick={fetchData}
          disabled={loading}
          className={`px-4 py-2 rounded text-white ${
            loading ? 'bg-gray-500 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {loading ? 'Loading...' : 'Fetch Data'}
        </button>
      </div>

      {error && <p className="text-red-500 mb-2">{error}</p>}

      {!loading && data.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="frequency" stroke="#8884d8" name="Frequency" />
            <Line type="monotone" dataKey="intensity" stroke="#82ca9d" name="Intensity" />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        !loading && <p className="text-gray-400">No data available for this selection.</p>
      )}

      {summary && (
        <p className="mt-4 text-lg font-semibold text-yellow-300">{summary}</p>
      )}
    </div>
  );
}

export default App;
