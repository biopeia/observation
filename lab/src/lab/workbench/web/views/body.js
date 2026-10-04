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

function physicalIdentity(state) {
  const physics = state?.sources?.physics3d ?? null;
  if (!physics?.run_id) return null;
  // A managed re-embodiment is a new run. body_kind is retained as an explicit
  // apparatus boundary so a future in-run morphology change cannot reuse pose,
  // trajectory, interpolation or observer-history buffers accidentally.
  return `${physics.run_id}|${physics.body_kind ?? ''}`;
}

function createViewer(root, domain) {
  globalInstance = new BodyViewer(root, undefined, { domain });
  return globalInstance;
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
  if (globalInstance) {
    globalInstance.unmount();
    globalInstance = null;
  }
  mountedRoot = null;
  presentationIdentity = null;
}
