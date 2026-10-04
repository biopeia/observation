/**
 * Shared entrypoint for the Embodiment and World routes.
 *
 * Morphology-neutral rendering lives in ./body/viewer.js; the route decides
 * the product domain (see ADR-0008).
 */
import { BodyViewer, HumanoidViewer } from './body/viewer.js';

export { BodyViewer, HumanoidViewer };

let globalInstance = null;
let mountedRoot = null;
let mountedDomain = 'world';
let presentationIdentity = null;
let remountScheduled = false;

function physicalIdentity(state) {
  const physics = state?.sources?.physics3d ?? null;
  if (!physics?.run_id) return null;
  // Managed runs expose the concrete body ref when known. Keep body_kind too:
  // morphology is an apparatus boundary even when a future source omits a
  // durable body ref. Any change recreates observer-owned physical state.
  return `${physics.run_id}|${physics.body_ref ?? ''}|${physics.body_kind ?? ''}`;
}

function eventPhysicalIdentity(event) {
  const runId = event?.run_id ?? null;
  if (!runId) return null;
  return `${runId}|${event.body_id ?? ''}|${event.embodiment_id ?? ''}`;
}

function remountPhysicalPresentation() {
  if (remountScheduled || !mountedRoot || !globalInstance) return;
  remountScheduled = true;
  queueMicrotask(() => {
    remountScheduled = false;
    if (!mountedRoot || !globalInstance) return;
    const root = mountedRoot;
    const domain = mountedDomain;
    globalInstance.unmount();
    root.replaceChildren();
    // The new viewer establishes its stream identity from the first event it
    // actually accepts. No old pose/trajectory/interpolation state survives.
    createViewer(root, domain);
  });
}

function installStreamIdentityGuard(viewer) {
  const decoder = viewer?.liveDecoder;
  if (!decoder?.decode) return;
  const decode = decoder.decode.bind(decoder);
  let acceptedIdentity = null;
  decoder.decode = (payload) => {
    const data = decode(payload);
    if (!data) return data;
    const nextIdentity = eventPhysicalIdentity(data);
    if (!nextIdentity) return data;
    if (acceptedIdentity === null) {
      acceptedIdentity = nextIdentity;
      return data;
    }
    if (nextIdentity === acceptedIdentity) return data;

    // Never let a frame from another run/body reach the existing viewer. The
    // remount is scheduled outside the EventSource callback to avoid mutating
    // the listener while it is dispatching this event.
    const status = viewer.statusEl;
    if (status) {
      status.textContent = '○ Physical identity changed — resetting presentation';
      status.style.color = 'var(--amber, #f1fa8c)';
      status.dataset.observationFreshness = 'stale';
    }
    remountPhysicalPresentation();
    return null;
  };
}

function createViewer(root, domain) {
  globalInstance = new BodyViewer(root, undefined, { domain });
  installStreamIdentityGuard(globalInstance);
  return globalInstance;
}

function drainTransportIssues() {
  const decoder = globalInstance?.liveDecoder;
  if (!decoder?.takeIssue) return;
  let issue = decoder.takeIssue();
  while (issue) {
    const status = globalInstance?.statusEl;
    if (status && ['gap', 'waiting-for-anchor', 'schema-error'].includes(issue.kind)) {
      status.textContent = issue.kind === 'schema-error'
        ? '○ Invalid observation payload — waiting for valid data'
        : `○ Observation gap${issue.channel ? ` · ${issue.channel}` : ''} — waiting for anchor`;
      status.style.color = 'var(--amber, #f1fa8c)';
      status.dataset.observationFreshness = 'stale';
    } else if (status && issue.kind === 'rebase') {
      status.textContent = `● Live · rebased${issue.reason ? ` (${issue.reason})` : ''}`;
      status.style.color = 'var(--mint, #50fa7b)';
      status.dataset.observationFreshness = 'live';
    }
    issue = decoder.takeIssue();
  }
}

export function mount(root, state = null, { domain = 'world' } = {}) {
  if (globalInstance) unmount();
  mountedRoot = root;
  mountedDomain = domain;
  presentationIdentity = physicalIdentity(state);
  return createViewer(root, domain);
}

export function update(root, state = null) {
  if (!globalInstance || root !== mountedRoot) return;
  drainTransportIssues();

  const nextIdentity = physicalIdentity(state);
  if (!nextIdentity || nextIdentity === presentationIdentity) return;

  // Physical presentation is observer-owned and body-specific. Recreate it at
  // a run/body boundary instead of carrying pose, trajectory, contacts,
  // interpolation buffers or World materialization into the new embodiment.
  globalInstance.unmount();
  root.replaceChildren();
  presentationIdentity = nextIdentity;
  createViewer(root, mountedDomain);
}

export function unmount() {
  remountScheduled = false;
  if (globalInstance) {
    globalInstance.unmount();
    globalInstance = null;
  }
  mountedRoot = null;
  presentationIdentity = null;
}
