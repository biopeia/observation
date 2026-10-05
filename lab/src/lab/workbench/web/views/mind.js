/**
 * mind.js — Cognitive ("Mind") view for Symbiont Lab.
 *
 * ES module.  Public API:
 *   mount(root: HTMLElement)  → void
 *   unmount()                 → void
 *
 * Displays one live symbiont organism across six research tabs:
 *   Overview · Identity · Sensory · Cognition · History
 *
 * Action discovery (formerly Motor Learning) belongs to the Embodiment
 * Experience (ADR-0008); Mind keeps cognitive structure only.
 *
 * SSE endpoints consumed:
 *   /api/organism   — coherent local observation stream
 *   /fleet          — Observatory source discovery (only unambiguous live source is selected)
 *   /instances/:id — full snapshot for an explicitly resolved instance
 *
 * No external dependencies (no Three.js). Uses CSS variables from app.css.
 */

// ─────────────────────────────────────────────────────────────────────────────
// Constants & Palette
// ─────────────────────────────────────────────────────────────────────────────

import { PAL } from './mind/config.js';
import { pct } from './mind/util.js';
import { buildMindLayout } from './mind/layout.js';
import { MindStreams } from './mind/streams.js';
import { applyTelemetryEvent } from './mind/telemetry.js';
import { applyMindSnapshot } from './mind/snapshot.js';
import { renderOverview as renderOverviewPanel } from './mind/overview.js';
import {
  activateMindDevelopmentHistory,
  nearestHistorySnapshot,
  persistMindDevelopmentHistory,
  recordMindHistory,
  renderHistory as renderHistoryPanel,
} from './mind/history.js';
import { createIdentitySensoryRenderer } from './mind/identity-sensory.js';
import { createCognitionController } from './mind/cognition-controller.js';
import { currentPhysiologyState } from './mind/derived.js';
import { applyMindTab } from './mind/tab-controller.js';
import {
  graph as _graph,
  resetMindDataState,
  snap as _snap,
  streamState as _streamState,
  tel as _tel,
} from './mind/state.js';

// ─────────────────────────────────────────────────────────────────────────────
// Module-level state (single active view by public API contract)
// ─────────────────────────────────────────────────────────────────────────────

let _root           = null;
let _streams        = null;
let _resizeObs      = null;   // ResizeObserver on canvas wrappers
let _activeTab      = 'overview';
let _appState        = null;

// Lifecycle / UI state merged from the instance-oriented refactor.
let _uid                    = 'default';
let _rootStyleBeforeMount   = '';
let _lastUITime             = 0;
const UI_THROTTLE_MS        = 66; // ~15 FPS for text-only telemetry updates
const STALE_AFTER_MS         = 5000;

const cognition = createCognitionController({
  getActiveTab: () => _activeTab,
  onSwitchTab: (tabId) => switchTab(tabId),
});

const {
  renderIdentityGap,
  renderPhenotype,
  renderSelf,
  renderSensesPanel,
  renderSensoryMap,
} = createIdentitySensoryRenderer({
  getUid: () => _uid,
  onSelectCognitiveNode: (nodeId) => cognition.selectNode(nodeId),
});

// ─────────────────────────────────────────────────────────────────────────────
// Layout HTML
// ─────────────────────────────────────────────────────────────────────────────

/** Build the complete DOM structure for the Mind view and inject it into root. */
function renderOverview() {
  renderOverviewPanel({ onOpenHistoryTick: openHistoryTick });
}

