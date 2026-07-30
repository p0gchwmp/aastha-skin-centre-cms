(() => {
  const body = document.body;
  if (!body || body.dataset.analyticsEnabled !== "true") return;

  const digits = value => String(value || "").replace(/\D/g, "");
  const normaliseBranch = value => {
    const text = String(value || "").trim().toLowerCase();
    if (text.includes("karan") || text.includes("amphalla")) return "karan_nagar";
    if (text.includes("paloura")) return "paloura";
    if (!text || text.includes("no preference")) return "not_selected";
    return "other";
  };

  const inferredBranch = element => {
    const explicit =
      element?.dataset?.clinicBranch ||
      element?.dataset?.branch ||
      element?.dataset?.clinic ||
      element?.closest?.("[data-clinic-branch],[data-branch],[data-clinic]")?.dataset
        ?.clinicBranch ||
      element?.closest?.("[data-clinic-branch],[data-branch],[data-clinic]")?.dataset
        ?.branch ||
      element?.closest?.("[data-clinic-branch],[data-branch],[data-clinic]")?.dataset
        ?.clinic;
    if (explicit) return normaliseBranch(explicit);

    const form = element?.closest?.("form");
    const field = form?.querySelector?.('[name="clinic"], [name="branch"]');
    if (field?.value) return normaliseBranch(field.value);

    const context = [
      element?.textContent,
      element?.getAttribute?.("aria-label"),
      element?.getAttribute?.("title"),
      element?.closest?.("article,section,li,div")?.textContent,
      element?.href
    ].filter(Boolean).join(" ");
    return normaliseBranch(context);
  };

  const track = (name, parameters = {}) => {
    if (typeof window.gtag !== "function") return;
    window.gtag("event", name, {
      page_path: window.location.pathname,
      transport_type: "beacon",
      ...parameters
    });
  };

  window.aasthaTrack = track;

  const linkKind = link => {
    const raw = link.getAttribute("href") || "";
    if (/^tel:/i.test(raw)) return "phone";
    if (/^https?:\/\/(?:wa\.me|(?:api\.)?whatsapp\.com)/i.test(raw)) return "whatsapp";
    if (/^https?:\/\/(?:maps\.app\.goo\.gl|maps\.google\.|www\.google\.[^/]+\/maps)/i.test(raw)) return "map";
    if (/^\/(?:book-appointment|contact)\/?(?:[?#].*)?$/i.test(raw)) return "appointment_cta";
    if (/^https?:\/\/(?:www\.)?(?:instagram\.com|facebook\.com|youtube\.com|youtu\.be|practo\.com|justdial\.com)/i.test(raw)) return "profile";
    return "";
  };

  document.addEventListener("click", event => {
    const link = event.target.closest?.("a[href]");
    if (!link) return;
    const kind = linkKind(link);
    if (!kind) return;

    const rawHref = link.getAttribute("href") || "";
    const branch = inferredBranch(link);
    if (kind === "phone") {
      const number = digits(rawHref);
      const primary = digits(body.dataset.primaryMobile);
      const secondary = digits(body.dataset.secondaryMobile);
      const phoneRole = number.endsWith(primary.slice(-10))
        ? "primary"
        : number.endsWith(secondary.slice(-10))
          ? "secondary"
          : "other";
      track("contact_click", {
        contact_method: "phone",
        phone_role: phoneRole,
        clinic_branch: branch
      });
      return;
    }
    if (kind === "whatsapp") {
      track("contact_click", {
        contact_method: "whatsapp",
        clinic_branch: branch
      });
      return;
    }
    if (kind === "map") {
      track("map_click", { clinic_branch: branch });
      return;
    }
    if (kind === "appointment_cta") {
      track("appointment_cta_click", { clinic_branch: branch });
      return;
    }

    let profileName = "other";
    try {
      const host = new URL(link.href, window.location.href).hostname.replace(/^www\./, "");
      profileName = host.split(".")[0] || "other";
    } catch (_) {
      profileName = "other";
    }
    track("outbound_profile_click", {
      profile_name: profileName,
      clinic_branch: branch
    });
  });

  document.addEventListener("change", event => {
    const field = event.target.closest?.('[name="clinic"], [name="branch"]');
    if (!field) return;
    track("branch_select", {
      clinic_branch: normaliseBranch(field.value)
    });
  });

  document.addEventListener("aastha:appointment-request-opened", event => {
    const detail = event.detail || {};
    track("generate_lead", {
      lead_source: "appointment_form",
      clinic_branch: normaliseBranch(detail.clinic),
      has_preferred_date: Boolean(detail.hasPreferredDate),
      has_preferred_time: Boolean(detail.hasPreferredTime)
    });
  });
})();
