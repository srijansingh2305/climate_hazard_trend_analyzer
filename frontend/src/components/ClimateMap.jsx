import React from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import ClickSelectRectangle from './ClickSelectRectangleWithClear';

function ClimateMap({ onBoundsChange }) {
  return (
    <MapContainer
      center={[23, 77]}
      zoom={5}
      scrollWheelZoom={true}
      className="map-container"
    >
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <ClickSelectRectangle onBoundsChange={onBoundsChange} />
    </MapContainer>
  );
}

export default ClimateMap;