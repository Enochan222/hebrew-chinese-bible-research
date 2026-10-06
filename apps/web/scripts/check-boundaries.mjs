import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const scanRoots = ["src", "tests", "scripts"];
const sourceExtensions = new Set([".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"]);

const forbiddenPackageExact = new Set([
  "@supabase/supabase-js",
  "supabase",
  "prisma",
  "@prisma/client",
  "drizzle-orm",
  "postgres",
  "pg",
  "aws-sdk",
]);
const forbiddenPackagePrefixes = [
  "@prisma/",
  "@neondatabase/",
  "@auth/",
  "@clerk/",
  "@aws-sdk/",
  "@google-cloud/",
  "@azure/",
  "firebase",
  "auth0",
  "next-auth",
];

const sqlPattern =
  /\b(?:SELECT\s+.+\s+FROM|INSERT\s+INTO|UPDATE\s+.+\s+SET|DELETE\s+FROM|CREATE\s+(?:TABLE|VIEW|FUNCTION)|ALTER\s+TABLE|DROP\s+(?:TABLE|VIEW|SCHEMA))\b/i;
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

function packageRoot(specifier) {
  if (specifier.startsWith(".") || specifier.startsWith("@/") || specifier.startsWith("/")) return null;
  if (specifier.startsWith("@")) return specifier.split("/").slice(0, 2).join("/");
  return specifier.split("/")[0];
}

function isForbiddenDependency(specifier) {
  const pkg = packageRoot(specifier);
  if (!pkg) return false;
  return forbiddenPackageExact.has(pkg) || forbiddenPackagePrefixes.some((prefix) => pkg.startsWith(prefix));
}

for (const file of scanRoots.flatMap(filesUnder)) {
  const relative = path.relative(root, file).split(path.sep).join("/");
  const text = fs.readFileSync(file, "utf8");

  if (relative !== "scripts/check-boundaries.mjs" && sqlPattern.test(text)) {
    errors.push(`${relative}: raw SQL statement text is forbidden in the web runtime.`);
  }

  for (const match of text.matchAll(importPattern)) {
    const specifier = match[2];
    if (isForbiddenDependency(specifier)) {
      errors.push(`${relative}: forbidden direct infrastructure dependency import ${specifier}`);
    }
    if (
      (relative.startsWith("src/app/") || relative.startsWith("src/features/")) &&
      specifier.includes("adapters/")
    ) {
      errors.push(`${relative}: app/features must not import adapters directly.`);
    }
  }
}

const packageJson = JSON.parse(fs.readFileSync(path.join(root, "package.json"), "utf8"));
const declared = { ...(packageJson.dependencies ?? {}), ...(packageJson.devDependencies ?? {}) };
for (const name of Object.keys(declared)) {
  if (isForbiddenDependency(name)) {
    errors.push(`package.json: forbidden direct infrastructure dependency ${name}`);
  }
}

if (errors.length) {
  console.error("Web runtime boundary validation failed:");
  for (const error of errors) console.error(` - ${error}`);
  process.exit(1);
}
console.log("Web runtime boundary validation passed.");
