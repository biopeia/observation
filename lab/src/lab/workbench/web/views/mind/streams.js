import { LiveObservationDecoder } from '../../stream-delta.js';

function frameIdentity(frame) {
  // Canonical v2 fields live on the frame itself. Nested fallbacks exist only
  // at this transport boundary for compatibility with pre-v2 observer frames.
  return {
    runId: frame?.run_id ?? frame?.runId ?? frame?.cognition?.run_id ?? null,
    instanceId: frame?.instance_id ?? frame?.instanceId ?? frame?.cognition?.instance_id ?? null,
    organismId: frame?.organism_id ?? frame?.organismId ?? null,
    bodyId: frame?.body_id ?? frame?.bodyId ?? null,
    embodimentId: frame?.embodiment_id ?? frame?.embodimentId ?? null,
  };
}

/**
 * Mind stream coordinator.
 *
 * Owns EventSource lifecycle and arbitration between the local Physics3D
 * snapshot stream and Observatory instance streams.
 */
export class MindStreams {
  constructor({
    onTelemetry,
    onSnapshot,
    onTopology,
    onWaiting,
    onSourceState,
  } = {}) {
    this.onTelemetry = onTelemetry ?? (() => {});
    this.onSnapshot = onSnapshot ?? (() => {});
    this.onTopology = onTopology ?? (() => {});
    this.onWaiting = onWaiting ?? (() => {});
    this.onSourceState = onSourceState ?? (() => {});

    this.organism = null;
    this.fleet = null;
    this.instance = null;
    this.activeInstance = null;
    this.activeRunId = null;
    this.localMindActive = false;
    this.closed = true;
    this.sourceIdentity = {
      source: null,
      instanceId: null,
      runId: null,
      organismId: null,
      bodyId: null,
      embodimentId: null,
    };
    this.liveDecoder = new LiveObservationDecoder();
  }

  emitSourceState(status, next = {}) {
    const previous = this.sourceIdentity;
    const source = Object.hasOwn(next, 'source') ? next.source : previous.source;
    const instanceId = Object.hasOwn(next, 'instanceId') ? next.instanceId : previous.instanceId;
    const runId = Object.hasOwn(next, 'runId') ? next.runId : previous.runId;
    const organismId = Object.hasOwn(next, 'organismId') ? next.organismId : previous.organismId;
    const bodyId = Object.hasOwn(next, 'bodyId') ? next.bodyId : previous.bodyId;
    const embodimentId = Object.hasOwn(next, 'embodimentId')
      ? next.embodimentId
      : previous.embodimentId;
    const identityChanged =
      source !== previous.source ||
      instanceId !== previous.instanceId ||
      runId !== previous.runId ||
      organismId !== previous.organismId;
    const embodimentChanged =
      bodyId !== previous.bodyId || embodimentId !== previous.embodimentId;
    this.sourceIdentity = { source, instanceId, runId, organismId, bodyId, embodimentId };
    this.onSourceState({
      status,
      source,
      instanceId,
      runId,
      organismId,
      bodyId,
      embodimentId,
      reason: next.reason ?? null,
      identityChanged,
      embodimentChanged,
    });
  }

  consumeDecoderIssues() {
    let issue = this.liveDecoder.takeIssue();
    while (issue) {
      if (['gap', 'waiting-for-anchor', 'schema-error'].includes(issue.kind)) {
        this.emitSourceState('stale', {
          reason: `transport-${issue.kind}${issue.channel ? `:${issue.channel}` : ''}`,
        });
        this.onWaiting(
          true,
          issue.kind === 'schema-error'
            ? 'Observation stream contains an invalid payload — waiting for valid data.'
            : `Observation gap on ${issue.channel ?? 'stream'} — waiting for a fresh anchor…`,
        );
      } else if (issue.kind === 'rebase') {
        this.onWaiting(false, null);
      }
      issue = this.liveDecoder.takeIssue();
    }
  }

  connect() {
    this.closed = false;
    this.emitSourceState('waiting', { reason: 'connecting' });
    void this.bootstrapRecentHistory().finally(() => {
      if (this.closed) return;
      this.connectOrganism();
      this.connectFleet();
    });
  }

