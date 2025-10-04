export const deg2num = (lat: number, lon: number, zoom: number) => {
  const latRad = lat * Math.PI / 180;
  const n = Math.pow(2, zoom);
  const x = Math.floor((lon + 180) / 360 * n);
  const y = Math.floor((1 - Math.asinh(Math.tan(latRad)) / Math.PI) / 2 * n);
  return { x, y };
};

export const calculateTilesAtZoom = (west: number, south: number, east: number, north: number, zoom: number) => {
  const minTile = deg2num(south, west, zoom);
  const maxTile = deg2num(north, east, zoom);

  const tilesX = Math.abs(maxTile.x - minTile.x) + 1;
  const tilesY = Math.abs(maxTile.y - minTile.y) + 1;

  return tilesX * tilesY;
};