function renderHistory() {
  renderHistoryPanel({ onOpenHistoryTick: openHistoryTick });
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab switching
// ─────────────────────────────────────────────────────────────────────────────

function switchTab(tabId) {
  _activeTab = applyMindTab(tabId);

  if (_activeTab === 'overview') renderOverview();
  if (_activeTab === 'phenotype') {
    renderPhenotype();
    renderIdentityGap();
    renderSelf();
  }
  if (_activeTab === 'sensory') {
    renderSensesPanel();
    renderSensoryMap();
  }
  if (_activeTab === 'cognition') {
    cognition.start();
    cognition.renderInspector();
  }
  if (_activeTab === 'history') renderHistory();
}

// ─────────────────────────────────────────────────────────────────────────────
// Telemetry strip update
// ─────────────────────────────────────────────────────────────────────────────

function observedTopologyCount(kind) {
  if (_snap.availability?.topology !== 'observed') return null;
  const nodes = Array.isArray(_snap.topology?.nodes) ? _snap.topology.nodes : null;
  if (!nodes) return null;
  return nodes.filter((node) => node?.kind === kind).length;
}

function countLabel(value, suffix) {
  return value == null ? `—${suffix}` : `${value}${suffix}`;
}

function updateTelemetryStrip(force = false) {
  const now = performance.now();
  if (!force && now - _lastUITime < UI_THROTTLE_MS) return;

  // A zero derived from topology is a fact only when topology itself was
  // observed. Missing telemetry plus missing topology remains unknown.
  const concepts = _tel.cognitiveConcepts ?? observedTopologyCount('concept');
  const predictors = _tel.predictorCount ?? observedTopologyCount('predictor');
  const physiology = currentPhysiologyState();

  setTelem('mind-t-tick', _tel.tick != null ? `t${_tel.tick}` : '—');
  setTelem(
    'mind-t-phase',
    physiology.toUpperCase(),
    physiology === 'dead' ? PAL.coral :
      physiology === 'dormant' ? PAL.amber :
      physiology === 'stressed' ? PAL.coral : PAL.mint,
  );
  setTelem(
    'mind-t-energy',
    _tel.metabolicReserve != null ? pct(_tel.metabolicReserve) : '—',
    _tel.metabolicReserve != null && _tel.metabolicReserve < 0.2 ? PAL.coral : null,
  );
  setTelem(
    'mind-t-resource',
    _tel.resourceProgress != null
      ? `${_tel.resourceProgress >= 0 ? '+' : ''}${_tel.resourceProgress.toFixed(2)} m`
      : '—',
  );
  setTelem(
    'mind-t-cognition',
    `${countLabel(concepts, 'C')} / ${countLabel(predictors, 'P')}`,
    PAL.violet,
  );
  setTelem(
    'mind-t-motor',
    _tel.motorOrigin ?? '—',
    ['cognition','mixed'].includes(_tel.motorOrigin) || String(_tel.motorOrigin).includes('primitive')
      ? PAL.mint
      : _tel.motorOrigin === 'babbling' ? PAL.amber : null,
  );
  setTelem('mind-t-instance', _snap.displayId ?? _snap.instanceId ?? _streamState.organismId ?? '—');
  const streamDetail = [_streamState.status || 'disconnected', _streamState.reason]
    .filter(Boolean).join(' · ');
  setTelem('mind-t-stream', streamDetail);
  setTelem('mind-t-frame', `${_streamState.telemetryTick ?? '—'} / ${_streamState.snapshotTick ?? '—'}`);
  _lastUITime = now;
}

function setTelem(id, text, color = null) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = text;
  if (color) el.style.color = color;
}

// ─────────────────────────────────────────────────────────────────────────────
// Waiting overlay
// ─────────────────────────────────────────────────────────────────────────────

function setWaiting(visible, message) {
  const overlay = document.getElementById('mind-waiting');
  if (!overlay) return;
  overlay.style.display = visible ? 'flex' : 'none';
  const txt = document.getElementById('mind-wait-text');
  if (txt && message) txt.textContent = message;
}

// ─────────────────────────────────────────────────────────────────────────────
// Senses panel rendering
// ─────────────────────────────────────────────────────────────────────────────

function openHistoryTick(tick) {
  const historical = nearestHistorySnapshot(tick, _streamState.runId);
  if (historical?.snapshot?.topology) {
    _graph.replaySnapshot = historical.snapshot;
    _graph.replayTick = historical.tick;
    _graph.cachedPositions.clear();
    switchTab('cognition');
  } else {
    renderHistory();
  }
}

