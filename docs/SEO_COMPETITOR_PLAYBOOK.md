# Aastha Skin Centre organic-search playbook

## Purpose

Build the strongest first-party dermatology resource for Jammu: clinically useful,
locally precise, easy to book from, and technically understandable to search
engines. Rankings cannot be guaranteed, and directory-scale tactics should not
be copied blindly.

## Search landscape reviewed

### Local and commercial competitors

- Dr. Nivedita Dadu: deep condition and treatment clusters, cost/session/safety
  sections, frequent publishing and extensive contextual links.
- Practo: city-specialty and city-service pages, structured doctor credentials,
  fees, location intent, appointment actions and patient stories.
- Justdial: very large city/category/locality taxonomies, listings, ratings,
  service combinations and long-tail internal linking.
- Cosmoweave Jammu: strong diagnosis-first local landing pages with doctor
  credentials, location coverage and direct conversion actions.
- Kaya: problem and procedure hubs, consultation-led treatment journeys and
  large service-category coverage.

### Medical publishers and authority sites

- American Academy of Dermatology: resource hubs split into overview, signs,
  causes, diagnosis, treatment, self-care and when to see a dermatologist.
- DermNet: dermatologist authorship/review, references, last-reviewed dates,
  differential diagnosis and extensive related-topic links.
- Cleveland Clinic: consistent templates covering overview, symptoms, causes,
  diagnosis, management, outlook, prevention and questions to ask.
- NHS and Mayo Clinic: plain-language summaries, warning signs, care escalation,
  treatment limits and clear update/review information.

## What Aastha should copy

Copy the useful systems, not the competitors' wording:

1. One definitive page for each real patient intent.
2. Diagnosis before procedure promotion.
3. Clear condition-to-treatment relationships.
4. Visible doctor authorship and medical review.
5. Accurate branch-level location data.
6. Useful answers about suitability, alternatives, safety, recovery and cost
   factors.
7. Strong links between hubs, clinical pages, doctor, locations and booking.
8. Regular updates driven by patient questions and Search Console evidence.

## What Aastha should not copy

- Unsupported “best”, “No. 1”, guaranteed-result or guaranteed-ranking claims.
- Duplicate pages that only change one keyword or locality.
- Fabricated ratings, patient counts, awards, equipment claims or outcomes.
- Thin lists of procedures without diagnostic context.
- Hidden or schema-only FAQs.
- Review incentives or review gating.
- Mass AI content without dermatologist review.

## Technical architecture

### Canonical entity graph

Every public page should consistently connect:

- Organization: Aastha Skin & Dermato-Cosmetic Centre.
- WebSite: the canonical `www` domain.
- MedicalClinic: separate Karan Nagar and Paloura entities.
- Physician/ProfilePage: Dr. Cheena Langer and verified professional profiles.
- BreadcrumbList: hierarchy from Home to hub to page.
- MedicalWebPage plus MedicalCondition or MedicalProcedure on clinical pages.
- BlogPosting on medically reviewed articles.

Branch entities should include only verified address, phone, map/profile URL,
postal code, opening hours and coordinates. Missing data should be omitted rather
than guessed.

### Crawl and indexing controls

- Canonical URLs always use the public `www` origin.
- Apex permanently redirects while preserving path and query.
- Render alias stays available but noindex.
- Internal search results are `noindex,follow`.
- Sitemap includes only canonical, indexable pages.
- Redirects are maintained when slugs change.
- Automated crawlers check titles, descriptions, H1s, canonicals, robots,
  schema, internal links and release parity after deployment.

### CMS safeguards

- Report missing and duplicate titles/descriptions.
- Report missing medical reviewers and review dates.
- Report overdue reviews.
- Track verified third-party profiles separately from page copy.
- Store branch hours and coordinates as structured facts.
- Keep high-risk claims out of global replacements and reusable snippets.

## Information architecture

### Core hubs

- Dermatologist in Jammu
- Conditions
- Treatments
- Acne and acne scars
- Pigmentation and melasma
- Hair and scalp
- Laser procedures
- Minor skin and nail procedures
- Paediatric dermatology
- Doctor profile
- Karan Nagar clinic
- Paloura clinic
- Patient guides / blog

### Relationship rules

Every condition page should link to:

- relevant treatment options;
- related or commonly confused conditions;
- the dermatologist profile;
- both clinic pages where appropriate;
- appointment guidance;
- two to five genuinely useful articles.

Every treatment page should link to:

