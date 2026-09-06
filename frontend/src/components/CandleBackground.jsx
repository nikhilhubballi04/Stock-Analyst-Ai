function CandleBackground() {
  let seed = 42;
  function rand() {
    seed = (seed * 9301 + 49297) % 233280;
    return seed / 233280;
  }

  const count = 160;
  const spacing = 16;
  const width = count * spacing;
  const height = 400;
  const baseY = 220;

  const candles = [];

  for (let i = 0; i < count; i++) {
    const t = i / count;
    const smoothTrend =
      Math.sin(t * Math.PI * 2.2) * 60 +
      Math.sin(t * Math.PI * 5 + 1) * 20;

    const jitter = (rand() - 0.5) * 18;
    const centerY = baseY - smoothTrend + jitter;

    const isGreen = rand() > 0.45;
    const bodyHeight = 6 + rand() * 22;
    const wickExtra = 3 + rand() * 10;
    const x = i * spacing;

    candles.push({ x, bodyHeight, wickExtra, centerY, isGreen, key: i });
  }

  // Build a smooth filled wave shape from a sine function directly (not tied to candle jitter)
  function buildWaveArea({ amplitude1, freq1, amplitude2, freq2, phase, baseline, points = 60 }) {
    const pts = [];
    for (let i = 0; i <= points; i++) {
      const t = i / points;
      const x = t * width;
      const y =
        baseline -
        Math.sin(t * Math.PI * freq1 + phase) * amplitude1 -
        Math.sin(t * Math.PI * freq2 + phase * 1.3) * amplitude2;
      pts.push({ x, y });
    }

    let d = `M ${pts[0].x} ${pts[0].y}`;
    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = pts[i];
      const p1 = pts[i + 1];
      const midX = (p0.x + p1.x) / 2;
      d += ` C ${midX} ${p0.y}, ${midX} ${p1.y}, ${p1.x} ${p1.y}`;
    }
    d += ` L ${width} ${height} L 0 ${height} Z`;
    return d;
  }

  const wave1 = buildWaveArea({ amplitude1: 55, freq1: 2.2, amplitude2: 15, freq2: 5, phase: 0, baseline: 240 });
  const wave2 = buildWaveArea({ amplitude1: 40, freq1: 1.6, amplitude2: 20, freq2: 3.4, phase: 1.8, baseline: 270 });

  const gridLines = [];
  const gridSpacingX = 80;
  const gridSpacingY = 45;
  for (let x = 0; x <= width; x += gridSpacingX) {
    gridLines.push(<line key={`v${x}`} x1={x} y1={0} x2={x} y2={height} stroke="var(--candle-grid)" strokeWidth="1" />);
  }
  for (let y = 0; y <= height; y += gridSpacingY) {
    gridLines.push(<line key={`h${y}`} x1={0} y1={y} x2={width} y2={y} stroke="var(--candle-grid)" strokeWidth="1" />);
  }

  return (
    <svg
      className="candle-bg"
      viewBox={`0 0 ${width} ${height}`}
      preserveAspectRatio="xMidYMid slice"
      xmlns="http://www.w3.org/2000/svg"
    >
      {gridLines}

      <path d={wave1} fill="var(--candle-wave-fill-1)" stroke="none" />
      <path d={wave2} fill="var(--candle-wave-fill-2)" stroke="none" />

      {candles.map((c) => {
        const wickTop = c.centerY - c.bodyHeight / 2 - c.wickExtra / 2;
        const wickBottom = c.centerY + c.bodyHeight / 2 + c.wickExtra / 2;
        const color = c.isGreen ? "var(--candle-green)" : "var(--candle-red)";

        return (
          <g key={c.key}>
            <line x1={c.x + 5} x2={c.x + 5} y1={wickTop} y2={wickBottom} stroke={color} strokeWidth="0.9" />
            <rect x={c.x + 2} y={c.centerY - c.bodyHeight / 2} width="6" height={c.bodyHeight} fill={color} rx="1" />
          </g>
        );
      })}
    </svg>
  );
}

export default CandleBackground;