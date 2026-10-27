// Formações em coordenadas do mundo (x 0..68, y 0..105). `down` = time ataca para cima (gol em y=0).
// Time "de baixo" defende o gol y=105; time "de cima" defende o gol y=0 (use mirror()).
(() => {
  const F = {
    '4-3-3': [[34,98],[10,82],[26,84],[42,84],[58,82],[22,66],[34,70],[46,66],[10,48],[34,42],[58,48]],
    '4-4-2': [[34,98],[10,82],[26,84],[42,84],[58,82],[10,64],[26,66],[42,66],[58,64],[26,46],[42,46]],
    '4-2-3-1': [[34,98],[10,82],[26,84],[42,84],[58,82],[26,68],[42,68],[10,52],[34,54],[58,52],[34,40]],
    '3-5-2': [[34,98],[18,84],[34,86],[50,84],[8,62],[22,66],[34,68],[46,66],[60,62],[26,44],[42,44]],
  };
  // espelha para o time de cima
  const mirror = pts => pts.map(([x, y]) => [68 - x, 105 - y]);
  // interpola entre dois conjuntos de posições (k 0..1)
  const morph = (a, b, k) => a.map((p, i) => [p[0] + (b[i][0] - p[0]) * k, p[1] + (b[i][1] - p[1]) * k]);
  // desloca o time inteiro (ex.: bloco sobe/desce), com compressão vertical opcional
  const shift = (pts, dx, dy, sy = 1, pivot = 52.5) => pts.map(([x, y]) => [x + dx, pivot + (y - pivot) * sy + dy]);
  window.Formations = { F, mirror, morph, shift };
})();
