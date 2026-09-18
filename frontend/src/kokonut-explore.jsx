/**
 * Aastha route search island.
 * Interaction model adapted from Kokonut UI Action Search Bar (MIT):
 * https://github.com/kokonut-labs/kokonutui
 * Styling is Aastha-specific; patient routes/data remain server-owned.
 */
import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { ArrowUpRight, Search, X } from "lucide-react";

const ROUTES = [
  ["Start here","Concerns","Browse by symptom or concern","/conditions/"],
  ["Start here","Find your route","Choose area + concern","/#v37-finder"],
  ["Start here","Treatments","Full treatment directory","/treatments/"],
  ["Start here","Book consultation","Request an appointment","/book-appointment/"],
  ["Common guides","Acne","Breakouts, marks and active acne","/treatments/acne-treatment/"],
  ["Common guides","Acne scars","Scar-type planning and resurfacing","/treatments/acne-scar-treatment/"],
  ["Common guides","Pigmentation","Melasma, marks and uneven tone","/treatments/pigmentation-treatment/"],
  ["Common guides","Melasma","Triggers, maintenance and treatment","/treatments/melasma-treatment/"],
  ["Common guides","Hair fall","Shedding, thinning and scalp assessment","/treatments/hair-fall-treatment/"],
  ["Common guides","Hair transplant","Donor planning and suitability","/treatments/hair-transplant/"],
  ["Common guides","Fungal infection","Ringworm, recurrence and steroid-modified tinea","/treatments/fungal-infection-treatment/"],
  ["Common guides","Laser hair reduction","Hair, skin type and session planning","/treatments/laser-hair-reduction/"],
  ["Clinic","Dr. Cheena Langer","Consultant dermatologist","/dr-cheena-langer/"],
  ["Clinic","Karan Nagar","Clinic details, timings and directions","/locations/karan-nagar/"],
  ["Clinic","Paloura","Clinic details, timings and directions","/locations/paloura/"],
  ["Learn","Journal","Dermatology articles and patient education","/blog/"],
  ["Clinic","Contact","Phone, WhatsApp and clinic information","/contact/"],
].map(([group,label,note,href], id) => ({ id, group, label, note, href }));

let exposeApi = null;

