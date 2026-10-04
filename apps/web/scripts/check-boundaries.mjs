import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const scanRoots = ["src", "tests", "scripts"];
const sourceExtensions = new Set([".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"]);
const forbiddenImports = [
  "@supabase", "supabase", "prisma", "@prisma", "drizzle", "postgres", "@neondatabase",
  "auth0", "next-auth", "@auth/", "@clerk/", "firebase", "@aws-sdk/", "aws-sdk",
  "@google-cloud/", "@azure/",
];
const sqlPattern = /\b(?:SELECT|INSERT|UPDATE)\b|\bDELETE\s+FROM\b/i;
const importPattern = /(?:from\s+|import\s*\()(["'`])([^"'`]+)\1/g;
const errors = [];

function filesUnder(relative) {
  const start = path.join(root, relative);
  if (!fs.existsSync(start)) return [];
  const out = [];
  for (const entry of fs.readdirSync(start, { withFileTypes: true })) {
    const full = path.join(start, entry.name);
    if (entry.isDirectory()) out.push(...filesUnder(path.relative(root, full)));
    else if (sourceExtensions.has(path.extname(entry.name))) out.push(full);
  }
  return out;
}

for (const file of scanRoots.flatMap(filesUnder)) {
  const relative = path.relative(root, file).split(path.sep).join("/");
  const text = fs.readFileSync(file, "utf8");
  if (relative !== "scripts/check-boundaries.mjs" && sqlPattern.test(text)) {
    errors.push(`${relative}: SQL statement text is forbidden in P1-VS-001.`);
  }
  for (const match of text.matchAll(importPattern)) {
    const specifier = match[2];
    if (forbiddenImports.some((token) => specifier.toLowerCase().includes(token))) {
      errors.push(`${relative}: forbidden dependency import ${specifier}`);
    }
    if ((relative.startsWith("src/app/") || relative.startsWith("src/features/")) && specifier.includes("adapters/")) {
      errors.push(`${relative}: app/features must not import fixture adapters directly.`);
    }
  }
}

const packageJson = JSON.parse(fs.readFileSync(path.join(root, "package.json"), "utf8"));
const declared = { ...(packageJson.dependencies ?? {}), ...(packageJson.devDependencies ?? {}) };
for (const name of Object.keys(declared)) {
  if (forbiddenImports.some((token) => name.toLowerCase().includes(token))) {
    errors.push(`package.json: forbidden dependency ${name}`);
  }
}
if (errors.length) {
  console.error("P1-VS-001 boundary validation failed:");
  for (const error of errors) console.error(` - ${error}`);
  process.exit(1);
}
console.log("P1-VS-001 boundary validation passed.");
