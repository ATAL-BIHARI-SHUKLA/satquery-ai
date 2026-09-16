import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const components = [
  "Navbar",
  "Hero",
  "ImageUploader",
  "QueryBox",
  "HowItWorks",
  "Capabilities",
  "UseCases",
  "CTA",
  "Footer",
];

components.forEach((name) => {
  fs.writeFileSync(
    path.join(__dirname, "src", "components", `${name}.jsx`),
    `export default function ${name}() {\n  return (\n    <div>${name} Component</div>\n  );\n}\n`,
  );
});

fs.writeFileSync(
  path.join(__dirname, "src", "pages", "Home.jsx"),
  `import Navbar from '../components/Navbar';\nimport Hero from '../components/Hero';\nimport ImageUploader from '../components/ImageUploader';\nimport QueryBox from '../components/QueryBox';\nimport HowItWorks from '../components/HowItWorks';\nimport Capabilities from '../components/Capabilities';\nimport UseCases from '../components/UseCases';\nimport CTA from '../components/CTA';\nimport Footer from '../components/Footer';\n\nexport default function Home() {\n  return (\n    <div>\n      <Navbar />\n      <Hero />\n      <ImageUploader />\n      <QueryBox />\n      <HowItWorks />\n      <Capabilities />\n      <UseCases />\n      <CTA />\n      <Footer />\n    </div>\n  );\n}\n`,
);

fs.writeFileSync(
  path.join(__dirname, "src", "services", "api.js"),
  `export const api = {};\n`,
);
fs.writeFileSync(
  path.join(__dirname, "src", "hooks", "useImageUpload.js"),
  `export function useImageUpload() {\n  return {};\n}\n`,
);
fs.writeFileSync(
  path.join(__dirname, "src", "utils", "fileValidation.js"),
  `export function validateFile(file) {\n  return true;\n}\n`,
);

fs.writeFileSync(
  path.join(__dirname, "src", "App.jsx"),
  `import Home from './pages/Home';\n\nfunction App() {\n  return (\n    <Home />\n  );\n}\n\nexport default App;\n`,
);

fs.writeFileSync(
  path.join(__dirname, "src", "index.css"),
  `@import "tailwindcss";\n\n@theme {\n  --color-primary: #3b82f6;\n}\n`,
);

fs.writeFileSync(
  path.join(__dirname, "vite.config.js"),
  `import { defineConfig } from 'vite'\nimport react from '@vitejs/plugin-react'\nimport tailwindcss from '@tailwindcss/vite'\n\n// https://vite.dev/config/\nexport default defineConfig({\n  plugins: [\n    react(),\n    tailwindcss(),\n  ],\n})\n`,
);

fs.writeFileSync(
  path.join(__dirname, "public", "favicon.svg"),
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="#3b82f6"/></svg>\n`,
);
