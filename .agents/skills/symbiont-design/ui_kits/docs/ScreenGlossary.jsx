function ScreenGlossary() {
  const { DocHeader, SectionHeading, StatusMark } = window.SymbiontDesignSystem_45c50a;
  const Term = ({ t, children, mono }) => (
    <div style={{ display: "flex", flexWrap: "wrap", columnGap: 24, rowGap: 4, padding: "14px 0", borderBottom: "1px solid var(--rule-1)" }}>
      <dt style={{ flex: "0 0 200px", font: "600 var(--fs-body)/1.4 var(--font-sans)" }}>{t}</dt>
      <dd style={{ flex: "1 1 320px", margin: 0, font: "var(--type-body)", maxWidth: "62ch", textWrap: "pretty" }}>{children}</dd>
    </div>
  );
  return (
    <article>
      <DocHeader docType="reference" id="root.glossary" domains={["symbiont", "lab"]} title="Glossary of epistemological and experimental terms" />
      <SectionHeading number="1" title="Experimental hierarchy" id="hier" />
      <dl style={{ margin: 0 }}>
        <Term t="Protocol">A defined scientific procedure and measurement methodology (e.g. <code className="ic">attention.causal</code>). Independent of software versions.</Term>
        <Term t="Experiment">A specific hypothesis-driven investigation bound to concrete parameters, hypotheses, and success criteria.</Term>
        <Term t="Run">A single deterministic execution of an experiment or protocol under a single world seed and parameter configuration.</Term>
        <Term t="Study">A collection of comparable runs across parameter sweeps and replication seeds.</Term>
      </dl>
      <SectionHeading number="2" title="Artifact status lifecycle" id="life" />
      <dl style={{ margin: 0 }}>
        <Term t={<StatusMark status="working" />}>Mutable local run or prototype results residing in <code className="ic">.symbiont/</code>. Not tracked in version control.</Term>
        <Term t={<StatusMark status="validated" />}>Run or study that has passed all protocol invariants, integrity assertions, and replication criteria.</Term>
        <Term t={<StatusMark status="frozen" />}>Formally accepted scientific record archived in <code className="ic">research/</code>. Immutable baseline for publications and future comparisons.</Term>
        <Term t={<StatusMark status="superseded" />}>Historical study preserved in <code className="ic">research/</code> whose methodological premise was found flawed or refined by a subsequent audit.</Term>
      </dl>
      <SectionHeading number="3" title="Organism vocabulary" id="org" />
      <dl style={{ margin: 0 }}>
        <Term t="Genome">The closed, versioned, kernel-validated configuration for one individual's development.</Term>
        <Term t="Phenotype">The plastic cognitive graph (nodes/edges/weights) an individual develops during its life, distinct from its genome.</Term>
        <Term t="EmbodimentEpisode">One continuous period of one Symbiont in one Body. A new Body always starts a new episode; the previous one is closed and archived.</Term>
        <Term t="Re-embodiment">The canonical move of a Symbiont into a fresh Body: knowledge is carried, Body state is replaced, execution authority is withdrawn.</Term>
      </dl>
    </article>
  );
}
window.ScreenGlossary = ScreenGlossary;
