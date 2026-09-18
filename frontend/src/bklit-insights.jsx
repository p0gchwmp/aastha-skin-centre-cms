/**
 * Staff-only CMS data visualization.
 * Ring composition is adapted from Bklit UI's MIT ring chart source:
 * https://github.com/bklit/bklit-ui
 * This intentionally visualizes only real server-provided CMS inventory.
 */
import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { arc as arcGenerator } from "@visx/shape";
import { motion } from "motion/react";

const TAU = Math.PI * 2;

function arcPath(innerRadius, outerRadius, startAngle, endAngle) {
  const generator = arcGenerator({
    innerRadius,
    outerRadius,
    cornerRadius: Math.max(2, (outerRadius - innerRadius) / 2),
  });
  return generator({ startAngle, endAngle }) || "";
}

function ClinicalMix({ treatments, conditions, blogs }) {
  const data = useMemo(() => [
    { label: "Treatments", value: treatments },
    { label: "Conditions", value: conditions },
    { label: "Journal", value: blogs },
  ], [treatments, conditions, blogs]);
  const total = Math.max(1, data.reduce((sum, item) => sum + item.value, 0));
  const [hovered, setHovered] = useState(null);
  const size = 300;
  const center = size / 2;
  const stroke = 16;
  const gap = 9;
  const base = 58;

  return (
    <div className="bklit-clinical-mix">
      <div className="bklit-ring-wrap">
        <svg viewBox={`0 0 ${size} ${size}`} role="img" aria-label="Clinical content mix">
          <g transform={`translate(${center} ${center})`}>
            {data.map((item, index) => {
              const inner = base + index * (stroke + gap);
              const outer = inner + stroke;
              const end = -Math.PI / 2 + TAU * (item.value / total);
              const bg = arcPath(inner, outer, -Math.PI / 2, 3 * Math.PI / 2);
              const fg = arcPath(inner, outer, -Math.PI / 2, end);
              const dim = hovered !== null && hovered !== index;
              return (
                <motion.g
                  key={item.label}
                  onPointerEnter={() => setHovered(index)}
                  onPointerLeave={() => setHovered(null)}
                  animate={{ opacity: dim ? 0.28 : 1, scale: hovered === index ? 1.025 : 1 }}
                  transition={{ type: "spring", stiffness: 420, damping: 28 }}
                  style={{ transformOrigin: "0 0", cursor: "default" }}
                >
                  <path d={bg} className="bklit-ring-bg" />
                  <motion.path
                    d={fg}
                    className={`bklit-ring-fg bklit-ring-fg--${index + 1}`}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.12 + index * 0.09, duration: 0.35 }}
                  />
                </motion.g>
              );
            })}
          </g>
        </svg>
        <div className="bklit-ring-center">
          <strong>{hovered === null ? total : data[hovered].value}</strong>
          <span>{hovered === null ? "published guides" : data[hovered].label}</span>
        </div>
      </div>
      <div className="bklit-legend">
        {data.map((item, index) => (
          <button
            type="button"
            key={item.label}
            onPointerEnter={() => setHovered(index)}
            onPointerLeave={() => setHovered(null)}
            onFocus={() => setHovered(index)}
            onBlur={() => setHovered(null)}
          >
            <i className={`bklit-dot bklit-dot--${index + 1}`} />
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </button>
        ))}
      </div>
    </div>
  );
}

document.querySelectorAll("[data-bklit-clinical-mix]").forEach((host) => {
  const number = (key) => Number.parseInt(host.dataset[key] || "0", 10) || 0;
  createRoot(host).render(
    <ClinicalMix
      treatments={number("treatments")}
      conditions={number("conditions")}
      blogs={number("blogs")}
    />
  );
});
