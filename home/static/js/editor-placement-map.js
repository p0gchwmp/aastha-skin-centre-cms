(() => {
  "use strict";

  const pageIdFromPath = () => {
    const match = window.location.pathname.match(/\/pages\/(\d+)\/(?:edit|view_draft|preview)\/?/);
    return match ? match[1] : null;
  };

  const targetInputs = () => Array.from(
    document.querySelectorAll('input[id$="-target_anchor"], input[name$="-target_anchor"]'),
  );

  const setNativeValue = (input, value) => {
    const setter = Object.getOwnPropertyDescriptor(
      window.HTMLInputElement.prototype,
      "value",
    )?.set;
    if (setter) setter.call(input, value);
    else input.value = value;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
  };

  const attachDatalist = (anchors) => {
    let datalist = document.getElementById("aastha-exact-anchor-options");
    if (!datalist) {
      datalist = document.createElement("datalist");
      datalist.id = "aastha-exact-anchor-options";
      document.body.appendChild(datalist);
    }
    datalist.replaceChildren(...anchors.map((anchor) => {
      const option = document.createElement("option");
      option.value = anchor.id;
      option.label = anchor.label;
      return option;
    }));

    targetInputs().forEach((input) => {
      input.setAttribute("list", datalist.id);
      input.setAttribute("autocomplete", "off");
      input.placeholder = anchors.length
        ? "Choose or type an existing section anchor"
        : "No compatible anchors detected; use a fixed placement";
    });
  };

  const appendFixedPlacements = (container, placements) => {
    const strong = document.createElement("strong");
    strong.textContent = "Fixed locations: ";
    container.appendChild(strong);
    placements.forEach((item, index) => {
      if (index) container.appendChild(document.createTextNode(" · "));
      container.appendChild(document.createTextNode(item.label));
    });
  };

  const helperPanel = (data) => {
    const section = document.createElement("section");
    section.className = "aastha-placement-map";
    section.setAttribute("aria-labelledby", "aastha-placement-map-title");

    const title = document.createElement("h3");
    title.id = "aastha-placement-map-title";
    title.textContent = "Exact placement map";
    section.appendChild(title);

    const intro = document.createElement("p");
    intro.textContent = data.has_exact_layout
      ? "Choose a fixed location, or click an existing section below and its anchor will be filled into the next Target anchor field you open."
      : "This page has no active exact layout. Builder sections follow drag-and-drop order; anchor placement is not needed.";
    section.appendChild(intro);

    if (data.has_exact_layout) {
      const fixed = document.createElement("div");
      fixed.className = "aastha-placement-fixed";
      appendFixedPlacements(fixed, data.fixed_placements || []);
      section.appendChild(fixed);

      const heading = document.createElement("h4");
      heading.textContent = "Existing sections available for before/after placement";
      section.appendChild(heading);

      if (data.anchors.length) {
        const list = document.createElement("div");
        list.className = "aastha-anchor-list";
        data.anchors.forEach((anchor) => {
          const button = document.createElement("button");
          button.type = "button";
          button.className = "button button-small button-secondary";
          button.dataset.anchorId = anchor.id;

          const label = document.createElement("span");
          label.textContent = anchor.label;
          const code = document.createElement("code");
          code.textContent = anchor.id;
          button.append(label, code);

          button.addEventListener("click", () => {
            const inputs = targetInputs();
            const active = inputs.find((input) => input === document.activeElement)
              || inputs.find((input) => !input.value)
              || inputs[0];
            if (!active) {
              window.alert("Add or open a section first, then choose Before/After an existing section.");
              return;
            }
            setNativeValue(active, anchor.id);
            active.focus();
          });
          list.appendChild(button);
        });
        section.appendChild(list);
      } else {
        const empty = document.createElement("p");
        empty.className = "help-block help-info";
        empty.textContent = "No compatible article-section anchors were detected. Use After hero, Article end or Page end; content will never be discarded.";
        section.appendChild(empty);
      }
    }

    return section;
  };

  const insertPanel = (panel) => {
    const stream = document.getElementById("id_layout_additions")
      || document.querySelector('[data-contentpath="layout_additions"]')
      || document.querySelector('input[name="layout_mode"]');
    if (!stream || document.querySelector(".aastha-placement-map")) return;
    const container = stream.closest(".w-panel") || stream.parentElement || stream;
    container.parentElement?.insertBefore(panel, container);
  };

  const init = async () => {
    const pageId = pageIdFromPath();
    const template = window.AASTHA_EDITOR_PLACEMENT_URL;
    if (!pageId || !template) return;

    try {
      const response = await fetch(template.replace("__PAGE_ID__", pageId), {
        credentials: "same-origin",
        headers: { Accept: "application/json" },
      });
      if (!response.ok) return;
      const data = await response.json();
      const anchors = Array.isArray(data.anchors) ? data.anchors : [];
      attachDatalist(anchors);
      insertPanel(helperPanel({ ...data, anchors }));

      const observer = new MutationObserver(() => attachDatalist(anchors));
      observer.observe(document.body, { childList: true, subtree: true });
    } catch (error) {
      console.warn("Aastha placement map could not load", error);
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
