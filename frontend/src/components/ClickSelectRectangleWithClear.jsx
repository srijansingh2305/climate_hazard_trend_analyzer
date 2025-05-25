import { useEffect, useState } from 'react';
import { useMapEvents, Rectangle, useMap } from 'react-leaflet';

function ClickSelectRectangle({ onBoundsChange }) {
  const [corner1, setCorner1] = useState(null);
  const [corner2, setCorner2] = useState(null);
  useMap();

  useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng;

      if (!corner1) {
        setCorner1([lat, lng]);
        setCorner2(null);
      } else {
        setCorner2([lat, lng]);
      }
    }
  });

  useEffect(() => {
    if (corner1 && corner2) {
      const south = Math.min(corner1[0], corner2[0]);
      const north = Math.max(corner1[0], corner2[0]);
      const west = Math.min(corner1[1], corner2[1]);
      const east = Math.max(corner1[1], corner2[1]);
      const bounds = [south, west, north, east];
      onBoundsChange(bounds);
    }
  }, [corner1, corner2, onBoundsChange]);

  const handleClear = () => {
    setCorner1(null);
    setCorner2(null);
    onBoundsChange(null);
  };

  return (
    <>
      {corner1 && corner2 && (
        <Rectangle bounds={[corner1, corner2]} pathOptions={{ color: 'blue' }} />
      )}
      {(corner1 || corner2) && (
        <div className="clear-button-container">
          <button className="clear-button" onClick={handleClear}>
            Clear Selection
          </button>
        </div>
      )}
    </>
  );
}

export default ClickSelectRectangle;