  async bootstrapRecentHistory() {
    try {
      const response = await fetch('/api/organism/history?limit=256', { cache: 'no-store' });
      if (!response.ok || this.closed) return;
      const payload = await response.json();
      const frames = Array.isArray(payload?.items) ? payload.items : [];
      let previousIdentity = null;
      for (let index = 0; index < frames.length; index += 1) {
        if (this.closed) return;
        const frame = frames[index];
        if (!frame || frame.type !== 'observed_frame') continue;
        const identity = frameIdentity(frame);
        const identityKey = `${identity.runId ?? ''}|${identity.organismId ?? ''}|${identity.instanceId ?? ''}`;
        // Recent history can span multiple runs. Never compose one historical
        // frame into presentation state left by another identity.
        if (previousIdentity !== null && previousIdentity !== identityKey) {
          this.emitSourceState('waiting', {
            source: 'physics3d',
            ...identity,
            reason: 'historical-identity-boundary',
          });
        }
        previousIdentity = identityKey;
        const meta = {
          source: 'physics3d',
          ...identity,
          coherentFrame: true,
          frameTick: frame.tick ?? null,
          historical: true,
          historicalFinal: index === frames.length - 1,
        };
        for (const component of [frame.body, frame.cognition, frame.vitals]) {
          if (component?.type) this.onTelemetry(component, meta);
        }
        if (frame.mind) {
          this.onSnapshot(frame.mind, {
            ...meta,
            tick: frame.tick ?? null,
          });
        }
      }
    } catch {
      // Recent history is observer convenience only. Live observation must
      // start even if this optional bootstrap endpoint is unavailable.
    }
  }

  close() {
    this.closed = true;
    for (const key of ['organism', 'fleet', 'instance']) {
      const source = this[key];
      if (source) {
        try { source.close(); } catch {}
        this[key] = null;
      }
    }
    this.activeInstance = null;
    this.activeRunId = null;
    this.localMindActive = false;
    this.liveDecoder.reset();
    this.emitSourceState('disconnected', {
      source: null,
      instanceId: null,
      runId: null,
      organismId: null,
      bodyId: null,
      embodimentId: null,
      reason: 'closed',
    });
  }

  connectOrganism() {
    if (this.organism) this.organism.close();
    this.organism = new EventSource('/api/organism');

    this.organism.addEventListener('message', (event) => {
      let data;
      try { data = JSON.parse(event.data); } catch { return; }
      data = this.liveDecoder.decode(data);
      this.consumeDecoderIssues();
      if (!data?.type) return;

      if (data.type === 'observed_frame' && data.source === 'physics3d') {
        this.localMindActive = true;
        const identity = frameIdentity(data);
        if (!identity.runId) {
          this.emitSourceState('stale', {
            source: 'physics3d',
            ...identity,
            reason: 'missing-run-identity',
          });
          this.onWaiting(true, 'Physics3D frame has no run identity — refusing to compose it.');
          return;
        }
        this.emitSourceState('live', { source: 'physics3d', ...identity });
        if (this.instance) {
          this.instance.close();
          this.instance = null;
        }
        this.activeInstance = null;
        this.activeRunId = null;
        for (const component of [data.body, data.cognition, data.vitals]) {
          if (component?.type) {
            this.onTelemetry(component, {
              source: 'physics3d',
              ...identity,
              coherentFrame: true,
              frameTick: data.tick ?? null,
            });
          }
        }
        if (data.mind) {
          this.onSnapshot(data.mind, {
            source: 'physics3d',
            ...identity,
            tick: data.tick ?? null,
            coherentFrame: true,
          });
        }
        return;
      }

      if (
        data.source === 'physics3d' &&
        ['body', 'cognition', 'vitals'].includes(data.type)
      ) {
        // Claim the local source immediately and expose its identity before the
        // coherent frame arrives. This clears presentation from a previous run
        // before any new-run field can be shown.
        this.localMindActive = true;
        this.emitSourceState('waiting', {
          source: 'physics3d',
          runId: data.run_id ?? null,
          instanceId: data.instance_id ?? null,
          organismId: data.organism_id ?? null,
          bodyId: data.body_id ?? null,
          embodimentId: data.embodiment_id ?? null,
          reason: 'awaiting-coherent-frame',
        });
        if (this.instance) {
          this.instance.close();
          this.instance = null;
        }
        this.activeInstance = null;
        this.activeRunId = null;
        return;
      }

      if (data.type === 'mind_snapshot' && data.source === 'physics3d' && data.snapshot) {
        this.localMindActive = true;
        const identity = {
          instanceId: data.instance_id ?? null,
          runId: data.run_id ?? null,
          organismId: data.organism_id ?? null,
          bodyId: data.body_id ?? null,
          embodimentId: data.embodiment_id ?? null,
        };
        this.emitSourceState('waiting', {
          source: 'physics3d',
          ...identity,
          reason: data.coherent_frame_follows ? 'awaiting-coherent-frame' : null,
        });
        if (this.instance) {
          this.instance.close();
          this.instance = null;
        }
        this.activeInstance = null;
        this.activeRunId = null;
        if (!data.coherent_frame_follows) {
          this.emitSourceState('live', { source: 'physics3d', ...identity });
          this.onSnapshot(data.snapshot, { source: 'physics3d', ...identity });
        }
        return;
      }

      if (!this.localMindActive && this.activeInstance && data.instance_id !== this.activeInstance) {
        return;
      }
      if (this.activeRunId && data.run_id && data.run_id !== this.activeRunId) {
        return;
      }
      if (!this.activeInstance) this.onWaiting(false, null);

      this.onTelemetry(data);
    });

    this.organism.onerror = () => {
      this.emitSourceState('stale', { reason: 'organism-stream-disconnected' });
      this.onWaiting(true, 'SSE /api/organism disconnected — retrying…');
    };
  }

