# Approved clay artwork implementation

All supplied artwork is retained at its original 1024 × 1024 resolution in
`home/static_src/visual-cues/approved-2026/`. The build creates 64, 128, 256
and 512 pixel WebP variants so high-density displays stay sharp without
serving the source JPEG to every visitor.

## Placement map

1. `acne-care.jpg`: Acne, pimples and scars.
2. `pigmentation-care.jpg`: Pigmentation and uneven tone.
3. `hair-scalp-care.jpg`: Hair fall and scalp concerns.
4. `fungal-infection-care.jpg`: Fungal and recurrent infections.
5. `allergy-inflammatory-rashes.jpg`: Allergy, eczema and itching.
6. `skin-quality-ageing.jpg`: Skin quality and ageing.
7. `dermatologist-diagnosis.jpg`: MBBS and MD, dermatologist-led diagnosis.
8. `medical-experience.jpg`: 20+ years in medicine.
9. `two-clinic-locations.jpg`: Two Jammu clinics.
10. `complete-care.jpg`: Complete medical, laser, hair and aesthetic care.
11. `personalised-plan.jpg`: Personalised treatment planning.
12. `clinical-skin-care.jpg`: Medical dermatology and clinical assessment.
13. `clinic-directions.jpg`: Homepage clinic cards and directions context.
14. `appointment-booking.jpg`: Homepage consultation and booking card.
15. `theme-dark.jpg`: Switch-to-dark control in light mode.
16. `theme-light.jpg`: Switch-to-light control in dark mode.

The uploaded artwork has an intentional light background. It is presented as
one consistent framed icon family in both themes, with restrained hover motion
and a reduced-motion fallback. No low-resolution asset is enlarged.
