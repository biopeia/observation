/** Observer-only identity/freshness boundary for Body and World presentation. */

function stateIdentity(state) {
  const physics = state?.sources?.physics3d ?? null;
  if (!physics?.run_id) return null;
  return `${physics.run_id}|${physics.body_ref ?? ''}|${physics.body_kind ?? ''}`;
}

function eventIdentity(event) {
  if (!event?.run_id) return null;
  return `${event.run_id}|${event.body_id ?? ''}|${event.embodiment_id ?? ''}`;
}

function markStatus(viewer, text, freshness, color) {
  const status = viewer?.statusEl;
  if (!status) return;
  status.textContent = text;
  status.style.color = color;
  status.dataset.observationFreshness = freshness;
}

export class PhysicalObservationBoundary {
  constructor({ onIdentityChange } = {}) {
    this.onIdentityChange = onIdentityChange ?? (() => {});
    this.presentationIdentity = null;
    this.remountScheduled = false;
  }

  mount(state) {
    this.presentationIdentity = stateIdentity(state);
  }

  attach(viewer) {
    const decoder = viewer?.liveDecoder;
    if (!decoder?.decode) return;
    const decode = decoder.decode.bind(decoder);
    let acceptedIdentity = null;
    decoder.decode = (payload) => {
      const data = decode(payload);
      if (!data) return data;
      const nextIdentity = eventIdentity(data);
      if (!nextIdentity) return data;
      if (acceptedIdentity === null) {
        acceptedIdentity = nextIdentity;
        return data;
      }
      if (nextIdentity === acceptedIdentity) return data;

      markStatus(
        viewer,
        '○ Physical identity changed — resetting presentation',
        'stale',
        'var(--amber, #f1fa8c)',
      );
      this.scheduleIdentityChange();
      return null;
    };
  }

  scheduleIdentityChange() {
    if (this.remountScheduled) return;
    this.remountScheduled = true;
    queueMicrotask(() => {
      this.remountScheduled = false;
      this.onIdentityChange();
    });
  }

  update(viewer, state) {
    this.drainTransportIssues(viewer);
    const nextIdentity = stateIdentity(state);
    if (!nextIdentity || nextIdentity === this.presentationIdentity) return false;
    this.presentationIdentity = nextIdentity;
    return true;
  }

  drainTransportIssues(viewer) {
    const decoder = viewer?.liveDecoder;
    if (!decoder?.takeIssue) return;
    let issue = decoder.takeIssue();
    while (issue) {
      if (['gap', 'waiting-for-anchor', 'schema-error'].includes(issue.kind)) {
        markStatus(
          viewer,
          issue.kind === 'schema-error'
            ? '○ Invalid observation payload — waiting for valid data'
            : `○ Observation gap${issue.channel ? ` · ${issue.channel}` : ''} — waiting for anchor`,
          'stale',
          'var(--amber, #f1fa8c)',
        );
      } else if (issue.kind === 'rebase') {
        markStatus(
          viewer,
          `● Live · rebased${issue.reason ? ` (${issue.reason})` : ''}`,
          'live',
          'var(--mint, #50fa7b)',
        );
      }
      issue = decoder.takeIssue();
    }
  }

  reset() {
    this.presentationIdentity = null;
    this.remountScheduled = false;
  }
}