  async connectFleet() {
    if (this.fleet) this.fleet.close();

    try {
      const response = await fetch('/api/state', { cache: 'no-store' });
      if (this.closed) return;
      if (response.ok) {
        const state = await response.json();
        const observatory = state?.sources?.observatory;
        if (observatory && observatory.available === false) {
          this.onWaiting(
            true,
            'Observatory is not available — local organism telemetry remains active.',
          );
          return;
        }
      }
    } catch {
      // Source discovery is advisory. The EventSource attempt below remains
      // the transport-level fallback for older or partially available servers.
    }

    if (this.closed) return;

    try {
      this.fleet = new EventSource('/fleet');
    } catch {
      this.onWaiting(
        true,
        'Observatory fleet is unavailable — showing local organism telemetry only.',
      );
      return;
    }

    this.fleet.onmessage = (event) => {
      let payload;
      try { payload = JSON.parse(event.data); } catch { return; }

      const instances = Array.isArray(payload.instances) ? payload.instances : [];
      const alive = instances.filter((item) => item.liveness === 'alive');
      if (this.localMindActive) return;

      const current = this.activeInstance
        ? alive.find((item) => item.instance_id === this.activeInstance)
        : null;

      if (current) {
        const nextRunId = current.run_id ?? null;
        this.emitSourceState('live', {
          source: 'observatory',
          instanceId: current.instance_id,
          runId: nextRunId,
          organismId: current.organism_id ?? null,
        });
        if (nextRunId !== this.activeRunId) {
          this.connectInstance(current.instance_id, nextRunId, current.organism_id ?? null);
        }
        return;
      }

      if (this.activeInstance && this.instance) {
        this.instance.close();
        this.instance = null;
      }
      this.activeInstance = null;
      this.activeRunId = null;

      if (alive.length === 1) {
        this.connectInstance(alive[0].instance_id, alive[0].run_id ?? null, alive[0].organism_id ?? null);
      } else if (alive.length > 1) {
        // Never make scientific identity depend on array ordering.
        this.emitSourceState('waiting', {
          source: 'observatory',
          instanceId: null,
          runId: null,
          organismId: null,
          reason: 'multiple-live-instances',
        });
        this.onWaiting(true, `${alive.length} live Observatory instances are available — no instance was selected automatically.`);
      } else {
        this.emitSourceState('waiting', {
          source: null,
          instanceId: null,
          runId: null,
          organismId: null,
          reason: 'no-live-instance',
        });
        this.onWaiting(true, 'Waiting for a live Observatory instance…');
      }
    };

    this.fleet.onerror = () => {
      this.onWaiting(
        true,
        'Observatory fleet unavailable — fallback to the organism stream is active.',
      );
      if (this.fleet) {
        try { this.fleet.close(); } catch {}
        this.fleet = null;
      }
    };
  }

  connectInstance(instanceId, runId = null, organismId = null) {
    if (
      this.activeInstance === instanceId &&
      this.activeRunId === runId &&
      this.instance
    ) {
      return;
    }

    if (this.instance) this.instance.close();
    this.activeInstance = instanceId;
    this.activeRunId = runId;
    this.emitSourceState('live', { source: 'observatory', instanceId, runId, organismId });
    this.instance = new EventSource(`/instances/${instanceId}`);

    this.instance.onmessage = (event) => {
      let payload;
      try { payload = JSON.parse(event.data); } catch { return; }

      if (payload.run_id && this.activeRunId && payload.run_id !== this.activeRunId) {
        return;
      }
      if (payload.run_id && !this.activeRunId) {
        this.activeRunId = payload.run_id;
        this.emitSourceState('live', {
          source: 'observatory',
          instanceId,
          runId: this.activeRunId,
          organismId: payload.organism_id ?? organismId,
        });
      }

      if (payload.snapshot) {
        this.onSnapshot(payload.snapshot, {
          source: 'observatory',
          instanceId,
          runId: this.activeRunId,
          organismId: payload.organism_id ?? organismId,
        });
      }
      if (payload.topology) {
        this.onTopology(payload.topology, {
          instanceId,
          runId: this.activeRunId,
          organismId: payload.organism_id ?? organismId,
        });
      }
    };

    this.instance.onerror = () => {
      this.emitSourceState('stale', {
        source: 'observatory',
        instanceId,
        runId: this.activeRunId,
        organismId,
        reason: 'instance-stream-disconnected',
      });
      this.onWaiting(true, `Connection to instance ${instanceId} lost — retrying…`);
    };
  }
}
