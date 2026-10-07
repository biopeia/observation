/** Observer-only identity/freshness boundary for Body and World presentation. */

function stateIdentity(state) {
  const physics = state?.sources?.physics3d ?? null;
  if (!physics?.run_id) return null;
  return `${physics.run_id}|${physics.body_ref ?? ''}|${physics.body_kind ?? ''}`;
}

function stateRunId(state) {
  return state?.sources?.physics3d?.run_id ?? null;
}

function eventIdentity(event) {
  if (!event?.run_id) return null;
  return {
    run_id: event.run_id,
    // Runtime component projections and apparatus/body-pose projections do
    // not currently share the same body_id namespace. Compare physical ids
    // only against subsequent events from the same projection family.
    scope: ['body', 'cognition', 'vitals'].includes(event.type) ? 'components' : 'apparatus',
    body_id: event.body_id ?? null,
    embodiment_id: event.embodiment_id ?? null,
    body_kind: event.body_kind ?? null,
  };
}

function mergeEventIdentity(current, next) {
  if (!current) {
    return {
      identity: { run_id: next.run_id, scopes: { [next.scope]: next } },
      conflict: false,
    };
  }
  if (current.run_id !== next.run_id) return { identity: current, conflict: true };
  const scoped = current.scopes[next.scope] ?? { scope: next.scope };
  const fields = ['body_id', 'embodiment_id', 'body_kind'];
  const conflict = fields.some((key) => (
    scoped[key] != null && next[key] != null && scoped[key] !== next[key]
  ));
  if (conflict) return { identity: current, conflict: true };
  return {
    identity: {
      ...current,
      scopes: {
        ...current.scopes,
        [next.scope]: Object.fromEntries(
          [['scope', next.scope], ...fields.map((key) => [key, scoped[key] ?? next[key]])],
        ),
      },
    },
    conflict: false,
  };
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
    this.presentationRunId = null;
    this.remountScheduled = false;
    // A newly-created EventSource has no Last-Event-ID and the server replays
    // the latest materialized boundary. Keep the last boundary across viewer
    // remounts so replaying that same lifecycle marker cannot trigger an
    // unbounded remount/reconnect loop.
    this.lastBoundaryKey = null;
  }

  mount(state) {
    this.presentationIdentity = stateIdentity(state);
    this.presentationRunId = stateRunId(state);
  }

  attach(viewer) {
    const decoder = viewer?.liveDecoder;
    if (!decoder?.decode) return;
    const decode = decoder.decode.bind(decoder);
    let acceptedIdentity = null;
    decoder.decode = (payload) => {
      const data = decode(payload);
      if (!data) return data;

      if (data.type === 'observation_boundary') {
        const boundaryKey = `${data.phase ?? ''}|${data.run_id ?? ''}`;
        if (boundaryKey === this.lastBoundaryKey) return null;
        this.lastBoundaryKey = boundaryKey;
        acceptedIdentity = null;
        markStatus(
          viewer,
          data.phase === 'begin'
            ? '○ New run — waiting for physical observation'
            : '○ Run ended — waiting for a new run',
          'stale',
          'var(--amber, #f1fa8c)',
        );
        this.scheduleIdentityChange();
        return null;
      }

      const nextIdentity = eventIdentity(data);
      if (!nextIdentity) return data;

      // /api/state may already know the new run while the SSE connection still
      // has an older event in flight. Never let that first stale event establish
      // a fresh presentation identity merely because the stream-local baseline
      // has not yet been populated.
      if (
        acceptedIdentity === null &&
        this.presentationRunId != null &&
        nextIdentity.run_id !== this.presentationRunId
      ) {
        markStatus(
          viewer,
          '○ Physical identity changed — resetting presentation',
          'stale',
          'var(--amber, #f1fa8c)',
        );
        this.scheduleIdentityChange();
        return null;
      }

      const merged = mergeEventIdentity(acceptedIdentity, nextIdentity);
      if (!merged.conflict) {
        acceptedIdentity = merged.identity;
        return data;
      }

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
    // The stream detected the boundary before /api/state necessarily did.
    // Forget the state-side baseline so the first subsequent poll establishes
    // the new identity instead of forcing a redundant second remount.
    this.presentationIdentity = null;
    this.presentationRunId = null;
    queueMicrotask(() => {
      this.remountScheduled = false;
      this.onIdentityChange();
    });
  }

  update(viewer, state) {
    this.drainTransportIssues(viewer);
    const nextIdentity = stateIdentity(state);
    const nextRunId = stateRunId(state);
    if (!nextIdentity) return false;
    if (this.presentationIdentity === null) {
      this.presentationIdentity = nextIdentity;
      this.presentationRunId = nextRunId;
      return false;
    }
    if (nextIdentity === this.presentationIdentity) {
      this.presentationRunId = nextRunId;
      return false;
    }
    this.presentationIdentity = nextIdentity;
    this.presentationRunId = nextRunId;
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
    this.presentationRunId = null;
    this.remountScheduled = false;
  }
}
