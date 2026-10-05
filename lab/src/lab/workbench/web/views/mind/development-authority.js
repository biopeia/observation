import {
  developmentScope,
  historySnapshots,
  milestones,
  mindHistory,
  selfDependencyHistory,
  selfRegionHistory,
} from './state.js';

const AUTHORITY = 'lab-physics3d-telemetry-v4.1';
let requestGeneration = 0;

function normalizedRunId(value) {
  const text = String(value ?? '').trim();
  return text || null;
}

function pointKey(point) {
  return `${normalizedRunId(point?.runId) ?? ''}|${Number(point?.tick) || 0}`;
}

function snapshotKey(item) {
  return `${normalizedRunId(item?.runId) ?? ''}|${Number(item?.tick) || 0}`;
}

function mergeByKey(canonical, live, keyFn, limit, runOrder) {
  const merged = new Map();
  for (const item of [...canonical, ...live]) {
    if (!item || !Number.isFinite(Number(item.tick))) continue;
    merged.set(keyFn(item), item);
  }
  return [...merged.values()]
    .sort((a, b) => {
      const runA = normalizedRunId(a.runId);
      const runB = normalizedRunId(b.runId);
      const orderA = runOrder.has(runA) ? runOrder.get(runA) : Number.MAX_SAFE_INTEGER;
      const orderB = runOrder.has(runB) ? runOrder.get(runB) : Number.MAX_SAFE_INTEGER;
      if (orderA !== orderB) return orderA - orderB;
      if (runA !== runB) return String(runA ?? '').localeCompare(String(runB ?? ''));
      return Number(a.tick) - Number(b.tick);
    })
    .slice(-limit);
}

function rebuildCanonicalMilestones(points) {
  const rebuilt = [];
  let previousRun = null;
  const previousByRun = new Map();
  for (const point of points) {
    const runId = normalizedRunId(point.runId);
    const previous = previousByRun.get(runId) ?? null;
    if (previousRun !== runId) {
      rebuilt.push({
        kind: 'observer-attached',
        label: 'Observer evidence begins for run',
        tick: point.tick,
        tone: 'info',
        runId,
      });
      if (previousRun !== null) {
        rebuilt.push({
          kind: `run-boundary:${runId ?? 'unscoped'}`,
          label: `Run boundary${runId ? ` · ${runId}` : ' · identity unavailable'}`,
          tick: point.tick,
          tone: 'info',
          runId,
        });
      }
      previousRun = runId;
    }
    if (previous) {
      if (previous.concepts === 0 && Number(point.concepts) > 0) {
        rebuilt.push({ kind:'first-concept', label:'First observed concept birth', tick:point.tick, tone:'violet', runId });
      }
      if (previous.predictors === 0 && Number(point.predictors) > 0) {
        rebuilt.push({ kind:'first-predictor', label:'First observed predictor birth', tick:point.tick, tone:'amber', runId });
      }
      if (previous.physiology !== point.physiology && point.physiology === 'dead') {
        rebuilt.push({ kind:'death', label:'Death', tick:point.tick, tone:'coral', runId });
      }
    }
    previousByRun.set(runId, point);
  }
  return rebuilt.slice(-128);
}

function resetForAuthority(organismId, runId) {
  mindHistory.length = 0;
  milestones.length = 0;
  historySnapshots.length = 0;
  selfRegionHistory.clear();
  selfDependencyHistory.clear();
  developmentScope.organismId = organismId;
  developmentScope.activeRunId = normalizedRunId(runId);
  developmentScope.observedStartTick = null;
  developmentScope.baselinePoint = null;
  developmentScope.lastPersistedTick = null;
  developmentScope.restored = false;
  developmentScope.authority = AUTHORITY;
  developmentScope.coverage = [];
  developmentScope.complete = false;
  developmentScope.loading = true;
  developmentScope.error = null;
}

export async function hydrateCanonicalDevelopmentHistory(organismId, runId = null) {
  const identity = String(organismId ?? '').trim();
  if (!identity) return false;
  const generation = ++requestGeneration;
  resetForAuthority(identity, runId);

  let payload;
  try {
    const response = await fetch(
      `/api/organism/development-history?organism_id=${encodeURIComponent(identity)}&limit=2048`,
      { cache: 'no-store' },
    );
    if (!response.ok) throw new Error(`history-http-${response.status}`);
    payload = await response.json();
  } catch (error) {
    if (generation !== requestGeneration || developmentScope.organismId !== identity) return false;
    developmentScope.loading = false;
    developmentScope.error = String(error?.message ?? error ?? 'history-unavailable');
    developmentScope.authority = 'unavailable';
    return false;
  }

  if (generation !== requestGeneration || developmentScope.organismId !== identity) return false;
  if (
    payload?.schema_version !== 1 ||
    payload?.authority !== AUTHORITY ||
    payload?.organism_id !== identity
  ) {
    developmentScope.loading = false;
    developmentScope.error = 'invalid-history-contract';
    developmentScope.authority = 'unavailable';
    return false;
  }

  // Live frames may arrive while the canonical request is in flight. Merge
  // them by run/tick instead of replacing them so hydration cannot rewind the
  // presentation or discard newer evidence.
  const livePoints = [...mindHistory];
  const liveSnapshots = [...historySnapshots];
  const canonicalPoints = Array.isArray(payload.points) ? payload.points : [];
  const canonicalSnapshots = Array.isArray(payload.snapshots) ? payload.snapshots : [];
  const coverage = Array.isArray(payload.coverage) ? payload.coverage : [];
  const runOrder = new Map(
    coverage.map((entry, index) => [normalizedRunId(entry?.run_id), index]),
  );
  const activeRunId = normalizedRunId(runId);
  if (activeRunId != null && !runOrder.has(activeRunId)) {
    runOrder.set(activeRunId, runOrder.size);
  }

  mindHistory.length = 0;
  mindHistory.push(...mergeByKey(canonicalPoints, livePoints, pointKey, 2048, runOrder));
  historySnapshots.length = 0;
  historySnapshots.push(...mergeByKey(canonicalSnapshots, liveSnapshots, snapshotKey, 160, runOrder));

  milestones.length = 0;
  milestones.push(...rebuildCanonicalMilestones(mindHistory));
  developmentScope.coverage = coverage;
  developmentScope.complete = payload.complete === true;
  developmentScope.observedStartTick = mindHistory.at(0)?.tick ?? null;
  developmentScope.baselinePoint = mindHistory.at(0) ? { ...mindHistory.at(0) } : null;
  developmentScope.lastPersistedTick = mindHistory.at(-1)?.tick ?? null;
  developmentScope.restored = Boolean(mindHistory.length || historySnapshots.length);
  developmentScope.loading = false;
  developmentScope.error = null;
  developmentScope.authority = payload.available === false ? 'unavailable' : AUTHORITY;
  return true;
}

export function cancelCanonicalDevelopmentHydration() {
  requestGeneration += 1;
}
