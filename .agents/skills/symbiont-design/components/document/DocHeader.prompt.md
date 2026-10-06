Document masthead: type, id, status, domains, serif title, gutter-labelled abstract and metadata grid — top of every spec, ADR, chapter or study.

```jsx
<DocHeader docType="adr" id="ADR-0013" status="accepted" domains={["symbiont","embodiment"]} title="…" abstract="…" meta={[{label:"Introduced in",value:"v0.30.0"}]} />
```

- docType: chapter, adr, specification, study, protocol, reference, anatomy, history, audit.
- `supersededBy` adds a hatched notice; historical docs render title in ink-2.
