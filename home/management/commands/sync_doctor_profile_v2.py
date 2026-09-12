from django.core.management.base import BaseCommand

from home.exact_editor import extract_exact_editor_payload
from home.models import Doctor, DoctorPage, ExactPageLayout


PROFILE_PATH = "/dr-cheena-langer/"
PROFILE_MARKER = 'data-doctor-profile-version="2"'
SEO_TITLE = "Dr. Cheena Langer – Dermatologist in Jammu | Aastha"
SEO_DESCRIPTION = (
    "Consult Dr. Cheena Langer, MBBS, MD Dermatology, for skin, hair, laser "
    "and procedural care in Jammu. Book at Karan Nagar or Paloura."
)

PROFILE_HTML = r'''<main id="main-content" class="doctor-main" data-doctor-profile-version="2">
  <section class="page-hero page-hero--professional">
    <div class="container">
      <div class="page-hero-copy">
        <nav class="breadcrumbs"><a href="/">Home</a><span aria-hidden="true">/</span><span aria-current="page">Dr. Cheena Langer</span></nav>
        <span class="eyebrow">Consultant dermatologist</span>
        <h1>Dr. Cheena Langer – Consultant Dermatologist in Jammu</h1>
        <p class="lead">MBBS, MD Dermatology · Consultant Dermatologist at Aastha Skin &amp; Dermato-Cosmetic Centre, Jammu.</p>
        <p>With more than 20 years in medicine, Dr. Cheena Langer provides diagnosis-led care across medical dermatology, acne and acne scars, pigmentation, hair and scalp disorders, laser dermatology, aesthetic dermatology and selected dermato-surgical procedures.</p>
        <div class="hero-actions"><a class="button" href="/book-appointment/">Book a consultation</a><a class="button button-secondary" href="https://wa.me/917006613362" target="_blank" rel="noopener">WhatsApp the clinic</a></div>
      </div>
      <figure class="doctor-hero-media">
        <img src="/assets/images/professional/doctor-care.svg" alt="" width="720" height="820">
        <figcaption class="doctor-hero-caption">Dr. Cheena Langer · MBBS, MD Dermatology · Aastha Skin Centre, Jammu</figcaption>
      </figure>
    </div>
  </section>

  <section class="premium-summary-strip"><div class="container"><div class="premium-summary-grid">
    <div class="premium-summary-item"><strong>MBBS, MD Dermatology</strong><span>Consultant dermatologist</span></div>
    <div class="premium-summary-item"><strong>More than 20 years</strong><span>In medicine</span></div>
    <div class="premium-summary-item"><strong>Two Jammu clinics</strong><span>Karan Nagar and Paloura Chowk</span></div>
    <div class="premium-summary-item"><strong>Diagnosis-led care</strong><span>Treatment follows assessment</span></div>
  </div></div></section>

  <section class="section doctor-profile-section"><div class="container"><article class="article-stack">
    <section class="article-section doctor-intro" aria-labelledby="meet-dr-cheena">
      <div>
        <span class="section-kicker">Doctor profile</span>
        <h2 id="meet-dr-cheena">Meet Dr. Cheena Langer</h2>
        <p>Dr. Cheena Langer is an MBBS and MD Dermatology qualified Consultant Dermatologist at Aastha Skin &amp; Dermato-Cosmetic Centre in Jammu. She practises with a diagnosis-first approach because skin, hair and nail concerns that look similar may have different causes.</p>
        <p>Her clinical work spans medical dermatology, laser dermatology, hair and scalp disorders, aesthetic dermatology and minor dermato-surgical care. Her wider professional work includes postgraduate research, scientific publications, academic presentations, invited faculty activity and conference leadership.</p>
      </div>
      <aside class="doctor-intro-card" aria-label="Consultation philosophy">
        <span class="quiet-label">Care philosophy</span>
        <h3>Understand the concern before choosing the treatment</h3>
        <p>History, examination, previous treatment and relevant triggers are considered before medicines, investigations or procedures are recommended.</p>
      </aside>
    </section>

    <section class="article-section" aria-labelledby="diagnosis-treatment-heading">
      <span class="section-kicker">Approach to care</span>
      <h2 id="diagnosis-treatment-heading">Diagnosis first. Treatment second.</h2>
      <p>A treatment plan should begin with understanding the condition rather than choosing a procedure first.</p>
      <div class="care-path">
        <article><h3>Understand</h3><p>Symptoms, duration, previous treatment, medical history and relevant triggers are reviewed.</p></article>
        <article><h3>Diagnose</h3><p>Clinical examination is used to identify the likely condition. Investigations may be advised when they can change diagnosis or treatment.</p></article>
        <article><h3>Explain</h3><p>The diagnosis, expected course, alternatives, limitations and relevant aftercare are discussed in clear language.</p></article>
        <article><h3>Plan</h3><p>Treatment is individualised according to the condition, medical history, skin or hair type, priorities and acceptable downtime.</p></article>
        <article><h3>Review</h3><p>When follow-up is needed, response and tolerability are reassessed so the plan can be continued, adjusted or simplified.</p></article>
      </div>
    </section>

    <section class="article-section" aria-labelledby="clinical-focus-heading">
      <h2 id="clinical-focus-heading">Clinical areas of focus</h2>
      <div class="focus-link-grid">
        <a href="/treatments/acne-treatment/"><strong>Acne and acne marks</strong><span>Teenage acne, adult acne, recurring breakouts and post-acne marks</span></a>
        <a href="/treatments/acne-scar-treatment/"><strong>Acne scars</strong><span>Scar-type assessment and individualised combination planning</span></a>
        <a href="/treatments/pigmentation-treatment/"><strong>Pigmentation</strong><span>Melasma, post-inflammatory pigmentation, uneven tone and related concerns</span></a>
        <a href="/treatments/hair-fall-treatment/"><strong>Hair and scalp</strong><span>Hair fall, thinning, alopecia patterns and scalp concerns</span></a>
        <a href="/conditions/"><strong>Medical dermatology</strong><span>Rashes, infections, allergy-related problems and chronic skin conditions</span></a>
        <a href="/treatments/"><strong>Laser and procedural dermatology</strong><span>Selected procedures after assessment of indication, limitations and aftercare</span></a>
      </div>
    </section>

    <section id="what-patients-can-expect" class="article-section" aria-labelledby="consultation-heading">
      <span class="section-kicker">Your consultation</span>
      <h2 id="consultation-heading">What can patients expect during a consultation?</h2>
      <div class="consultation-journey">
        <article class="consultation-step"><div class="consultation-step-number">01</div><div><h3>Tell us what has been happening</h3><p>Your symptoms, duration, previous treatment and relevant medical history are reviewed.</p></div></article>
        <article class="consultation-step"><div class="consultation-step-number">02</div><div><h3>Understand the diagnosis</h3><p>Dr. Cheena Langer explains the likely diagnosis and, where relevant, other conditions that may need to be considered.</p></div></article>
        <article class="consultation-step"><div class="consultation-step-number">03</div><div><h3>Discuss the available options</h3><p>Depending on the diagnosis, management may include medicines, skincare, investigations, procedures, observation or a combination of approaches.</p></div></article>
        <article class="consultation-step"><div class="consultation-step-number">04</div><div><h3>Build a realistic plan</h3><p>The plan considers the medical condition, individual priorities, skin or hair type, tolerability, downtime and expected course.</p></div></article>
        <article class="consultation-step"><div class="consultation-step-number">05</div><div><h3>Review the response</h3><p>Follow-up is advised when needed so progress, side effects and next steps can be reassessed.</p></div></article>
      </div>
    </section>

    <section class="article-section" aria-labelledby="principles-heading">
      <span class="section-kicker">Treatment principles</span>
      <h2 id="principles-heading">Dermatology without unnecessary treatment</h2>
      <div class="principle-grid">
        <article class="principle-card"><strong>No procedure without a clear indication</strong><p>Not every skin or hair concern needs a laser, peel, injectable or other procedure. Treatment should match the diagnosis and the individual patient.</p></article>
        <article class="principle-card"><strong>No identical plan for every patient</strong><p>Similar-looking conditions may have different causes, and the same condition can vary in severity, triggers and response to treatment.</p></article>
        <article class="principle-card"><strong>No unrealistic promises</strong><p>Expected improvement, limitations, downtime, recurrence risk and maintenance are discussed where relevant. Results vary from person to person.</p></article>
      </div>
    </section>

    <section class="article-section" aria-labelledby="professional-heading">
      <span class="section-kicker">Professional profile</span>
      <h2 id="professional-heading">Academic and professional background</h2>
      <p>Alongside clinical practice, Dr. Cheena Langer’s professional work includes postgraduate research, scientific publications, academic presentations, invited teaching and participation in dermatology conferences and professional activities.</p>
      <div class="professional-highlights">
        <div class="professional-highlight"><strong>MBBS, MD Dermatology</strong><span>Medical and specialist dermatology qualifications</span></div>
        <div class="professional-highlight"><strong>20+ years in medicine</strong><span>Clinical experience across medical and procedural care</span></div>
        <div class="professional-highlight"><strong>Research and publications</strong><span>Postgraduate research and scientific publication activity</span></div>
        <div class="professional-highlight"><strong>Academic engagement</strong><span>Scientific presentations, invited faculty activity and conference leadership</span></div>
      </div>
    </section>

    <section class="media-feature" aria-labelledby="clinical-work-heading">
      <figure><img src="/assets/images/professional/doctor-care.svg" alt="" width="760" height="620"></figure>
      <div><span class="section-kicker">In clinic</span><h2 id="clinical-work-heading">Dermatologist-led assessment and treatment</h2><p>Consultations and procedures are planned around diagnosis, medical history, treatment goals and realistic expectations. When a procedure is considered, the indication, alternatives, aftercare and relevant limitations are discussed first.</p></div>
    </section>

    <section class="article-section" aria-labelledby="doctor-note-heading">
      <span class="section-kicker">Approach</span>
      <h2 id="doctor-note-heading">Dr. Cheena Langer’s approach to care</h2>
      <div class="doctor-note"><p>Skin and hair concerns can look deceptively similar. Dr. Cheena Langer’s approach is to establish the likely diagnosis, explain the realistic options clearly and then select a treatment plan that makes sense for the individual patient rather than starting with a fixed package or procedure.</p></div>
    </section>

    <section class="article-section clinic-choice-section" aria-labelledby="clinic-choice-heading">
      <span class="section-kicker">Two locations</span>
      <h2 id="clinic-choice-heading">Choose a clinic in Jammu</h2>
      <div class="clinic-choice-grid">
        <article>
          <figure class="clinic-visual"><img src="/assets/images/professional/clinic-care.svg" alt="" width="720" height="420"></figure>
          <h3>Karan Nagar</h3>
          <address>Lane 2, Karan Nagar, near Amphalla Chowk, Jammu – 180005</address>
          <p><strong>Doctor consultation</strong><br>Mon–Sat 11:00 AM–4:00 PM<br>Sun 11:00 AM–3:00 PM</p>
          <ul class="clinic-meta"><li>Consultation ₹500</li><li>Follow-up within 10 days for the same concern</li></ul>
          <div class="inline-actions"><a href="/locations/karan-nagar/">Clinic details</a><a href="https://maps.app.goo.gl/pHCQ1r4crKuZBSi98" target="_blank" rel="noopener">Directions</a><a href="/book-appointment/">Book here</a></div>
        </article>
        <article>
          <figure class="clinic-visual"><img src="/assets/images/professional/clinic-care.svg" alt="" width="720" height="420"></figure>
          <h3>Paloura Chowk</h3>
          <address>Top Paloura, opposite Government Senior Secondary School, Jammu – 181121</address>
          <p><strong>Doctor consultation</strong><br>Mon–Sat 6:00 PM–8:00 PM<br>Sun 10:30 AM–12:00 PM</p>
          <ul class="clinic-meta"><li>Consultation ₹500</li><li>Follow-up within 10 days for the same concern</li></ul>
          <div class="inline-actions"><a href="/locations/paloura/">Clinic details</a><a href="https://maps.app.goo.gl/kh4AqZoUkscpEgWc8" target="_blank" rel="noopener">Directions</a><a href="/book-appointment/">Book here</a></div>
        </article>
      </div>
    </section>

    <section class="faq-section article-section" aria-labelledby="faq-heading">
      <span class="section-kicker">Common questions</span>
      <h2 id="faq-heading">Frequently asked questions</h2>
      <div class="faq-clean-list">
        <details><summary>Is Dr. Cheena Langer a dermatologist?</summary><div class="faq-answer"><p>Yes. Dr. Cheena Langer is MBBS and MD Dermatology qualified and practises as a Consultant Dermatologist at Aastha Skin &amp; Dermato-Cosmetic Centre in Jammu.</p></div></details>
        <details><summary>How much experience does Dr. Cheena Langer have?</summary><div class="faq-answer"><p>Dr. Cheena Langer has more than 20 years in medicine. Her work includes medical dermatology, hair and scalp disorders, laser dermatology, aesthetic dermatology and selected procedural care.</p></div></details>
        <details><summary>What skin conditions does Dr. Cheena Langer treat?</summary><div class="faq-answer"><p>She evaluates medical skin conditions, acne, pigmentation concerns, infections, allergy-related problems, nail concerns and selected aesthetic or procedural indications. Treatment depends on the diagnosis and individual assessment.</p></div></details>
        <details><summary>Does Dr. Cheena Langer treat acne and acne scars?</summary><div class="faq-answer"><p>Yes. Acne and acne-scar assessment are among her clinical areas of focus. Active acne is usually assessed and controlled before scar-specific procedural planning where appropriate.</p></div></details>
        <details><summary>Does Dr. Cheena Langer treat hair loss?</summary><div class="faq-answer"><p>Yes. Hair fall, thinning and scalp concerns are assessed to identify the likely cause before treatment is selected.</p></div></details>
        <details><summary>Does Dr. Cheena Langer perform laser procedures?</summary><div class="faq-answer"><p>Laser dermatology is part of her professional scope. A laser procedure is recommended only when it is appropriate for the diagnosis, skin type and treatment goal.</p></div></details>
        <details><summary>Where does Dr. Cheena Langer consult in Jammu?</summary><div class="faq-answer"><p>She consults at Aastha Skin &amp; Dermato-Cosmetic Centre in Karan Nagar and at the Paloura Chowk branch in Jammu.</p></div></details>
        <details><summary>How much is a consultation with Dr. Cheena Langer?</summary><div class="faq-answer"><p>The consultation fee is ₹500 at either clinic. One follow-up consultation for the same concern is included within 10 days.</p></div></details>
      </div>
    </section>

    <section class="final-consultation-cta" aria-labelledby="final-cta-heading">
      <div><span class="quiet-label">Next step</span><h2 id="final-cta-heading">Ready to discuss your skin, hair or nail concern?</h2><p>Request a consultation with Dr. Cheena Langer, MBBS, MD Dermatology, at Aastha Skin &amp; Dermato-Cosmetic Centre in Karan Nagar or Paloura Chowk, Jammu.</p><div class="doctor-contact-facts"><span>Consultation ₹500</span><span>One follow-up within 10 days for the same concern</span></div></div>
      <div><div class="hero-actions"><a class="button button-secondary" href="/book-appointment/">Book a consultation</a><a class="button button-secondary" href="https://wa.me/917006613362" target="_blank" rel="noopener">WhatsApp</a></div><a class="plain-link" href="tel:+917006613362">Call 7006613362</a></div>
    </section>

    <p class="medical-disclaimer"><strong>Medical disclaimer:</strong> Results may vary from person to person. This content is for informational purposes only and does not substitute a consultation with a qualified medical professional. Dr. Cheena Langer, MD is a registered medical practitioner.</p>
  </article></div></section>
</main>'''


