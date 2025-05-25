import React from 'react';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  Tooltip, CartesianGrid, Legend,
} from 'recharts';

function Chart({ data }) {
  return (
    <div className="chart-wrapper">
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
    </div>
  );
}

export default Chart;