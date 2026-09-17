"""Editorial v37 route helpers.

Only explicitly migrated public pages are routed to dedicated editorial
partials. Everything else keeps the existing ExactPageLayout / Wagtail
renderer under the shared v37 skin, which makes the migration incremental and
reversible.
"""

from django import template

register = template.Library()

EDITORIAL_V37_TEMPLATES = {
    "acne-treatment": "home/editorial_v37/treatments/acne-treatment.html",
    "acne-scar-treatment": "home/editorial_v37/treatments/acne-scar-treatment.html",
    "pigmentation-treatment": "home/editorial_v37/treatments/pigmentation-treatment.html",
    "melasma-treatment": "home/editorial_v37/treatments/melasma-treatment.html",
    "fungal-infection-treatment": "home/editorial_v37/treatments/fungal-infection-treatment.html",
    "hair-fall-treatment": "home/editorial_v37/treatments/hair-fall-treatment.html",
    "hair-transplant": "home/editorial_v37/treatments/hair-transplant.html",
    "laser-hair-reduction": "home/editorial_v37/treatments/laser-hair-reduction.html",
    "botulinum-toxin-dermal-fillers": "home/editorial_v37/treatments/botulinum-toxin-dermal-fillers.html",
    "book-appointment": "home/editorial_v37/booking.html",
    "contact": "home/editorial_v37/contact.html",
    "dr-cheena-langer": "home/editorial_v37/doctor.html",
    "karan-nagar": "home/editorial_v37/clinic.html",
    "paloura": "home/editorial_v37/clinic.html",
}


def _guide(
    *,
    kicker,
    headline,
    emphasis,
    lede,
    fallback_image,
    meta,
    section_title,
    section_intro,
    principles,
    assessment,
    logic_title,
    logic_intro,
    steps,
    faqs,
    related_href="",
    related_label="",
):
    return {
        "kicker": kicker,
        "headline": headline,
        "emphasis": emphasis,
        "lede": lede,
        "fallback_image": fallback_image,
        "meta": [{"label": label, "value": value} for label, value in meta],
        "section_title": section_title,
        "section_intro": section_intro,
        "principles": [
            {"label": label, "title": title, "copy": copy}
            for label, title, copy in principles
        ],
        "assessment": assessment,
        "logic_title": logic_title,
        "logic_intro": logic_intro,
        "steps": [
            {"label": label, "title": title, "copy": copy}
            for label, title, copy in steps
        ],
        "faqs": [{"q": question, "a": answer} for question, answer in faqs],
        "related_href": related_href,
        "related_label": related_label,
    }


