# Low-cost validation plan

Use this sequence before any production merge.

1. Review branch diff and CSS syntax.
2. Run local/manual browser checks first; do not use GitHub Actions for iteration.
3. Check representative routes at 390px/414px mobile and desktop:
   - `/`
   - `/conditions/`
   - `/treatments/`
   - `/treatments/mnrf-treatment/`
   - `/treatments/acne-scar-treatment/`
   - `/dr-cheena-langer/`
   - `/locations/`
   - `/locations/karan-nagar/`
   - `/book-appointment/`
   - `/blog/`
4. Verify both light and dark themes.
5. Specifically verify:
   - no one-character/one-word-column wrapping;
   - mobile rail hidden below 1181px;
   - footer headings remain compact;
   - homepage fact cards are compact and non-redundant;
   - mobile navigation uses consistent link styling;
   - Call/WhatsApp/Book does not obscure page content;
   - Wagtail userbar stays above the public action bar;
   - clinical gallery heading/background follows the active theme;
   - semantic checks display as a real check mark;
   - directory headings fit at 390px;
   - no horizontal overflow.
6. Re-run the existing colour-contrast checks locally when possible.
7. Only after visual/manual review, merge once so Render receives one production deployment.
8. If budget permits later, use one deliberate `main` QA run as the final regression gate rather than iterative Action runs.
