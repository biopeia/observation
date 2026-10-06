function ScreenEvidence() {
  const { DocHeader, SectionHeading, DataTable, StatusMark, Callout, CodeBlock } = window.SymbiontDesignSystem_45c50a;
  const rows = [
    ["E1", "Yoked External Causation", "negative", "H1 not supported"],
    ["E2", "Tool / Body Distinction", "negative", "H1 not supported"],
    ["E3", "Temporal Causality", "negative", "H1 not supported"],
    ["E4", "Causal Revision", "negative", "H1 not supported"],
    ["E5", "Somatic Correlation Trap", "negative", "H1 not supported"],
    ["E6", "Hidden Common Cause", "negative", "H1 not supported"],
    ["E7", "Heredity Leakage", "supported", "no learned-state leakage observed in tested scope"],
    ["E8", "Label Invariance", "failing", "fails; open P0 integrity issue"],
  ].map(([e, n, s, r]) => ({ e, n, s: <StatusMark status={s} size="sm" />, r }));
  return (
    <article>
      <DocHeader docType="study" id="E1–E8" status="frozen" domains={["lab", "embodiment"]}
        title="Embodied agency: unified falsification battery"
        abstract="Current embodiment evidence includes a unified falsification battery. These results define the next causal research problem; they are not defects to edit away."
        meta={[{ label: "Programme", value: "Embodied Agency E1–E6" }, { label: "Record", value: "lab/research/STATUS.md", mono: true }, { label: "Owner gate", value: "Scientific protocol" }]} />
      <Callout kind="warning" title="E8 Label Invariance fails" status="failing">P0 experimental-integrity failure; remediation required.</Callout>
      <SectionHeading number="1" title="Results" id="results" />
      <DataTable number="1" caption="Battery outcomes. Negative results are retained and are not rewritten when later work changes the mechanism." columns={[{ key: "e", label: "Exp.", mono: true, width: 60 }, { key: "n", label: "Experiment" }, { key: "s", label: "Status", width: 150 }, { key: "r", label: "Result" }]} rows={rows} />
      <Callout kind="principle">A capability being implemented does not establish scientific generalisation. A completed experiment remains bounded by its preregistered conditions.</Callout>
      <SectionHeading number="2" title="Evidence lifecycle" id="lifecycle" />
      <CodeBlock language="text" title="lab/research/README.md" code={"PLANNED PREREGISTERED RUNNING DISCOVERY PARTIAL SUPPORTED NEGATIVE\nINCONCLUSIVE SUPERSEDED FROZEN"} />
      <div style={{ display: "flex", flexWrap: "wrap", gap: "10px 20px", marginBottom: 24 }}>
        {["planned", "preregistered", "running", "discovery", "partial", "supported", "negative", "inconclusive", "superseded", "frozen"].map((s) => <StatusMark key={s} status={s} />)}
      </div>
      <SectionHeading number="3" title="Reproduce" id="reproduce" />
      <CodeBlock tone="night" language="bash" title="validation layers" code={"pytest -o addopts= tests/integration tests/experimental_integrity\npytest -o addopts= tests/contract tests/experiments\npython scripts/agentctl.py verify   # governance check"} />
      <Callout kind="note">Held-out, confirmation and replication runs require an explicit owner decision before launch.</Callout>
    </article>
  );
}
window.ScreenEvidence = ScreenEvidence;
