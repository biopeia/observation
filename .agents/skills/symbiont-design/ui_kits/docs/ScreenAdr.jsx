function ScreenAdr() {
  const { DocHeader, SectionHeading, DecisionList, Callout, Lineage } = window.SymbiontDesignSystem_45c50a;
  return (
    <article>
      <DocHeader docType="adr" id="ADR-0011 · ADR-EW-004" status="partially-superseded" domains={["modality", "embodiment"]}
        title="Visual apparatus and perceptual topology"
        meta={[{ label: "Status", value: "Accepted. Decision 2 is reversible." }, { label: "Introduced in", value: "Milestone EW-C" }, { label: "Superseded in part by", value: "ADR-0066", mono: true }]} />
      <Callout kind="superseded" id="2026-10-04" supersededBy="ADR-0066">After the substrate cut the array is sampled by a deterministic CPU ray caster owned by modality rather than by the physics engine's renderer. The receptor contract, topology, cadence and isolation rules here remain authoritative.</Callout>
      <SectionHeading number="1" title="Context" id="context" />
      <div className="sym-prose"><p>The Experience &amp; World specification requires Vision to arrive as a causal apparatus: physical world → apparatus → physical sample → opaque receptor channels → cognition. Observer geometry (<code>world_scene</code>, <code>PhysicsWorldObserver.entities</code>) is not a valid substitute.</p></div>
      <SectionHeading number="2" title="Decision" id="decision" />
      <DecisionList items={[
        { title: "Topology", body: <>Physical receptor adjacency is apparatus-given structure. Grouping into sources is acquired structure. The apparatus owns a <code>PerceptualTopology</code>: neighbour lists over opaque receptor ids.</> },
        { title: "A new body kind, not a modified body", status: "intended", statusDetail: "reversible", body: <>Vision ships as <code>anthropomorphic-v6-vision</code>. The receptor contract of <code>anthropomorphic-v6</code> is left unchanged.</> },
        { title: "Apparatus", status: "superseded", statusDetail: "renderer identity · ADR-0066", body: "A single receptor array is mounted on the head link. Each receptor delivers a bounded luminance value in [0, 1]." },
        { title: "Size and sensory budget", body: "The array is 12×12 (144 receptors). BodyDescriptor.sensory_capacity makes the budget per body: 256 for every existing body, 512 for the vision body." },
        { title: "Opaque identities", body: "Visual receptors extend the existing rec.N namespace (rec.107–rec.250) through a fixed, versioned permutation of array positions." },
      ]} />
      <Callout kind="evidence" title="Closed by EW-D0 (2026-09-28/29)" strength={2} scope="seed 11, 6 × 250 ticks" status="observed">Sensors 387 → 413 → 428 → 434 → 440 → 440: plateau below the 512 capacity, 0 capacity rejections.</Callout>
      <Callout kind="limitation" title="Open: bundle growth">The portable bundle grows ~3.5 MB per 250 ticks (29 MB at 1500) without plateau — an age-dependent storage concern (Gate J), not a sensory-budget one.</Callout>
      <SectionHeading number="3" title="Consequences" id="consequences" />
      <div className="sym-prose"><ul><li>Gate D (visual acquisition) is not claimed. EW-C delivers only the substrate.</li><li>Raw receptor-field observer transport is not chosen here. It must be benchmarked before any Vision UI.</li></ul></div>
      <Lineage items={[
        { id: "ADR-0066", title: "MuJoCo physics engine and engine-independent vision", status: "accepted", date: "2026-10-04", relation: "supersedes decision 3 (renderer identity) of" },
        { id: "ADR-0011", title: "Visual apparatus and perceptual topology", status: "partially-superseded" },
      ]} />
    </article>
  );
}
window.ScreenAdr = ScreenAdr;
