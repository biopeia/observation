function ScreenIndex({ onNavigate }) {
  const { DocHeader, SectionHeading, CodeBlock, Callout, DataTable, DomainTag } = window.SymbiontDesignSystem_45c50a;
  const link = (id, t) => <a href={`#${id}`} onClick={(e) => { e.preventDefault(); onNavigate(id); }}>{t}</a>;
  return (
    <article>
      <DocHeader docType="reference" id="symbiont/docs/index.md" domains={["symbiont"]}
        title="Symbiont — scientific description of the organism"
        abstract="This corpus is the canonical entry point for studying Symbiont as a computational organism. It synthesizes design specifications, implementation notes and historical documents with the current implementation, and separates what exists from what was proposed." />
      <div className="sym-prose">
        <p>Symbiont should be read at three depths. A first reading explains the organism in ordinary scientific language. The anatomy documents then follow concrete processes end to end. The reference and atlas layers provide the exact ownership, implementation and causal relationships needed for verification.</p>
      </div>
      <Callout kind="principle" title="The central architectural distinction">A world contains external state and dynamics. A body is a physical substrate in that world. An embodiment is the historically bounded relationship between one Symbiont and one body contract. Symbiont is the persistent organism whose internal organization may survive the end of a particular body.</Callout>
      <CodeBlock language="text" code={"World != Body != Embodiment != Symbiont"} />
      <SectionHeading number="1" title="Reading path" id="path" />
      <div className="sym-prose">
        <p>Start with {link("c00", "Foundations and epistemology")}, then read {link("c01", "System and boundaries")}. From there the natural path is lifecycle, embodiment, perception, physiology, cognition, agency, learning, generative cognition and social/lineage processes.</p>
      </div>
      <SectionHeading number="2" title="Five domains" id="domains" />
      <DataTable columns={[{ key: "d", label: "Domain", width: 170 }, { key: "p", label: "Package", mono: true, width: 120 }, { key: "r", label: "Responsibility" }]} rows={[
        { d: <DomainTag domain="symbiont" />, p: "symbiont", r: "the organism / research subject" },
        { d: <DomainTag domain="embodiment" />, p: "embodiment", r: "couplings between the organism and a concrete form of existence" },
        { d: <DomainTag domain="modality" />, p: "modality", r: "signal channels; no cognitive meaning" },
        { d: <DomainTag domain="environment" />, p: "environment", r: "external laws, dynamics and ground truth" },
        { d: <DomainTag domain="lab" />, p: "lab", r: "composition, experiments, studies, observation, analysis" },
      ]} />
      <Callout kind="invariant" id="README §Architecture">symbiont, embodiment, modality and environment are peer, self-contained libraries: none imports another, none imports lab. Lab is the only composition root.</Callout>
      <SectionHeading number="3" title="What is canonical here" id="canonical" />
      <div className="sym-prose">
        <p>This corpus is canonical for explanation of the current system. It does not make old specifications disappear. A specification answers “what was intended”; this corpus answers “how the present system is organised and what evidence supports that description”.</p>
      </div>
    </article>
  );
}
window.ScreenIndex = ScreenIndex;