function refreshSnapshotViews() {
  setWaiting(false, null);
  recordMindHistory();
  updateTelemetryStrip();
  if (_activeTab === 'overview') renderOverview();
  if (_activeTab === 'phenotype') {
    renderPhenotype();
    renderIdentityGap();
    renderSelf();
  }
  if (_activeTab === 'sensory') {
    renderSensesPanel();
    renderSensoryMap();
  }
  if (_activeTab === 'cognition') {
    cognition.updateSummary();
    cognition.init(
      document.getElementById('mind-cognition-canvas')?.width ?? 900,
      document.getElementById('mind-cognition-canvas')?.height ?? 600,
    );
    cognition.renderInspector();
  }
  if (_activeTab === 'history') renderHistory();
}

// ─────────────────────────────────────────────────────────────────────────────
// SSE connections
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Connect to /api/organism for coherent local observation and Observatory fallback.
 */
function resetCurrentObservation() {
  for (const key of Object.keys(_tel)) _tel[key] = null;
  for (const key of Object.keys(_snap)) {
    _snap[key] = Array.isArray(_snap[key]) ? [] : null;
  }
  _snap.senses = [];
  _snap.beliefs = [];
  _snap.sensoryDevelopment = [];
  _snap.sensoryRelations = [];
  _snap.availability = {};
}

function updateCoherence() {
  _streamState.coherent =
    _streamState.runId != null &&
    _streamState.organismId != null &&
    _streamState.telemetryTick != null &&
    _streamState.snapshotTick != null &&
    _streamState.telemetryTick === _streamState.snapshotTick;
  if (_streamState.status === 'live' && _streamState.coherent) {
    _streamState.lastCoherentFrameAt = Date.now();
    _streamState.stale = false;
  }
}

function ingestTelemetryEvent(data, meta = {}) {
  if (!applyTelemetryEvent(data)) return;
  if (!meta.historical) _streamState.lastTelemetryAt = Date.now();
  _streamState.telemetryTick = meta.frameTick ?? data.tick ?? null;
  updateCoherence();
  recordMindHistory({ captureSnapshot: false, persist: !meta.historical });
  if (!meta.historical) updateTelemetryStrip();
}

function updateMindSourceState(next) {
  if (next.identityChanged) {
    persistMindDevelopmentHistory({ force: true });
    resetCurrentObservation();
    _streamState.telemetryTick = null;
    _streamState.snapshotTick = null;
    _streamState.coherent = false;
  }
  Object.assign(_streamState, {
    status: next.status,
    source: next.source ?? null,
    instanceId: next.instanceId ?? null,
    runId: next.runId ?? null,
    organismId: next.organismId ?? null,
    bodyId: next.bodyId ?? null,
    embodimentId: next.embodimentId ?? null,
    topologyRevision: next.topologyRevision ?? null,
    stale: next.status !== 'live',
    reason: next.reason ?? null,
  });
  if (_streamState.organismId) {
    // Development remains organism-longitudinal while history records retain
    // run boundaries. Live state was already cleared above on identity change.
    activateMindDevelopmentHistory(_streamState.organismId, _streamState.runId);
  }
  updateCoherence();
  updateTelemetryStrip(true);
}

function physicsRunning(appState) {
  return ['starting', 'running', 'stopping'].includes(appState?.sources?.physics3d?.state);
}

