(() => {
  const whatsappUrl = document.body.dataset.whatsappUrl || "";
  const clinicName =
    document.body.dataset.clinicShortName || "Aastha Skin Centre";

  const setupGlobalLogo = () => {
    const logoUrl = document.body.dataset.logoUrl || "";
    if (!logoUrl) return;

    const logoWidth = Number(document.body.dataset.logoWidth || 0);
    const logoHeight = Number(document.body.dataset.logoHeight || 0);
    const logoLargeUrl = document.body.dataset.logoLargeUrl || "";
    const logoLargeWidth = Number(document.body.dataset.logoLargeWidth || 0);

    const responsiveCandidates = [
      [logoUrl, logoWidth],
      [logoLargeUrl, logoLargeWidth],
    ].filter(
      ([url, width], index, values) =>
        url &&
        width > 0 &&
        values.findIndex(([candidateUrl]) => candidateUrl === url) === index,
    );

    const applyLogo = (root) => {
      const marks = [...root.querySelectorAll(".brand-mark")].filter(
        (mark) => mark.dataset.globalLogoApplied !== "true",
      );
      if (!marks.length) return false;

      marks.forEach((mark) => {
        const fallback = (mark.textContent || "A").trim() || "A";
        const image = new Image();
        image.src = logoUrl;
        if (responsiveCandidates.length > 1) {
          image.srcset = responsiveCandidates
            .map(([url, width]) => `${url} ${width}w`)
            .join(", ");
          image.sizes = root.matches("[data-site-footer]")
            ? "150px"
            : "(max-width: 700px) 105px, 150px";
        }
        image.alt = "";
        image.decoding = "async";
        image.loading = root.matches("[data-site-footer]") ? "lazy" : "eager";
        if (!image.loading || image.loading === "eager") {
          image.fetchPriority = "high";
        }
        if (logoWidth > 0) image.width = logoWidth;
        if (logoHeight > 0) image.height = logoHeight;

        image.addEventListener(
          "error",
          () => {
            mark.classList.remove("brand-mark--image");
            mark.removeAttribute("data-global-logo-applied");
            mark.textContent = fallback;
          },
          { once: true },
        );

        mark.dataset.globalLogoApplied = "true";
        mark.classList.add("brand-mark--image");
        mark.replaceChildren(image);
      });
      return true;
    };

    document
      .querySelectorAll("[data-site-header], [data-site-footer]")
      .forEach((root) => {
        if (applyLogo(root)) return;

        // site.js hydrates the shared header and footer asynchronously after it
        // loads the legacy JSON config. Observe each mount point so the current
        // Wagtail logo is applied regardless of network timing.
        const observer = new MutationObserver(() => {
          if (applyLogo(root)) observer.disconnect();
        });
        observer.observe(root, { childList: true, subtree: true });
      });
  };

  setupGlobalLogo();

  const openWhatsApp = (lines) => {
    if (!whatsappUrl) return;
    const separator = whatsappUrl.includes("?") ? "&" : "?";
    const message = lines.filter(Boolean).join("\n");
    window.open(
      `${whatsappUrl}${separator}text=${encodeURIComponent(message)}`,
      "_blank",
      "noopener,noreferrer",
    );
  };

  const restrictToTenDigits = (input) => {
    if (!input) return;
    input.addEventListener("input", () => {
      input.value = input.value.replace(/\D/g, "").slice(0, 10);
      input.setCustomValidity("");
    });
  };

  const menuButton = document.querySelector(".cms-menu-toggle");
  const navigation = document.querySelector(".cms-navigation");
  if (menuButton && navigation) {
    menuButton.addEventListener("click", () => {
      const open = navigation.classList.toggle("is-open");
      menuButton.setAttribute("aria-expanded", String(open));
    });
  }

  document.querySelectorAll(".cms-theme-toggle").forEach((button) => {
    button.addEventListener("click", () => {
      const next =
        document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      document.documentElement.dataset.theme = next;
      localStorage.setItem("aastha-theme", next);
    });
  });

  document.querySelectorAll("[data-carousel]").forEach((carousel) => {
    const slides = [...carousel.querySelectorAll(".cms-carousel-slide")];
    if (slides.length < 2) return;
    const status = carousel.querySelector("[data-carousel-status]");
    const previous = carousel.querySelector("[data-carousel-prev]");
    const next = carousel.querySelector("[data-carousel-next]");
    let current = 0;
    let timer;

    const show = (index) => {
      current = (index + slides.length) % slides.length;
      slides.forEach((slide, slideIndex) => {
        slide.hidden = slideIndex !== current;
      });
      if (status) status.textContent = `${current + 1} / ${slides.length}`;
    };

    const stop = () => {
      if (timer) window.clearInterval(timer);
    };

    const start = () => {
      stop();
      if (carousel.dataset.autoplay !== "true") return;
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
      const seconds = Number(carousel.dataset.interval || 6);
      timer = window.setInterval(() => show(current + 1), seconds * 1000);
    };

    previous?.addEventListener("click", () => {
      show(current - 1);
      start();
    });
    next?.addEventListener("click", () => {
      show(current + 1);
      start();
    });
    carousel.addEventListener("mouseenter", stop);
    carousel.addEventListener("mouseleave", start);
    carousel.addEventListener("focusin", stop);
    carousel.addEventListener("focusout", start);
    start();
  });

  // Keep long FAQ groups tidy while preserving normal browser accessibility.
  document.querySelectorAll(".faq-clean-list").forEach((list) => {
    list.querySelectorAll("details").forEach((item) => {
      item.addEventListener("toggle", () => {
        if (!item.open) return;
        list.querySelectorAll("details[open]").forEach((other) => {
          if (other !== item) other.open = false;
        });
      });
    });
  });

  // Appointment requests deliberately continue in WhatsApp. The destination is
  // read from the global CMS setting, never duplicated in page content or code.
  const appointmentForm = document.querySelector("[data-appointment-form]");
  if (appointmentForm) {
    const mobile = appointmentForm.querySelector('[name="mobile"]');
    const date = appointmentForm.querySelector("[data-appointment-date]");
    const patientType = appointmentForm.querySelector("[data-patient-type]");
    const opdField = appointmentForm.querySelector("[data-opd-field]");
    restrictToTenDigits(mobile);

    if (date) {
      const now = new Date();
      date.min = new Date(
        now.getTime() - now.getTimezoneOffset() * 60000,
      )
        .toISOString()
        .slice(0, 10);
    }

    const updatePatientType = () => {
      if (!patientType || !opdField) return;
      opdField.hidden = patientType.value !== "Existing patient";
    };
    patientType?.addEventListener("change", updatePatientType);
    updatePatientType();

    appointmentForm.addEventListener("submit", (event) => {
      event.preventDefault();
      if (!appointmentForm.reportValidity()) return;
      if (!/^\d{10}$/.test(mobile?.value || "")) {
        mobile?.setCustomValidity("Enter a valid 10-digit mobile number.");
        mobile?.reportValidity();
        return;
      }

      const data = new FormData(appointmentForm);
      openWhatsApp([
        `Appointment request - ${clinicName}`,
        `Name: ${data.get("name") || ""}`,
        `Mobile: ${data.get("mobile") || ""}`,
        data.get("age") ? `Age: ${data.get("age")}` : "",
        data.get("gender") ? `Gender: ${data.get("gender")}` : "",
        `Clinic: ${data.get("clinic") || "No preference"}`,
        `Concern: ${data.get("concern") || ""}`,
        `Patient type: ${data.get("patient_type") || ""}`,
        data.get("opd")
          ? `OPD / patient number: ${data.get("opd")}`
          : "",
        data.get("date") ? `Preferred date: ${data.get("date")}` : "",
        `Preferred time: ${data.get("time") || "Any available time"}`,
        data.get("message") ? `Message: ${data.get("message")}` : "",
      ]);
    });
  }

  // Contact forms use the same global destination and validation.
  document.querySelectorAll("[data-premium-contact-form]").forEach((form) => {
    const mobile = form.querySelector('[name="mobile"]');
    restrictToTenDigits(mobile);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      if (mobile && !/^\d{10}$/.test(mobile.value)) {
        mobile.setCustomValidity("Enter a valid 10-digit mobile number.");
        mobile.reportValidity();
        return;
      }
      const data = new FormData(form);
      openWhatsApp([
        `Clinic enquiry - ${clinicName}`,
        `Name: ${data.get("name") || ""}`,
        `Mobile: ${data.get("mobile") || ""}`,
        `Clinic: ${data.get("clinic") || "No preference"}`,
        `Reason: ${data.get("reason") || ""}`,
        data.get("message") ? `Message: ${data.get("message")}` : "",
      ]);
    });
  });

  // Normalise legacy relative links and secure all new-tab links.
  document.querySelectorAll("a[href]").forEach((link) => {
    const href = link.getAttribute("href");
    if (["/blog", "blog", "blog/", "./blog/"].includes(href)) {
      link.setAttribute("href", "/blog/");
    }
    if (link.target === "_blank") {
      const rel = new Set(
        (link.rel || "").split(/\s+/).filter(Boolean),
      );
      rel.add("noopener");
      rel.add("noreferrer");
      link.rel = [...rel].join(" ");
    }
  });
})();
