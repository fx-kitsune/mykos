# MyKOS Fold 1.0

40 original SVG icons for the MyKOS concept. Source geometry: tools/build-icons.cjs. Run node tools/build-icons.cjs to regenerate the exports and catalog.

## Construction
- ViewBox: 0 0 24 24; normal drawing bounds 2–22.
- Stroke: 1.6 units; round caps and joins.
- A 2-unit clipped corner on enclosing shapes echoes the MyKOS mark. Do not add a cut to every symbol: preserve familiar meanings.
- Single-color currentColor; secondary construction lines use 40% opacity.
- UI sizes: 16 / 20 / 24 / 32; application emblems: 56 / 72 / 96. Scale stroke with the SVG. Never distort the viewBox or mix stroke widths.
- Default, selected, disabled colors come from the interface, not the SVG. Disabled opacity: 35%.
- App emblems use a clipped container, matte material colors, and the same underlying glyph. No baked shadows or gradients.

## Files
Individual name.svg assets, sprite.svg with named symbols, and ../../icons.js for inline rendering. ../../icons.html is the visual catalog. Icons communicate meaning alongside visible labels or aria-label on their controls; decorative SVGs are aria-hidden.

## Web usage
Inline: icon('files') after loading icons.js. Sprite: <svg><use href="assets/icons/sprite.svg#files" /></svg>. External img assets use their own currentColor context, so use inline SVG or a sprite for theme-aware color.
