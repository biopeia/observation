const { DocNav, SearchField, Toc, Breadcrumb, DomainGlyph } = window.SymbiontDesignSystem_45c50a;

const NAV = [
  { label: "Canonical corpus", domain: "symbiont", items: [
    { id: "index", label: "Scientific description" },
    { id: "c00", number: "00", label: "Foundations and epistemology" },
    { id: "c01", number: "01", label: "System and boundaries" },
    { id: "c03", number: "03", label: "World, body and embodiment" },
    { id: "c04", number: "04", label: "Perception and sensory development" },
    { id: "c11", number: "11", label: "Persistence, provenance and re-embodiment" },
  ] },
  { label: "Decisions", items: [
    { id: "adr11", number: "0011", label: "Visual apparatus and perceptual topology", status: "partially-superseded" },
    { id: "adr13", number: "0013", label: "Longitudinal re-embodiment", status: "accepted" },
  ] },
  { label: "Evidence", domain: "lab", items: [
    { id: "evidence", label: "Embodied agency E1–E8", status: "failing" },
  ] },
  { label: "Reference", items: [
    { id: "glossary", label: "Glossary" },
  ] },
];

function DocsShell({ page, onNavigate, crumbs, toc, activeToc, children }) {
  const [q, setQ] = React.useState("");
  return (
    <div className="shell">
      <aside className="shell-nav">
        <a href="#index" onClick={(e) => { e.preventDefault(); onNavigate("index"); }} style={{ display: "block", marginBottom: 20 }}>
          <img src="../../assets/logo/logo_horizontal.png" alt="Symbiont" style={{ height: 40, display: "block", marginLeft: -8 }} />
        </a>
        <DocNav sections={NAV} activeId={page} onSelect={onNavigate} header={<SearchField value={q} onChange={setQ} />} />
        <div style={{ marginTop: 32, paddingTop: 12, borderTop: "1px solid var(--rule-1)", display: "grid", gap: 6 }}>
          {["symbiont", "embodiment", "modality", "environment", "lab"].map((d) => (
            <span key={d} style={{ display: "flex", alignItems: "center", gap: 8, fontFamily: "var(--font-mono)", fontVariationSettings: '"wdth" 87.5', fontSize: 10.5, color: "var(--ink-3)" }}>
              <DomainGlyph domain={d} size={8} />{d}/
            </span>
          ))}
        </div>
      </aside>
      <main className="shell-main">
        <div style={{ marginBottom: 32 }}><Breadcrumb items={crumbs} /></div>
        {children}
        <footer style={{ marginTop: 96, paddingTop: 12, borderTop: "1px solid var(--rule-2)", display: "flex", flexWrap: "wrap", justifyContent: "space-between", gap: 12, fontFamily: "var(--font-mono)", fontVariationSettings: '"wdth" 87.5', fontSize: 10.5, color: "var(--ink-3)" }}>
          <span>alessbarb/symbiont-lab · main</span>
          <span>Historical results remain evidence for their original scope.</span>
        </footer>
      </main>
      <aside className="shell-toc">{toc ? <Toc items={toc} activeId={activeToc} /> : null}</aside>
    </div>
  );
}

Object.assign(window, { DocsShell });