EDITORIAL_V37_GUIDES = {
    "mnrf-treatment": _guide(
        kicker="MNRF · acne scar and texture care · Jammu",
        headline="Microneedling RF works best when the",
        emphasis="indication is clear.",
        lede="MNRF combines controlled microneedling with radiofrequency energy. It may be considered for selected scar and texture concerns after the skin, scar pattern and downtime expectations are assessed.",
        fallback_image="images/visual-cues/acne-care-512.webp",
        meta=[("Use", "selected scars + texture"), ("Plan", "depth depends on indication"), ("Course", "often staged"), ("Review", "response guides next step")],
        section_title="A device is not the diagnosis.",
        section_intro="The same technology can be used differently depending on what is being treated, skin characteristics and whether active inflammation is still present.",
        principles=[
            ("Scar type", "Morphology matters.", "Rolling, boxcar and mixed scars do not necessarily respond in the same way, and deeper tethering may need a different or combined approach."),
            ("Skin context", "Active acne comes first.", "Ongoing inflammatory acne, irritation or infection can change timing and preparation."),
            ("Downtime", "Plan for recovery.", "Redness, swelling and temporary sensitivity can occur, so aftercare and sun protection matter."),
        ],
        assessment=["Scar type and depth", "Active acne or inflammation", "Skin tone and tendency to pigment after procedures", "Previous scar procedures and response", "Downtime tolerance and treatment priorities", "Current medicines and relevant medical history"],
        logic_title="Build the procedure around the scar pattern.",
        logic_intro="MNRF may sit inside a broader scar plan rather than being the only step.",
        steps=[
            ("Assess", "Map the scar pattern", "Identify rolling, boxcar, ice-pick, mixed scars and any tethering before selecting a procedure."),
            ("Prepare", "Control active disease", "Active acne and significant irritation are generally addressed before scar-focused procedures."),
            ("Treat", "Select settings for the indication", "Needle depth and energy are procedure decisions made after examination, not fixed website presets."),
            ("Review", "Reassess before repeating", "Response, healing and pigmentation risk help decide whether to repeat, combine or change the next step."),
        ],
        faqs=[
            ("Is MNRF suitable for every acne scar?", "No. Scar morphology and depth matter, and some scars may need other or combined procedures."),
            ("Is there downtime?", "Temporary redness, swelling or sensitivity can occur. The expected recovery period varies with the treatment plan."),
            ("Can active acne and scars be treated at the same time?", "Active inflammatory acne is commonly controlled before scar-focused procedural work is prioritised."),
        ],
        related_href="/treatments/acne-scar-treatment/",
        related_label="Explore acne scar planning",
    ),
    "fractional-co2-laser": _guide(
        kicker="Fractional CO₂ laser · resurfacing · Jammu",
        headline="Resurfacing needs a",
        emphasis="reason, not a trend.",
        lede="Fractional CO₂ laser may be considered for selected textural scars and resurfacing concerns. Skin type, scar morphology, pigmentation risk and recovery time all influence planning.",
        fallback_image="images/visual-cues/complete-care-512.webp",
        meta=[("Target", "selected texture + scars"), ("Recovery", "downtime matters"), ("Risk", "pigment change can occur"), ("Plan", "settings are individual")],
        section_title="Resurfacing is not one universal setting.",
        section_intro="The decision is shaped by the concern, skin characteristics and how much recovery is acceptable.",
        principles=[
            ("Indication", "Texture first.", "Fractional CO₂ is considered for selected resurfacing indications rather than every pigmentation or acne concern."),
            ("Skin tone", "Pigment risk matters.", "Post-inflammatory pigmentation risk is part of planning, particularly in darker skin tones."),
            ("Aftercare", "Healing is part of treatment.", "Post-procedure care and sun protection are important parts of the treatment course."),
        ],
        assessment=["Scar or texture pattern", "Skin tone and pigmentation history", "Active acne, infection or irritation", "Previous resurfacing procedures", "Expected downtime", "Sun exposure and ability to follow aftercare"],
        logic_title="Match resurfacing intensity to the indication.",
        logic_intro="A more aggressive treatment is not automatically a better treatment.",
        steps=[
            ("Assess", "Confirm the target", "Different scar types and texture concerns may need different or combined techniques."),
            ("Plan", "Balance benefit and recovery", "Treatment intensity is selected around the indication, skin context and acceptable downtime."),
            ("Recover", "Protect healing skin", "Aftercare focuses on barrier recovery, irritation control and sun protection."),
            ("Review", "Judge the response", "Further treatment is planned only after healing and response are assessed."),
        ],
        faqs=[
            ("Is fractional CO₂ the same as laser toning?", "No. They are different laser approaches used for different indications."),
            ("Can it treat every acne scar?", "No. Scar type changes the strategy and combination treatment may be more appropriate for some patterns."),
            ("Does it have downtime?", "Yes, recovery is expected. The degree and duration vary with the treatment plan."),
        ],
        related_href="/treatments/acne-scar-treatment/",
        related_label="Explore acne scar planning",
    ),
    "chemical-peels": _guide(
        kicker="Chemical peels · skin and pigmentation care · Jammu",
        headline="The peel should match the",
        emphasis="problem and the skin.",
        lede="Chemical peels use selected acids or peeling agents to create controlled exfoliation. The agent, strength and timing depend on the indication, skin sensitivity and pigmentation risk.",
        fallback_image="images/visual-cues/personalised-plan-512.webp",
        meta=[("Use", "selected acne + pigment concerns"), ("Choice", "agent varies by indication"), ("Aftercare", "sun protection matters"), ("Course", "often more than one visit")],
        section_title="There is no single 'best peel'.",
        section_intro="Different peeling agents behave differently, and suitability changes with skin type, current irritation and the condition being treated.",
        principles=[
            ("Indication", "Treat the right target.", "Acne, superficial pigmentation and dullness do not automatically use the same peel."),
            ("Barrier", "Irritated skin changes timing.", "A compromised skin barrier may need to settle before a peel is considered."),
            ("Expectation", "One session is not a promise.", "Improvement may be gradual and maintenance can matter depending on the concern."),
        ],
        assessment=["Primary concern and diagnosis", "Skin sensitivity and current irritation", "History of post-inflammatory pigmentation", "Current skincare and prescription products", "Recent procedures or sun exposure", "Pregnancy or relevant medical considerations"],
        logic_title="Choose the agent after the indication.",
        logic_intro="Peel selection is a clinical decision rather than a fixed menu choice.",
        steps=[
            ("Assess", "Identify the concern", "Confirm whether the target is acne, superficial pigmentation, texture or another issue."),
            ("Prepare", "Review the skin barrier", "Current irritation, skincare and recent procedures can affect timing."),
            ("Treat", "Use a selected peel", "The peel type and exposure are chosen for the individual indication and skin context."),
            ("Maintain", "Protect the result", "Sun protection and an appropriate home routine are important after treatment."),
        ],
        faqs=[
            ("Does a peel always make skin visibly peel?", "Not necessarily. Visible flaking varies with the agent, strength and individual response."),
            ("Can the same peel be used for everyone?", "No. Skin type, sensitivity and indication all matter."),
            ("Is sunscreen important after a peel?", "Yes. Photoprotection is an important part of aftercare."),
        ],
        related_href="/treatments/pigmentation-treatment/",
        related_label="Explore pigmentation care",
    ),
    "q-switched-laser-toning": _guide(
        kicker="Q-switched laser · selected pigment care · Jammu",
        headline="Pigment lasers need a",
        emphasis="specific target.",
        lede="Q-switched laser treatment may be considered for selected pigmentation or tattoo-related indications. Diagnosis, pigment depth, skin tone and recurrence risk matter before treatment is planned.",
        fallback_image="images/visual-cues/complete-care-512.webp",
        meta=[("Target", "selected pigment / tattoo ink"), ("Assessment", "diagnosis first"), ("Skin", "tone affects planning"), ("Course", "sessions vary")],
        section_title="Not every dark patch is a laser problem.",
        section_intro="Melasma, freckles, post-inflammatory pigmentation and tattoo pigment behave differently and should not be treated as one category.",
        principles=[
            ("Diagnosis", "Name the pigment pattern first.", "The cause and depth of pigmentation influence whether a laser belongs in the plan."),
            ("Skin tone", "Parameters matter.", "Skin tone and pigmentation tendency influence treatment selection and aftercare."),
            ("Maintenance", "Triggers can persist.", "Laser does not remove sun, heat, inflammation or hormonal triggers that may continue to affect pigmentation."),
        ],
        assessment=["Pigmentation diagnosis", "Depth and distribution of pigment", "Skin tone and post-inflammatory pigmentation history", "Sun and heat exposure", "Previous laser or peel response", "For tattoos: colour, age, density and body site"],
        logic_title="Use the laser only when the target fits.",
        logic_intro="The device is one possible tool inside a broader pigmentation or tattoo-removal plan.",
        steps=[
            ("Diagnose", "Define the target", "Melasma, freckles, post-inflammatory pigment and tattoo ink are not interchangeable indications."),
            ("Plan", "Select a treatment approach", "Skin characteristics and pigment type influence whether laser, topical care, procedures or a combination is appropriate."),
            ("Treat", "Use selected parameters", "Settings are chosen clinically rather than copied from a universal preset."),
            ("Maintain", "Address recurrence factors", "Photoprotection and trigger control remain important where the underlying condition can recur."),
        ],
        faqs=[
            ("Can Q-switched laser permanently cure melasma?", "Melasma is a chronic relapsing condition. Laser may be considered in selected cases but does not remove the tendency to recur."),
            ("Is it used for tattoo removal?", "Q-switched laser technology is used for selected tattoo pigments, but response varies with colour, ink density, depth, body site and other factors."),
            ("Does every pigmentation problem need laser?", "No. Many pigmentation concerns are managed with photoprotection, topical treatment, procedures or combinations based on the diagnosis."),
        ],
        related_href="/treatments/pigmentation-treatment/",
        related_label="Explore pigmentation planning",
    ),
    "prp-gfc-hair-treatment": _guide(
        kicker="PRP & GFC · supportive hair procedures · Jammu",
        headline="Growth-factor procedures work best inside a",
        emphasis="diagnosis-led hair plan.",
        lede="PRP and GFC are supportive procedures used for selected hair-loss patterns. They do not replace diagnosis, medical treatment or evaluation of nutritional, hormonal and scalp factors when those are relevant.",
        fallback_image="images/visual-cues/hair-scalp-512.webp",
        meta=[("Use", "selected hair-loss patterns"), ("Role", "supportive, not standalone"), ("Course", "sessions may be staged"), ("Review", "response varies")],
        section_title="The injection is not the diagnosis.",
        section_intro="Shedding, patterned thinning, alopecia areata and scarring hair loss are different problems and should not be placed into the same procedural package.",
        principles=[
            ("Pattern", "Identify the hair-loss pattern.", "Patterned thinning and diffuse shedding may need different medical evaluation and treatment."),
            ("Scalp", "Scalp disease can change the plan.", "Dandruff, inflammation, infection or scarring changes timing and priorities."),
            ("Maintenance", "Ongoing causes still matter.", "Medical treatment, nutrition and trigger management may remain important even when a procedure is used."),
        ],
        assessment=["Pattern and duration of hair loss", "Scalp condition", "Family history", "Current medicines and treatment", "Relevant nutritional or hormonal history", "Previous PRP/GFC response"],
        logic_title="Use procedures as part of the plan.",
        logic_intro="A supportive procedure makes more sense when the underlying hair-loss pattern is understood.",
        steps=[
            ("Assess", "Identify the pattern", "History and scalp examination guide whether a growth-factor procedure belongs in the plan."),
            ("Treat causes", "Address relevant contributors", "Medical, scalp, nutritional or hormonal factors are managed where appropriate."),
            ("Support", "Add a selected procedure", "PRP or GFC may be considered as supportive treatment for suitable patterns."),
            ("Review", "Track change over time", "Hair response is gradual, so progress is assessed over an appropriate interval rather than immediately."),
        ],
        faqs=[
            ("Are PRP and GFC cures for all hair loss?", "No. Suitability depends on the diagnosis and some types of hair loss need very different treatment."),
            ("How soon are results visible?", "Hair-cycle change takes time and response varies. Progress is usually judged over months rather than days."),
            ("Do I still need medical treatment?", "Possibly. Procedures may be supportive and do not automatically replace appropriate medical treatment."),
        ],
        related_href="/treatments/hair-fall-treatment/",
        related_label="Explore hair-loss assessment",
    ),
    "laser-tattoo-removal": _guide(
        kicker="Laser tattoo removal · Jammu",
        headline="Tattoo removal is a",
        emphasis="multi-variable process.",
        lede="Laser tattoo removal usually requires multiple sessions. Ink colour, depth, density, tattoo age, body site, skin characteristics and previous treatment can all affect response.",
        fallback_image="images/visual-cues/complete-care-512.webp",
        meta=[("Sessions", "usually multiple"), ("Response", "colour-dependent"), ("Plan", "skin + ink both matter"), ("Risk", "temporary pigment change possible")],
        section_title="Not every tattoo clears at the same rate.",
        section_intro="Professional and amateur tattoos, different pigments and different body sites can behave differently during removal.",
        principles=[
            ("Colour", "Ink colour matters.", "Some pigment colours respond more predictably to certain laser wavelengths than others."),
            ("Depth", "Ink is not all at one depth.", "Density and depth influence how many sessions may be needed."),
            ("Skin", "Healing matters too.", "Skin tone, previous scarring and aftercare are part of treatment planning."),
        ],
        assessment=["Tattoo colour and density", "Professional versus amateur tattoo", "Tattoo age and body site", "Skin tone", "History of scarring or pigment change", "Previous laser treatment"],
        logic_title="Plan around the ink and the skin.",
        logic_intro="A website cannot predict an exact number of sessions from a tattoo photograph alone.",
        steps=[
            ("Assess", "Review the tattoo", "Colour, density, depth clues, body site and skin characteristics are considered."),
            ("Plan", "Choose the laser strategy", "Wavelength and settings are selected for the pigment and skin context."),
            ("Treat", "Allow adequate healing", "Sessions are spaced to allow skin recovery and continued clearance of fragmented pigment."),
            ("Review", "Adjust to response", "Treatment is adapted according to fading, healing and any pigment change."),
        ],
        faqs=[
            ("Can a tattoo be removed in one session?", "Usually not. Multiple sessions are commonly needed."),
            ("Does tattoo colour affect removal?", "Yes. Different pigments absorb different wavelengths and response varies by colour."),
            ("Does laser tattoo removal always scar?", "No, but scarring and pigment change are possible risks. Existing tattoo scarring can also become more visible as ink fades."),
        ],
        related_href="/treatments/q-switched-laser-toning/",
        related_label="Explore Q-switched laser",
    ),
    "eczema-atopic-dermatitis-treatment": _guide(
        kicker="Eczema & atopic dermatitis · medical dermatology · Jammu",
        headline="Eczema care starts with the",
        emphasis="skin barrier and trigger pattern.",
        lede="Atopic dermatitis is a relapsing inflammatory skin condition. Treatment aims to settle inflammation, support the skin barrier, reduce itch and identify relevant triggers or complications.",
        fallback_image="images/visual-cues/rash-infection-512.webp",
        meta=[("Pattern", "itch + inflammation"), ("Course", "can relapse"), ("Foundation", "barrier care"), ("Review", "infection/trigger check")],
        section_title="A flare is more than dry skin.",
        section_intro="Distribution, age, severity, infection, irritants and contact triggers can all alter management.",
        principles=[
            ("Barrier", "Moisturising is foundational.", "Barrier support reduces dryness and can help the skin tolerate treatment and daily exposures."),
            ("Inflammation", "Active eczema needs anti-inflammatory care.", "Prescription treatment may be needed depending on severity and body site."),
            ("Trigger", "Not every flare is an allergy.", "Irritants, climate, sweating, infection and contact allergy may contribute in different people."),
        ],
        assessment=["Distribution and severity", "Itch and sleep disturbance", "Skin-care and soap exposure", "Possible infection", "Occupational or contact triggers", "Previous treatment and steroid use"],
        logic_title="Control the flare, then maintain the barrier.",
        logic_intro="Long-term eczema management often alternates between active treatment and maintenance rather than relying on one permanent cure.",
        steps=[
            ("Assess", "Confirm the pattern", "Other itchy rashes can resemble eczema, so distribution and morphology matter."),
            ("Settle", "Treat active inflammation", "Appropriate anti-inflammatory treatment is selected for severity and body site."),
            ("Support", "Repair and protect the barrier", "Moisturisers, gentle cleansing and trigger reduction support ongoing control."),
            ("Review", "Look for recurrent drivers", "Frequent flares may prompt review of infection, contact allergy, adherence or treatment strategy."),
        ],
        faqs=[
            ("Is eczema contagious?", "No. Atopic dermatitis is not contagious."),
            ("Is every eczema flare caused by food allergy?", "No. Food allergy is not the cause of every eczema flare and unnecessary restriction can be harmful."),
            ("Can eczema come back after improving?", "Yes. Atopic dermatitis can relapse, so maintenance skin care and trigger management are often important."),
        ],
        related_href="/treatments/contact-dermatitis-treatment/",
        related_label="Explore contact dermatitis",
    ),
    "psoriasis-treatment": _guide(
        kicker="Psoriasis · medical dermatology · Jammu",
        headline="Psoriasis needs a",
        emphasis="severity-based plan.",
        lede="Psoriasis is a chronic inflammatory condition that can affect skin, scalp, nails and sometimes joints. Treatment depends on extent, location, symptoms, medical history and impact on daily life.",
        fallback_image="images/visual-cues/rash-infection-512.webp",
        meta=[("Course", "chronic / relapsing"), ("Sites", "skin, scalp, nails"), ("Review", "joint symptoms matter"), ("Plan", "severity-based")],
        section_title="Extent is only one measure of severity.",
        section_intro="Small areas on the face, hands, feet, genitals or scalp can have a large impact, while widespread disease may require systemic assessment.",
        principles=[
            ("Site", "Location changes treatment.", "Scalp, nails and body folds need different formulations and approaches."),
            ("Joints", "Ask about pain and stiffness.", "Joint symptoms may suggest psoriatic arthritis and deserve medical assessment."),
            ("Triggers", "Flares can have context.", "Stress, infection, skin injury and some medicines can influence psoriasis in some people."),
        ],
        assessment=["Extent and body sites", "Scalp and nail involvement", "Joint pain, swelling or morning stiffness", "Previous treatment", "Relevant medical history and medicines", "Impact on sleep, work and daily life"],
        logic_title="Match treatment intensity to disease burden.",
        logic_intro="Topical, phototherapy or systemic options are considered according to severity, location and patient factors.",
        steps=[
            ("Assess", "Map disease burden", "Extent, difficult sites, symptoms and daily-life impact are reviewed."),
            ("Screen", "Ask beyond the skin", "Nails, joints and relevant comorbidities may change management."),
            ("Treat", "Choose an appropriate level of therapy", "Treatment can range from topical care to systemic options depending on the clinical picture."),
            ("Maintain", "Plan for a chronic condition", "Response, safety and recurrence are reviewed over time."),
        ],
        faqs=[
            ("Is psoriasis contagious?", "No. Psoriasis is not contagious."),
            ("Can psoriasis affect joints?", "Yes. Some people with psoriasis develop psoriatic arthritis, so joint pain or stiffness should be mentioned during consultation."),
            ("Can psoriasis be permanently cured?", "Psoriasis is generally a chronic condition. Treatment aims for good control and longer periods with fewer symptoms."),
        ],
        related_href="/conditions/",
        related_label="Browse medical dermatology",
    ),
    "urticaria-hives-treatment": _guide(
        kicker="Urticaria / hives · medical dermatology · Jammu",
        headline="Hives are about the",
        emphasis="pattern over time.",
        lede="Urticaria causes transient raised itchy wheals and sometimes deeper swelling. Duration, recurrence, individual lesion behaviour and associated symptoms help guide assessment.",
        fallback_image="images/visual-cues/rash-infection-512.webp",
        meta=[("Lesions", "transient wheals"), ("Symptom", "itch common"), ("Course", "acute or chronic"), ("Urgency", "airway symptoms = emergency")],
        section_title="A photograph helps, but the timeline matters more.",
        section_intro="Individual hives typically come and go, while chronic urticaria is defined by recurrence over time rather than one persistent spot.",
        principles=[
            ("Timeline", "Track how long each lesion lasts.", "A wheal that stays fixed in one place for an unusually long time may suggest another diagnosis."),
            ("Triggers", "Not all chronic hives are food allergy.", "In many chronic cases no single external allergen is identified."),
            ("Safety", "Breathing symptoms are different.", "Lip/tongue swelling with breathing difficulty, faintness or severe systemic symptoms requires emergency care."),
        ],
        assessment=["How long individual wheals last", "Total duration of the problem", "Angioedema or swelling", "Medicines and recent infections", "Physical triggers", "Any breathing, fainting or systemic symptoms"],
        logic_title="Separate routine hives from red flags.",
        logic_intro="Most urticaria is managed medically, while emergency symptoms need urgent care rather than a routine clinic appointment.",
        steps=[
            ("Describe", "Confirm the lesion behaviour", "Appearance, duration and movement of wheals help distinguish urticaria from other rashes."),
            ("Classify", "Acute or chronic", "Duration of the overall condition influences what evaluation is useful."),
            ("Treat", "Control symptoms", "Antihistamine-based treatment and trigger review are common parts of management, tailored to the case."),
            ("Review", "Escalate when needed", "Persistent or difficult urticaria may need treatment adjustment and targeted investigation."),
        ],
        faqs=[
            ("Are chronic hives always due to food allergy?", "No. Many cases of chronic urticaria do not have a single food trigger."),
            ("Can stress worsen hives?", "Stress can aggravate symptoms in some people, but it is not the only possible factor."),
            ("When are hives an emergency?", "Breathing difficulty, faintness or rapidly progressive tongue/throat swelling requires emergency medical care."),
        ],
        related_href="/treatments/skin-allergy-treatment/",
        related_label="Explore skin allergy care",
    ),
    "alopecia-areata-treatment": _guide(
        kicker="Alopecia areata · hair and scalp · Jammu",
        headline="Smooth patches of hair loss need a",
        emphasis="specific diagnosis.",
        lede="Alopecia areata is an autoimmune form of hair loss that commonly causes smooth patches but can vary in extent. Diagnosis and activity influence treatment planning.",
        fallback_image="images/visual-cues/hair-scalp-512.webp",
        meta=[("Pattern", "smooth patches"), ("Cause", "autoimmune"), ("Course", "unpredictable"), ("Plan", "extent + activity matter")],
        section_title="Not every patch of hair loss is alopecia areata.",
        section_intro="Fungal infection, traction, scarring alopecia and hair-pulling disorders can also create localised loss and need different treatment.",
        principles=[
            ("Scalp", "Look for inflammation or scale.", "A smooth normal-looking patch behaves differently from an inflamed or scarred area."),
            ("Extent", "Small and extensive disease differ.", "Number, size and location of patches influence treatment options."),
            ("Activity", "New patches change the conversation.", "Ongoing spread, nail changes and previous episodes help estimate current disease activity."),
        ],
        assessment=["Number and size of patches", "Scalp appearance", "Eyebrow, eyelash or body-hair involvement", "Nail changes", "Previous episodes and regrowth", "Relevant autoimmune or medical history"],
        logic_title="Confirm the type of patchy loss first.",
        logic_intro="Treatment is selected according to diagnosis, extent, age, activity and previous response.",
        steps=[
            ("Examine", "Confirm the pattern", "Scalp examination helps separate alopecia areata from infection, traction and scarring disorders."),
            ("Assess", "Estimate extent and activity", "New patches, progression and other hair-bearing sites are reviewed."),
            ("Treat", "Choose an appropriate option", "Topical, intralesional or other treatments may be considered depending on the clinical situation."),
            ("Review", "Track regrowth and recurrence", "Response and new activity are reassessed over time."),
        ],
        faqs=[
            ("Is alopecia areata contagious?", "No. Alopecia areata is not contagious."),
            ("Will every patch regrow?", "Regrowth can occur, but the course is unpredictable and recurrence is possible."),
            ("Does every bald patch need PRP?", "No. Patchy hair loss first needs a diagnosis; PRP is not a universal treatment for alopecia areata."),
        ],
        related_href="/treatments/hair-fall-treatment/",
        related_label="Explore hair-loss assessment",
    ),
    "seborrheic-dermatitis-dandruff": _guide(
        kicker="Dandruff & seborrhoeic dermatitis · scalp care · Jammu",
        headline="Flaking is a",
        emphasis="scalp condition, not just dry hair.",
        lede="Dandruff and seborrhoeic dermatitis can cause recurrent flaking, itch and redness on the scalp and other oily areas. Severity and distribution guide treatment.",
        fallback_image="images/visual-cues/hair-scalp-512.webp",
        meta=[("Symptoms", "flakes + itch"), ("Course", "often recurrent"), ("Sites", "scalp + oily areas"), ("Plan", "control, then maintain")],
        section_title="More shampoo is not always the answer.",
        section_intro="Psoriasis, contact dermatitis, fungal infection and other scalp disorders can resemble dandruff, particularly when symptoms are severe or treatment-resistant.",
        principles=[
            ("Pattern", "Look beyond the flakes.", "Redness, thickness of scale and spread beyond the scalp help refine the diagnosis."),
            ("Products", "Irritation can add to the problem.", "Hair oils, dyes and fragranced products may worsen symptoms in some people."),
            ("Maintenance", "Recurrence is common.", "Once controlled, intermittent maintenance treatment may help reduce repeated flares."),
        ],
        assessment=["Flake and itch severity", "Scalp redness or thick scale", "Eyebrow, ear or facial involvement", "Hair products and dye use", "Previous anti-dandruff treatment", "Hair loss or scalp tenderness"],
        logic_title="Control the scalp, then maintain it.",
        logic_intro="Treatment may use antifungal, anti-inflammatory or keratolytic approaches depending on severity and diagnosis.",
        steps=[
            ("Assess", "Confirm the scalp pattern", "Persistent scale is examined to rule out psoriasis, infection and contact dermatitis where relevant."),
            ("Control", "Reduce yeast, scale and inflammation", "Shampoos or prescription treatments are selected according to severity."),
            ("Simplify", "Reduce irritating exposures", "Product triggers are reviewed where symptoms persist."),
            ("Maintain", "Prevent repeated flares", "An intermittent maintenance routine may be advised after symptoms improve."),
        ],
        faqs=[
            ("Is dandruff caused by poor hygiene?", "No. Seborrhoeic dermatitis is not simply a hygiene problem."),
            ("Can dandruff come back?", "Yes. It commonly recurs and may need maintenance care."),
            ("Can every flaky scalp be treated as dandruff?", "No. Psoriasis, dermatitis and infection can look similar, so persistent or severe symptoms deserve assessment."),
        ],
        related_href="/treatments/hair-fall-treatment/",
        related_label="Explore hair and scalp care",
    ),
    "vitiligo-treatment": _guide(
        kicker="Vitiligo · pigment loss · Jammu",
        headline="White patches need the",
        emphasis="right diagnosis first.",
        lede="Vitiligo causes loss of skin pigment, but not every pale or white patch is vitiligo. Distribution, activity and body site affect treatment planning.",
        fallback_image="images/visual-cues/pigmentation-512.webp",
        meta=[("Change", "loss of pigment"), ("Course", "activity varies"), ("Plan", "site + extent matter"), ("Goal", "stabilise + repigment where possible")],
        section_title="White patches have more than one cause.",
        section_intro="Fungal infection, post-inflammatory colour change and other conditions can appear lighter than surrounding skin and need different treatment.",
        principles=[
            ("Activity", "New or spreading patches matter.", "Current disease activity influences treatment priorities and expectations."),
            ("Site", "Body site changes response.", "Face and trunk often behave differently from hands, feet and areas with white hair."),
            ("Context", "Associated history can matter.", "Personal or family autoimmune history may be relevant in selected patients."),
        ],
        assessment=["Distribution and extent", "Recent spread or new patches", "Hair colour within patches", "Previous treatment and response", "Relevant autoimmune history", "Impact on daily life"],
        logic_title="First stabilise active disease, then plan repigmentation.",
        logic_intro="Treatment can involve topical therapy, light-based treatment or other approaches depending on age, site, extent and activity.",
        steps=[
            ("Confirm", "Establish the diagnosis", "Clinical examination distinguishes vitiligo from other causes of light patches."),
            ("Assess", "Determine activity and extent", "Recent spread, body site and hair involvement help shape the plan."),
            ("Treat", "Select an appropriate approach", "Treatment is individualised and may combine medical and light-based options."),
            ("Review", "Track stability and repigmentation", "Progress is assessed over time because pigment recovery is gradual."),
        ],
        faqs=[
            ("Is vitiligo contagious?", "No. Vitiligo is not contagious."),
            ("Are all white patches vitiligo?", "No. Several skin conditions can cause lighter patches."),
            ("Can vitiligo treatment guarantee complete repigmentation?", "No. Response varies with body site, disease activity, duration and other individual factors."),
        ],
        related_href="/conditions/",
        related_label="Browse skin concerns",
    ),
    "hifu-treatment": _guide(
        kicker="HIFU · selected skin-tightening care · Jammu",
        headline="Skin tightening should start with",
        emphasis="anatomy and expectation.",
        lede="HIFU uses focused ultrasound energy at selected tissue depths. It may be considered for appropriate laxity concerns after facial anatomy, skin quality and expectations are assessed.",
        fallback_image="images/visual-cues/skin-ageing-512.webp",
        meta=[("Goal", "selected laxity"), ("Method", "focused ultrasound"), ("Change", "gradual"), ("Suitability", "anatomy-dependent")],
        section_title="Not every ageing concern is a tightening problem.",
        section_intro="Skin texture, pigmentation, volume loss, muscle activity and tissue laxity are different components of facial ageing and need different tools.",
        principles=[
            ("Anatomy", "Treat the right layer.", "Facial structure and tissue distribution influence whether tightening is appropriate."),
            ("Expectation", "Think subtle and gradual.", "Non-surgical tightening should not be presented as equivalent to surgical lifting."),
            ("Combination", "One device does not address everything.", "Texture, pigment, expression lines or volume loss may need different approaches."),
        ],
        assessment=["Primary concern", "Degree and location of laxity", "Skin quality and volume loss", "Previous aesthetic procedures", "Medical history and implanted devices where relevant", "Expectations and desired downtime"],
        logic_title="Use HIFU for a tightening indication, not every ageing sign.",
        logic_intro="The plan depends on whether laxity is truly the dominant concern.",
        steps=[
            ("Assess", "Map the ageing pattern", "Separate laxity from texture, pigment, volume and expression-related concerns."),
            ("Plan", "Select appropriate treatment zones", "Anatomy and tissue distribution guide where treatment is considered."),
            ("Treat", "Use selected ultrasound parameters", "Treatment settings and depth are clinician decisions rather than fixed website presets."),
            ("Review", "Allow time for gradual change", "Collagen remodelling is not immediate, so response is assessed over time."),
        ],
        faqs=[
            ("Is HIFU the same as a surgical facelift?", "No. HIFU is a non-surgical energy-based treatment and should not be expected to reproduce surgical lifting."),
            ("Does HIFU treat pigmentation?", "No. Pigmentation is a different concern and usually needs a separate treatment strategy."),
            ("Is one session guaranteed to be enough?", "No. Suitability, response and any future treatment need to be assessed individually."),
        ],
        related_href="/treatments/hifu-rf-skin-tightening/",
        related_label="Compare tightening approaches",
    ),
    "hydrafacial-medifacial": _guide(
        kicker="Hydrafacial / medifacial · skin-quality care · Jammu",
        headline="A facial should support the",
        emphasis="skin, not fight it.",
        lede="Hydrafacial and medifacial-style procedures are used for selected skin-quality goals such as hydration, superficial congestion and temporary brightness. They do not replace medical treatment for active skin disease.",
        fallback_image="images/visual-cues/skin-ageing-512.webp",
        meta=[("Goal", "skin quality"), ("Role", "supportive"), ("Plan", "skin-state dependent"), ("Aftercare", "gentle routine")],
        section_title="Healthy-looking skin is not one procedure.",
        section_intro="Barrier condition, acne activity, sensitivity and current skincare determine whether an exfoliating or hydrating facial is appropriate.",
        principles=[
            ("Barrier", "Do not over-treat irritated skin.", "Active irritation or dermatitis can make exfoliating procedures a poor choice until the barrier settles."),
            ("Acne", "Medical acne still needs medical care.", "A facial may support skin care but does not replace acne diagnosis or prescription treatment when needed."),
            ("Goal", "Choose the treatment for the goal.", "Hydration, congestion and pigment concerns are not interchangeable targets."),
        ],
        assessment=["Current skin concern", "Sensitivity and barrier condition", "Active acne or dermatitis", "Current prescription products", "Recent peels, lasers or procedures", "Event timing and expectations"],
        logic_title="Match the facial to the current skin state.",
        logic_intro="The safest useful procedure may change from visit to visit as the skin changes.",
        steps=[
            ("Assess", "Check the skin today", "Barrier condition, acne activity and sensitivity are reviewed before choosing a facial."),
            ("Select", "Choose the treatment goal", "Hydration, gentle exfoliation or congestion management are approached differently."),
            ("Treat", "Use a selected protocol", "Products and steps are chosen for the individual skin context."),
            ("Maintain", "Support the result at home", "A consistent routine and sun protection matter more than frequent aggressive procedures."),
        ],
        faqs=[
            ("Can a medifacial cure acne?", "No. Cosmetic facials do not replace diagnosis and medical acne treatment."),
            ("Is stronger exfoliation always better?", "No. Over-exfoliation can irritate the skin barrier."),
            ("Can I combine it with other procedures?", "Timing depends on the other procedure and your skin condition, so combinations should be planned rather than stacked automatically."),
        ],
        related_href="/treatments/chemical-peels/",
        related_label="Explore chemical peels",
    ),
    "wart-mole-skin-tag-removal": _guide(
        kicker="Warts, moles & skin tags · minor procedures · Jammu",
        headline="Identify the lesion before you",
        emphasis="remove it.",
        lede="Warts, skin tags, moles and other growths can look similar to patients but are not the same condition. Examination comes before choosing a removal method.",
        fallback_image="images/visual-cues/dermatologist-diagnosis-512.webp",
        meta=[("First", "identify the lesion"), ("Method", "depends on diagnosis"), ("Reason", "symptoms / irritation / cosmetic"), ("Safety", "changing lesions need assessment")],
        section_title="Removal is not the first diagnostic step.",
        section_intro="A lesion that is changing, bleeding, painful or clinically uncertain should be assessed rather than treated as a routine cosmetic growth.",
        principles=[
            ("Diagnosis", "Wart, tag and mole are different.", "Each has different biology and different removal considerations."),
            ("Change", "New or changing lesions deserve attention.", "Rapid change, bleeding or unusual appearance may change whether removal, biopsy or observation is appropriate."),
            ("Scar", "Every procedure heals.", "Location, lesion size and individual healing tendency affect the expected mark or scar."),
        ],
        assessment=["Clinical diagnosis", "Recent change in size, colour or shape", "Bleeding, pain or recurrent irritation", "Body site", "History of scarring or keloids", "Whether tissue needs histopathology"],
        logic_title="Choose the procedure after the diagnosis.",
        logic_intro="Cautery, cryotherapy, excision or other techniques are selected for the lesion rather than used interchangeably.",
        steps=[
            ("Identify", "Confirm what the growth is", "Clinical assessment comes before removal."),
            ("Safety", "Check for warning features", "Changing or uncertain lesions may require a different pathway, including biopsy."),
            ("Remove", "Select the appropriate technique", "Method depends on diagnosis, size, site and cosmetic considerations."),
            ("Aftercare", "Plan healing and review", "Wound care and follow-up depend on the procedure performed."),
        ],
        faqs=[
            ("Can every mole be removed cosmetically?", "No. Some lesions need diagnostic assessment or biopsy considerations before cosmetic removal is discussed."),
            ("Do all removal methods leave no mark?", "No. Any procedure can leave a temporary or permanent mark, and healing varies by person and body site."),
            ("Are warts and skin tags the same?", "No. Warts are viral growths; skin tags are benign soft growths and follow a different treatment approach."),
        ],
        related_href="/treatments/skin-biopsy/",
        related_label="Explore skin biopsy",
    ),
}