function Explore() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);
  const inputRef = useRef(null);
  const panelRef = useRef(null);
  const previousFocus = useRef(null);
  const reducedMotion = useReducedMotion();

  const matches = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return ROUTES;
    return ROUTES.filter((route) =>
      `${route.group} ${route.label} ${route.note}`.toLowerCase().includes(q)
    );
  }, [query]);

  useEffect(() => setActive(0), [query]);

  useEffect(() => {
    exposeApi = {
      open() {
        previousFocus.current = document.activeElement;
        setOpen(true);
      },
      close() {
        setOpen(false);
      },
    };
    window.AasthaKokonutExplore = exposeApi;
    window.dispatchEvent(new CustomEvent("aastha:kokonut-ready"));
    return () => {
      if (window.AasthaKokonutExplore === exposeApi) delete window.AasthaKokonutExplore;
    };
  }, []);

  useEffect(() => {
    if (!open) {
      document.body.classList.remove("v37-kokonut-open");
      previousFocus.current?.focus?.();
      return;
    }

    document.body.classList.add("v37-kokonut-open");
    const timer = window.setTimeout(() => inputRef.current?.focus(), reducedMotion ? 0 : 40);

    const onDialogKeyDown = (event) => {
      if (event.key === "Escape") {
        event.preventDefault();
        setOpen(false);
        return;
      }
      if (event.key !== "Tab") return;

      const panel = panelRef.current;
      if (!panel) return;
      const focusable = [...panel.querySelectorAll(
        'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
      )].filter((element) => !element.hidden && element.getAttribute("aria-hidden") !== "true");

      if (!focusable.length) {
        event.preventDefault();
        panel.focus();
        return;
      }

      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener("keydown", onDialogKeyDown);
    return () => {
      window.clearTimeout(timer);
      document.removeEventListener("keydown", onDialogKeyDown);
    };
  }, [open, reducedMotion]);

  const choose = (route) => {
    if (!route) return;
    window.location.assign(route.href);
  };

  const onKeyDown = (event) => {
    if (!matches.length) return;
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActive((value) => (value + 1) % matches.length);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActive((value) => (value - 1 + matches.length) % matches.length);
    } else if (event.key === "Enter") {
      event.preventDefault();
      choose(matches[active]);
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="kokonut-explore"
          initial={reducedMotion ? false : { opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={reducedMotion ? { opacity: 1 } : { opacity: 0 }}
          transition={{ duration: reducedMotion ? 0 : 0.18 }}
        >
          <button
            className="kokonut-explore__backdrop"
            type="button"
            aria-label="Close Explore"
            onClick={() => setOpen(false)}
          />
          <motion.section
            ref={panelRef}
            className="kokonut-explore__panel"
            role="dialog"
            aria-modal="true"
            aria-labelledby="kokonut-explore-title"
            tabIndex={-1}
            initial={reducedMotion ? false : { opacity: 0, y: 24, scale: 0.99 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={reducedMotion ? { opacity: 1, y: 0, scale: 1 } : { opacity: 0, y: 14, scale: 0.995 }}
            transition={reducedMotion ? { duration: 0 } : { type: "spring", stiffness: 330, damping: 31, mass: 0.78 }}
          >
            <header className="kokonut-explore__head">
              <div>
                <span>AASTHA · JAMMU</span>
                <h2 id="kokonut-explore-title">Where do you want to go?</h2>
              </div>
              <button type="button" onClick={() => setOpen(false)} aria-label="Close Explore">
                <X size={18} />
              </button>
            </header>

            <label className="kokonut-explore__search">
              <Search size={18} aria-hidden="true" />
              <input
                ref={inputRef}
                type="search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                onKeyDown={onKeyDown}
                placeholder="Search acne, pigmentation, hair, doctor, clinics…"
                autoComplete="off"
                role="combobox"
                aria-expanded="true"
                aria-controls="kokonut-route-results"
                aria-autocomplete="list"
                aria-activedescendant={matches.length ? `kokonut-route-option-${matches[active]?.id}` : undefined}
              />
              <kbd>⌘K</kbd>
            </label>

            <motion.div
              className="kokonut-explore__results"
              id="kokonut-route-results"
              role="listbox"
              layout
            >
              <AnimatePresence mode="popLayout">
                {matches.length ? matches.map((route, index) => (
                  <motion.button
                    type="button"
                    id={`kokonut-route-option-${route.id}`}
                    key={route.href}
                    className={index === active ? "is-active" : ""}
                    role="option"
                    aria-selected={index === active}
                    onMouseEnter={() => setActive(index)}
                    onFocus={() => setActive(index)}
                    onClick={() => choose(route)}
                    layout={!reducedMotion}
                    initial={reducedMotion ? false : { opacity: 0, y: 7 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={reducedMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: -5 }}
                    transition={{ duration: reducedMotion ? 0 : 0.18, delay: reducedMotion ? 0 : Math.min(index * 0.018, 0.12) }}
                  >
                    <span className="kokonut-explore__group">{route.group}</span>
                    <strong>{route.label}</strong>
                    <small>{route.note}</small>
                    <ArrowUpRight size={17} aria-hidden="true" />
                  </motion.button>
                )) : (
                  <motion.p
                    className="kokonut-explore__empty"
                    initial={reducedMotion ? false : { opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: reducedMotion ? 0 : 0.18 }}
                  >
                    No matching route. Try a broader word.
                  </motion.p>
                )}
              </AnimatePresence>
            </motion.div>
            <footer>↑ ↓ navigate <span>·</span> Enter open <span>·</span> Esc close</footer>
          </motion.section>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

const host = document.createElement("div");
host.id = "aastha-kokonut-island";
document.body.appendChild(host);
createRoot(host).render(<Explore />);
