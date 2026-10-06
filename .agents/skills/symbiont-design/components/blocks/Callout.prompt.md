Typed block for one information class in a scientific document — invariant, principle, hypothesis, evidence, implementation, limitation, warning, decision, superseded, note.

```jsx
<Callout kind="invariant" id="INV-01">Ground truth belongs to Lab/evaluator.</Callout>
<Callout kind="evidence" strength={2} scope="seed 11" status="observed" title="Plateau below capacity">…</Callout>
<Callout kind="superseded" supersededBy="ADR-0066">…</Callout>
```

- Kind is encoded by structure: heavy rule (invariant/decision), dashed (hypothesis), aside ground (implementation), hatch (superseded), vermilion (warning/limitation only).