@register.simple_tag
def editorial_v37_template_for(page):
    """Return a v37 include path for an explicitly migrated or data-driven page."""
    slug = getattr(page, "slug", "") or ""
    if slug in EDITORIAL_V37_TEMPLATES:
        return EDITORIAL_V37_TEMPLATES[slug]
    if slug in EDITORIAL_V37_GUIDES:
        return "home/editorial_v37/treatments/clinical-guide.html"
    return ""


@register.simple_tag
def editorial_v37_guide_for(page):
    """Return structured copy for a data-driven clinical guide page."""
    slug = getattr(page, "slug", "") or ""
    return EDITORIAL_V37_GUIDES.get(slug, {})


@register.simple_tag
def editorial_v37_is_native(page):
    """Return whether this page has a self-contained v37 renderer.

    This is intentionally independent from the rollout flag so the base
    template can decide whether legacy premium assets are still required once
    v37 is enabled. Legacy/fallback pages retain the historic stack.
    """
    if page is None:
        return False
    slug = getattr(page, "slug", "") or ""
    model = getattr(getattr(page, "content_type", None), "model", "") or ""
    if model in {"homepage", "contentindexpage"}:
        return True
    return slug in EDITORIAL_V37_TEMPLATES or slug in EDITORIAL_V37_GUIDES