- conditions it may be used for;
- who may not be suitable;
- alternatives;
- preparation and aftercare;
- doctor and branch pages;
- related procedures without implying that more treatment is always better.

## Standard clinical-page template

1. Direct answer and who the page is for.
2. What the condition/procedure is.
3. Symptoms, patterns or treatment goals.
4. Causes, triggers or suitability factors.
5. How a dermatologist assesses the concern.
6. Treatment options or alternatives.
7. What happens during a procedure, where relevant.
8. Safety, side effects and contraindications.
9. Recovery, aftercare and realistic expectations.
10. Cost factors, not invented fixed prices.
11. When to seek urgent or in-person care.
12. Frequently asked questions visible on the page.
13. Related conditions, treatments and guides.
14. Author, medical reviewer, reviewed date and credible sources.
15. Branch and appointment choices.

## Priority keyword-to-page map

| Search intent | Primary target |
| --- | --- |
| dermatologist in Jammu | Homepage / dedicated dermatologist hub |
| skin specialist in Jammu | Same canonical dermatologist hub |
| lady dermatologist in Jammu | Doctor page or dermatologist hub, without duplication |
| acne treatment in Jammu | Acne treatment page |
| acne scar treatment in Jammu | Acne scar treatment page |
| laser hair reduction in Jammu | Laser hair reduction page |
| hair fall treatment in Jammu | Hair loss diagnostic/treatment page |
| melasma treatment in Jammu | Melasma page |
| pigmentation treatment in Jammu | Pigmentation hub |
| fungal infection treatment in Jammu | Fungal infection page |
| psoriasis treatment in Jammu | Psoriasis page |
| eczema / skin allergy doctor Jammu | Distinct eczema and skin-allergy pages linked through a hub |
| wart, mole, skin tag removal Jammu | Procedure hub plus specific pages when intent differs |
| ingrown toenail treatment Jammu | Ingrown toenail / nail surgery page |
| tattoo removal in Jammu | Tattoo-removal page |
| PRP or GFC hair treatment Jammu | Hair-regeneration treatment page with alternatives |
| dermatologist Karan Nagar | Karan Nagar clinic page |
| dermatologist Paloura | Paloura clinic page |

A second page should not be created when the intent can be answered well on the
same canonical URL.

## Local prominence programme

1. Keep name, address, phone, hours and categories consistent across website,
   Google Business Profile, Practo, Justdial and social profiles.
2. Maintain separate branch identities and map links.
3. Correct incomplete Practo services, photos, clinic hours and education data.
4. Strengthen both Justdial listings, especially Paloura’s thin category/profile
   coverage.
5. Request genuine reviews consistently, with no reward or filtering.
6. Respond professionally to every review, including negative reviews, without
   revealing patient details.
7. Publish real clinic, doctor, equipment and educational media regularly.
8. Earn legitimate citations from medical associations, conferences, hospitals,
   local press, community organisations and professional profiles.

## Publishing programme

Publish from real questions rather than arbitrary volume. Useful clusters include:

- “Is this fungal infection or something else?”
- acne by age, pattern, severity and scarring risk;
- hair fall versus hair shedding, patchy loss and scalp disease;
- melasma versus post-inflammatory pigmentation;
- laser suitability for Indian skin tones;
- procedure preparation and aftercare;
- nail, wart, mole and cyst warning signs;
- seasonal Jammu concerns: heat, humidity, monsoon, winter dryness and gym
  infections.

Clinic videos can become original pages with concise transcripts, key answers,
doctor review and `VideoObject` only when the video is embedded and accurately
described.

## Measurement

Track by page and query, not by vanity ranking screenshots:

- indexed canonical URLs;
- impressions and clicks;
- click-through rate;
- average position distributions;
- non-brand versus brand queries;
- calls, WhatsApp clicks, map clicks and appointment requests;
- branch selection;
- landing-page conversion rate;
- queries with impressions but weak CTR;
- pages losing traffic or overdue for review.

Review monthly. Update pages when evidence shows missing intent, weak snippets,
outdated medical information, poor internal links or low conversion quality.

## Implementation sequence

1. Technical entity and crawl foundation.
2. Verified branch and doctor profiles plus CMS audits.
3. Search Console, GA4 and conversion events.
4. Information architecture and contextual internal links.
5. Priority Jammu landing-page upgrades.
6. Google Business Profile, Practo and Justdial alignment.
7. Medically reviewed publishing and video repurposing.
8. Monthly evidence-led iteration.
