import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { fileURLToPath } from "node:url";

const frontendRoot = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: path.resolve(frontendRoot, "../home/static/ui"),
    emptyOutDir: true,
    sourcemap: false,
    cssCodeSplit: false,
    rollupOptions: {
      input: {
        "motion-runtime": path.resolve(frontendRoot, "src/motion-runtime.js"),
        "kokonut-explore": path.resolve(frontendRoot, "src/kokonut-explore.jsx"),
        "bklit-insights": path.resolve(frontendRoot, "src/bklit-insights.jsx"),
      },
      output: {
        entryFileNames: "[name].js",
        chunkFileNames: "chunks/[name]-[hash].js",
        assetFileNames: "assets/[name]-[hash][extname]",
      },
    },
  },
});
