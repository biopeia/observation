function BoundaryDiagram() {
  const { DomainGlyph } = window.SymbiontDesignSystem_45c50a;
  const nodes = [["environment", "World", "external state and dynamics"], ["embodiment", "Body", "physical substrate"], ["embodiment", "Embodiment", "bounded relationship"], ["symbiont", "Symbiont", "persistent organism"]];
  return (
    <div style={{ display: "flex", flexWrap: "wrap", alignItems: "stretch", width: "100%", gap: 0 }}>
      {nodes.map(([d, n, s], i) => (
        <React.Fragment key={n}>
          <div style={{ flex: "1 1 120px", padding: "14px 14px 12px", borderTop: `2px solid var(--dom-${d})`, background: "var(--night-1)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}><DomainGlyph domain={d} size={9} /><span style={{ font: "500 15px/1.2 var(--font-sans)", color: "var(--night-ink-1)" }}>{n}</span></div>
            <div style={{ font: "12px/1.4 var(--font-sans)", color: "var(--night-ink-2)", marginTop: 6 }}>{s}</div>
          </div>
          {i < nodes.length - 1 ? <div style={{ flex: "0 0 36px", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--night-ink-3)" }}>≠</div> : null}
        </React.Fragment>
      ))}
    </div>
  );
}

function ScreenChapter() {
  const { DocHeader, SectionHeading, Figure, Callout, SourceList } = window.SymbiontDesignSystem_45c50a;
  return (
    <article>
      <DocHeader docType="chapter" id="§ 03" status="implemented" domains={["environment", "embodiment", "symbiont"]}
        title="World, body and embodiment"
        subtitle="Why three entities are required"
        abstract="A body is not an organism and an embodiment is not a body. The distinction is easiest to see during change."
        meta={[{ label: "Source", value: "symbiont/docs/03-world-body-and-embodiment.md", mono: true }, { label: "Runtime", value: "Physics3D" }, { label: "Read next", value: "§ 04 Perception" }]} />
      <div className="sym-prose">
        <p>If the same Symbiont is moved from one anthropomorphic body to a crawler, the organism persists, the old physical body does not, and the relationship between organism and physical surface is rebuilt. Calling all three “the body” makes it impossible to say what was learned, what was retained and what must be reacquired.</p>
      </div>
      <Figure number="3.1" tone="night" caption="The four entities of the boundary. Each is owned by a different domain; none may be inferred from another." source="symbiont/docs/index.md"><BoundaryDiagram /></Figure>
      <SectionHeading number="3.1" title="Physical body" id="body" />
      <div className="sym-prose">
        <p>In Physics3D the body is represented by PyBullet state plus an apparatus implementation. Body descriptors define the available receptor and effector sets. The runtime stores physical body identity explicitly; it does not infer identity from physical state or migrate older checkpoint formats.</p>
        <p>The body can be affected without cognition. Gravity, collision, joint limits, surface contact and environmental forces are physical dynamics. The laboratory can inspect them even when no corresponding internal representation exists.</p>
      </div>
      <SectionHeading number="3.2" title="Apparatus" id="apparatus" level={3} />
      <div className="sym-prose"><p>The apparatus is the interface exposed by the body. On the incoming side it supplies receptor values. On the outgoing side it accepts validated actuator channels.</p></div>
      <SectionHeading number="3.3" title="Embodiment contract" id="contract" />
      <div className="sym-prose"><p>The core <code>EmbodimentContract</code> binds a perceptual surface, actuator surface, timing contract and mutually exclusive actuator groups. In Physics3D this contract is derived from the actual apparatus counts and effector constraints.</p></div>
      <Callout kind="implementation" source="src/symbiont/core/embodiment/contract.py">The contract captures the actionable/sensible surface without claiming that the organism knows the anatomical meaning of those channels.</Callout>
      <SectionHeading number="3.4" title="Body schema" id="schema" />
      <div className="sym-prose"><p><code>BodySchemaEngine</code> is organism-owned inferred structure. It is not a mirror of the PyBullet model. It is built from relationships available through experience and should therefore be read as an internal model of sensorimotor organisation rather than a copy of external anatomy.</p></div>
      <Callout kind="limitation" title="Observatory views are observer reconstructions">A human-friendly skeletal view may draw a right arm because the observer knows the body's morphology. The organism's schema may contain only opaque channels, learned couplings and confidence about their relations.</Callout>
      <SectionHeading number="3.5" title="What should survive a body change?" id="survive" />
      <div className="sym-prose"><p>The answer is not “everything” or “nothing”. Persistence is mechanism-specific. Organism identity, genome and general cognitive history may survive; physical pose and body integrity do not.</p></div>
      <SourceList items={[
        { kind: "design", path: "docs/design/embodiment/embodiment-v2.md" },
        { kind: "design", path: "docs/design/embodiment/embodiment-memory-v1.md" },
        { kind: "code", path: "src/symbiont/core/embodiment/body_schema.py" },
        { kind: "code", path: "src/symbiont_lab/physics3d/apparatus.py" },
      ]} />
    </article>
  );
}
window.ScreenChapter = ScreenChapter;
