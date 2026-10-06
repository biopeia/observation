Marks which of the five domains (symbiont, embodiment, modality, environment, lab) a document, section or entity belongs to; use wherever ownership matters.

```jsx
<DomainTag domain="embodiment" />
<DomainTag domain="lab" variant="filled" />
<DomainGlyph domain="modality" size={8} />
```

- `variant`: label (default) · filled (tinted chip, for tables/headers) · glyph (shape only, for dense lists).
- Each domain has a shape: circle, square, diamond, ground, ring. Never use domain hues for anything else.
