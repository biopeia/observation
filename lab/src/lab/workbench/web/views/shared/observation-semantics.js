export const OBSERVED_AVAILABILITY = new Set(['observed', 'observed_empty']);

export function observedCollectionCount(availability, value) {
  if (!OBSERVED_AVAILABILITY.has(availability)) return null;
  return Array.isArray(value) ? value.length : null;
}

export function observedTopologyCounts(topology, availability) {
  if (!OBSERVED_AVAILABILITY.has(availability)) {
    return { senses: null, concepts: null, predictors: null, readouts: null };
  }
  const nodes = Array.isArray(topology?.nodes) ? topology.nodes : [];
  return {
    senses: nodes.filter((node) => node?.kind === 'sense').length,
    concepts: nodes.filter((node) => node?.kind === 'concept').length,
    predictors: nodes.filter((node) => node?.kind === 'predictor').length,
    readouts: nodes.filter((node) => node?.kind === 'readout').length,
  };
}

export function observedFiniteNumber(value) {
  if (value === null || value === undefined || value === '') return null;
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
}

export function refreshFrameCoherence(streamState, now = Date.now()) {
  streamState.coherent =
    streamState.runId != null &&
    streamState.organismId != null &&
    streamState.telemetryTick != null &&
    streamState.snapshotTick != null &&
    streamState.telemetryTick === streamState.snapshotTick;
  if (streamState.status === 'live' && streamState.coherent) {
    streamState.lastCoherentFrameAt = now;
    streamState.stale = false;
  }
  return streamState.coherent;
}

export function frameTimedOut(streamState, now = Date.now(), timeoutMs = 5000) {
  return (
    streamState.status === 'live' &&
    streamState.lastCoherentFrameAt != null &&
    now - streamState.lastCoherentFrameAt > timeoutMs
  );
}

export function displayObservedCount(value) {
  return value == null ? '—' : String(value);
}
