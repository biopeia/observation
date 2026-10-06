export const PAL = {
  cyan:   'oklch(0.52 0.12 252)', // modality
  violet: 'oklch(0.50 0.10 300)', // lab
  amber:  'oklch(0.56 0.10 62)',  // embodiment
  coral:  'oklch(0.54 0.17 32)',  // signal-warn
  mint:   'oklch(0.52 0.11 152)', // symbiont
  muted:  '#5c636c',              // ink-3
  text:   '#18202b',              // ink-1
  bg:     '#0e1317',              // night-0 (instrument)
  surface:'#151c21',              // night-1 (instrument)
  line:   '#2c373e',              // night-rule
};

// Observer-defined reference zones. Analytical overlays only.
export const REGIMES = [
  { id: 'low_activity',        name: 'Baja actividad',        x: -160, y:  130, color: PAL.cyan,  radius: 95,  description: 'Observer projection: low measured activity and low predictive tension.' },
  { id: 'sustained_activity',  name: 'Actividad sostenida',   x:  170, y:  110, color: PAL.mint,  radius: 100, description: 'Observer projection: sustained activity with comparatively low predictive tension.' },
  { id: 'transient_activity',  name: 'Actividad transitoria', x:  -40, y:  -50, color: PAL.amber, radius: 90,  description: 'Observer projection: intermediate activity with elevated short-term predictive tension.' },
  { id: 'high_tension',        name: 'Tensión elevada',       x:  180, y: -170, color: PAL.coral, radius: 95,  description: 'Observer projection: high activity and/or predictive tension.' },
];

export const GRAPH_PHYSICS = Object.freeze({
  // The Atlas is a persistent cartography, not a box of elastic particles.
  // Keep long-range repulsion weak; use local overlap exclusion for legibility.
  repulsion: 1800,
  overlapStrength: 0.12,
  overlapGap: 4,
  springK: 0.028,
  springLength: 80,
  centerGravity: 0.010,
  temporalAnchor: 0.006,
  damping: 0.72,
  maxStep: 3.5,
  settleSpeed: 0.035,
  alphaDecay: 0.975,
  alphaMin: 0.001,
});