export function update(root, appState) {
  if (!_root || root !== _root) return;
  _appState = appState ?? null;
  const timedOut =
    _streamState.status === 'live' &&
    _streamState.lastCoherentFrameAt != null &&
    Date.now() - _streamState.lastCoherentFrameAt > STALE_AFTER_MS;
  if (timedOut) {
    _streamState.status = 'stale';
    _streamState.stale = true;
    _streamState.reason = 'coherent-frame-timeout';
  }
  if (_streamState.source === 'physics3d' && !physicsRunning(_appState) && _streamState.status === 'live') {
    _streamState.status = 'stale';
    _streamState.stale = true;
    _streamState.reason = 'physics3d-run-ended';
    updateTelemetryStrip(true);
  } else if (timedOut) {
    updateTelemetryStrip(true);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Public API
// ─────────────────────────────────────────────────────────────────────────────

/** Mount the Mind view into root. */
export function mount(root, appState = null) {
  if (!(root instanceof HTMLElement)) {
    throw new TypeError('Mind view requires a valid HTMLElement root');
  }

  if (_root) unmount();

  _root = root;
  _appState = appState ?? null;
  _rootStyleBeforeMount = root.style.cssText;
  _uid = Math.random().toString(36).slice(2, 9);
  _lastUITime = 0;
  _activeTab = 'overview';

  resetMindDataState();
  cognition.resetPresentation();

  buildMindLayout(root, {
    activeTab: _activeTab,
    graphDimension: _graph.dimension,
    graph3DMode: _graph.threeDMode,
    graphAtlasMode: _graph.atlasMode,
    showEmbodiment: _graph.showEmbodiment,
    onTabChange: switchTab,
    on3DModeChange: (mode) => cognition.set3DMode(mode),
    onAtlasModeChange: (mode) => cognition.setAtlasMode(mode),
    onShowEmbodimentChange: (show) => cognition.setShowEmbodiment(show),
    onSearch: (query) => cognition.searchAtlas(query),
    onReturnLive: () => cognition.returnLive(),
  });

  setWaiting(true, 'Connecting to organism streams…');
  renderOverview();
  updateTelemetryStrip(true);
  switchTab('overview');

  _streams = new MindStreams({
    onTelemetry: ingestTelemetryEvent,
    onSnapshot: (snapshot, meta = {}) => {
      if (applyMindSnapshot(snapshot)) {
        const organismId = meta.organismId ?? _streamState.organismId ?? null;
        const runId = meta.runId ?? _streamState.runId ?? null;
        if (organismId) activateMindDevelopmentHistory(organismId, runId);
        if (!meta.historical) _streamState.lastSnapshotAt = Date.now();
        _streamState.snapshotTick = meta.tick ?? snapshot?.tick ?? snapshot?.snapshot?.tick ?? null;
        updateCoherence();
        if (meta.historical) {
          recordMindHistory({ captureSnapshot: true, persist: false });
          if (meta.historicalFinal) {
            persistMindDevelopmentHistory({ force: true });
          }
        } else {
          refreshSnapshotViews();
        }
      }
    },
    onTopology: (topology) => {
      _snap.topology = topology;
      _snap.availability = { ...(_snap.availability ?? {}), topology: 'observed' };
      if (_activeTab === 'cognition') {
        cognition.init(
          document.getElementById('mind-cognition-canvas')?.width ?? 900,
          document.getElementById('mind-cognition-canvas')?.height ?? 600,
        );
      }
    },
    onWaiting: setWaiting,
    onSourceState: updateMindSourceState,
  });
  _streams.connect();

  _resizeObs = new ResizeObserver(() => {
    if (_activeTab === 'cognition') cognition.resize();
    if (_activeTab === 'phenotype') {
      renderPhenotype();
      renderIdentityGap();
      renderSelf();
    }
  });
  _resizeObs.observe(root);
}

/** Unmount the Mind view and release presentation resources. */
export function unmount() {
  persistMindDevelopmentHistory({ force: true });

  cognition.stop();
  cognition.resetPresentation();

  if (_streams) {
    _streams.close();
    _streams = null;
  }

  if (_resizeObs) { _resizeObs.disconnect(); _resizeObs = null; }

  _graph.nodes = [];
  _graph.edges = [];
  _graph.hoveredNode = null;
  _graph.selectedNodeId = null;
  _graph.cachedPositions.clear();
  _graph.world3d.clear();
  _graph.velocity3d.clear();
  _graph.projected3d.clear();

  if (_root) {
    _root.replaceChildren();
    _root.classList.remove('mind-view-root');
    _root.style.cssText = _rootStyleBeforeMount;
    _root = null;
  }

  _rootStyleBeforeMount = '';
  _appState = null;
}
