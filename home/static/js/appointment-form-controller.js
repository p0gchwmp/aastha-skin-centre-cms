(() => {
  const FORM_SELECTOR = "[data-appointment-form]";

  const digits = value => String(value || "").replace(/\D/g, "");
  const valueFor = (data, ...names) => {
    for (const name of names) {
      const value = String(data.get(name) || "").trim();
      if (value) return value;
    }
    return "";
  };

  const initialiseForm = form => {
    if (form.dataset.appointmentController === "v2") return;
    form.dataset.appointmentController = "v2";

    const mobile = form.querySelector('[name="mobile"]');
    mobile?.addEventListener("input", () => {
      mobile.value = digits(mobile.value).slice(0, 10);
      mobile.setCustomValidity("");
    });

    const date = form.querySelector(
      '[name="date"], [name="preferred_date"], [data-appointment-date]'
    );
    if (date && !date.min) {
      const now = new Date();
      date.min = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
        .toISOString()
        .slice(0, 10);
    }
  };

  document.querySelectorAll(FORM_SELECTOR).forEach(initialiseForm);

  // This capture-phase listener is the single owner of appointment submission.
  // Older page bundles contain two bubble-phase handlers; stopping propagation
  // here prevents duplicate WhatsApp tabs and inconsistent field mappings.
  document.addEventListener(
    "submit",
    event => {
      const form = event.target.closest?.(FORM_SELECTOR);
      if (!form) return;

      event.preventDefault();
      event.stopImmediatePropagation();
      initialiseForm(form);

      if (!form.reportValidity()) return;

      const data = new FormData(form);
      const mobileInput = form.querySelector('[name="mobile"]');
      const mobile = digits(valueFor(data, "mobile")).slice(0, 10);
      if (!/^\d{10}$/.test(mobile)) {
        mobileInput?.setCustomValidity("Enter a valid 10-digit mobile number.");
        mobileInput?.reportValidity();
        mobileInput?.focus();
        return;
      }

      const name = valueFor(data, "name");
      const clinic = valueFor(data, "clinic", "branch") || "No preference";
      const date = valueFor(data, "date", "preferred_date");
      const time = valueFor(data, "time", "preferred_time");
      const concern = valueFor(data, "concern");
      const patientType = valueFor(data, "patient_type");
      const opd = valueFor(data, "opd", "opd_number", "patient_number");
      const age = valueFor(data, "age");
      const gender = valueFor(data, "gender");
      const note = valueFor(data, "message", "notes");

      const lines = [
        "Appointment request — Aastha Skin Centre",
        `Name: ${name}`,
        `Mobile: ${mobile}`,
        age ? `Age: ${age}` : "",
        gender ? `Gender: ${gender}` : "",
        `Clinic: ${clinic}`,
        concern ? `Concern: ${concern}` : "",
        patientType ? `Patient type: ${patientType}` : "",
        opd ? `OPD / patient number: ${opd}` : "",
        date ? `Preferred date: ${date}` : "",
        `Preferred time: ${time || "Any available time"}`,
        note ? `Message: ${note}` : "",
        "",
        document.body?.dataset.appointmentConfirmationText ||
          "Submitting this form requests an appointment. It is confirmed only after the clinic contacts you."
      ].filter(line => line !== "");

      const configuredUrl = document.body?.dataset.whatsappUrl || "";
      const whatsappNumber = digits(
        document.body?.dataset.whatsappMobile || "7006613362"
      ).slice(-10);
      const whatsappUrl = configuredUrl || `https://wa.me/91${whatsappNumber}`;
      window.open(
        `${whatsappUrl}?text=${encodeURIComponent(lines.join("\n"))}`,
        "_blank",
        "noopener,noreferrer"
      );

      const status = form.querySelector("[data-form-status]");
      if (status) {
        status.hidden = false;
        status.textContent =
          "WhatsApp has opened with your appointment request. Send the message to complete your request; the clinic will confirm availability.";
      }
    },
    true
  );
})();