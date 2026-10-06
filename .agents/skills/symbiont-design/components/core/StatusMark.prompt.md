Shows the epistemic or lifecycle status of a claim, study, artifact or ADR using the repository vocabulary.

```jsx
<StatusMark status="negative" label="H1 not supported" />
<StatusMark status="partially-superseded" />
<StatusMark status="failing" />
```

- Evidence: implemented, tested, observed, supported, intended, historical, unresolved.
- Study: planned, preregistered, running, discovery, partial, negative, inconclusive, superseded, frozen.
- ADR: proposed, accepted, partially-superseded. Only `failing` is coloured.
