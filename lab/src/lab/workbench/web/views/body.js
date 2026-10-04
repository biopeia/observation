/**
 * Shared entrypoint for the Embodiment and World routes.
 *
 * Morphology-neutral rendering lives in ./body/viewer.js; observer identity
 * and freshness policy lives in ./body/observability.js (ADR-0008 boundary).
 */
import { BodyViewer, HumanoidViewer } from './body/viewer.js';
import { PhysicalObservationBoundary } from './body/observability.js';

export { BodyViewer, HumanoidViewer };

let viewer = null;
let mountedRoot = null;
let mountedDomain = 'world';

const boundary = new PhysicalObservationBoundary({
  onIdentityChange: () => remountViewer(),
});

function createViewer(root, domain) {
  viewer = new BodyViewer(root, undefined, { domain });
  boundary.attach(viewer);
  return viewer;
}

function remountViewer() {
  if (!viewer || !mountedRoot) return;
  const root = mountedRoot;
  viewer.unmount();
  root.replaceChildren();
  createViewer(root, mountedDomain);
}

export function mount(root, state = null, { domain = 'world' } = {}) {
  if (viewer) unmount();
  mountedRoot = root;
  mountedDomain = domain;
  boundary.mount(state);
  return createViewer(root, domain);
}

export function update(root, state = null) {
  if (!viewer || root !== mountedRoot) return;
  if (boundary.update(viewer, state)) remountViewer();
}

export function unmount() {
  boundary.reset();
  if (viewer) {
    viewer.unmount();
    viewer = null;
  }
  mountedRoot = null;
}