class Command(BaseCommand):
    help = "Apply the approved v2 Dr. Cheena Langer profile to the production exact layout once."

    def handle(self, *args, **options):
        layout = ExactPageLayout.objects.filter(path=PROFILE_PATH).first()
        if layout is None:
            self.stderr.write("Doctor exact layout not found; no changes applied.")
            return

        page = DoctorPage.objects.filter(slug="dr-cheena-langer").first()
        doctor = Doctor.objects.filter(slug="dr-cheena-langer").first()

        already_current = PROFILE_MARKER in (layout.html or "")
        if not already_current:
            payload = extract_exact_editor_payload(PROFILE_HTML)
            layout.html = PROFILE_HTML
            layout.enabled = True
            layout.editable_text = [("text", value) for value in payload["editable_text"]]
            layout.editable_images = [("image", value) for value in payload["editable_images"]]
            layout.editable_links = [("link", value) for value in payload["editable_links"]]
            layout.save(
                update_fields=[
                    "html",
                    "enabled",
                    "editable_text",
                    "editable_images",
                    "editable_links",
                ]
            )
            self.stdout.write("Updated the Dr. Cheena Langer exact-page layout and editor fields.")
        else:
            self.stdout.write("Dr. Cheena Langer exact-page layout is already v2; content sync skipped.")

        if page is not None:
            changed = False
            desired = {
                "title": "Dr. Cheena Langer – Dermatologist in Jammu",
                "draft_title": "Dr. Cheena Langer – Dermatologist in Jammu",
                "seo_title": SEO_TITLE,
                "search_description": SEO_DESCRIPTION,
                "eyebrow": "Consultant dermatologist",
                "introduction": (
                    "MBBS, MD Dermatology · Consultant Dermatologist at Aastha Skin & "
                    "Dermato-Cosmetic Centre, Jammu, with more than 20 years in medicine."
                ),
                "show_consultation_sidebar": False,
                "show_clinic_choices": False,
            }
            for field, value in desired.items():
                if getattr(page, field, None) != value:
                    setattr(page, field, value)
                    changed = True
            if changed:
                page.save()
                page.save_revision().publish()
                self.stdout.write("Updated and published doctor-page metadata.")

        if doctor is not None:
            short_bio = (
                "MBBS and MD Dermatology qualified Consultant Dermatologist at Aastha "
                "Skin & Dermato-Cosmetic Centre, Jammu, with more than 20 years in medicine."
            )
            if doctor.short_bio != short_bio:
                doctor.short_bio = short_bio
                doctor.save()
                doctor.save_revision().publish()
                self.stdout.write("Updated the reusable doctor profile summary.")

        self.stdout.write(self.style.SUCCESS("Dr. Cheena Langer profile v2 sync complete."))
