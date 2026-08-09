# Post-merge visual polish checklist

This checklist maps the 18 follow-up screenshots supplied after visual-system PR #79.

- [x] 1. Four-card homepage panel uses equal tracks, matched internal rows and a complete outer border, including the far-right edge.
- [x] 2. Both homepage clinic addresses use a larger responsive text size while the paired cards retain equal rows and height.
- [x] 3. The “Before your visit” heading and FAQ receive a CSS visibility fail-safe in both themes and no longer depend on reveal timing.
- [x] 4. About and Locations desktop dropdowns have a stable readable width; doctor and clinic article spacing is reduced without collapsing content rhythm.
- [x] 5. Doctor focus cards use equal-height rows, consistent padding and left-aligned heading/body geometry.
- [x] 6. The academic-background disclosure uses the shared fixed marker column.
- [x] 7. Doctor clinic cards use the architectural 2px rectangle family with equal heights.
- [x] 8. All shared FAQ/deep-dive plus and minus markers use the same centered 32px column.
- [x] 9. Clinical photographs use `object-fit: contain`; controls, counter and medical note remain fully visible.
- [x] 10. Article list items have restrained gold diamond bullets and meaningful inline emphasis regains a gold treatment.
- [x] 11. The same bullet hierarchy applies to lists inside and outside expandable article boxes.
- [x] 12. The sticky article rail uses continuous scroll-position tracking and explicitly activates the final section at the page bottom.
- [x] 13. Nearby-area pointers on both clinic pages use architectural rectangles; Central Jammu and Northern Jammu are title-cased in visible copy only.
- [x] 14. Contact and shared clinic-choice cards use the same rectangular geometry and aligned height rules.
- [x] 15. Related-care navigation uses a rectangular aligned grid instead of floating rounded pills.
- [x] 16. The current theme control is legible in both themes. The later custom-artwork pass must provide separate light and dark artwork for every replacement icon.
- [x] 17. Open appointment FAQ answers use a controlled reading measure and an intentional inset treatment.
- [x] 18. The mobile menu button shows three high-contrast lines and retains an accessible expanded-state transformation.

## Deferred artwork requirement

No low-resolution clay icon was enlarged or regenerated in this pass. A future icon-artwork pass must replace the entire current set as a coherent high-resolution family and include explicit light-theme and dark-theme variants where the surrounding surface or symbol contrast changes.
