import { readFile, readdir, stat } from "node:fs/promises";
import { resolve } from "node:path";
import process from "node:process";

const root = resolve(import.meta.dirname, "..");
const required = [
  "index.html","books.html","publishing-house.html","fiction.html","framework.html",
  "fragments.html","notes.html","about.html","contact.html","review-copies.html",
  "press.html","privacy.html","404.html","CNAME","sitemap.xml","robots.txt",
  "assets/css/site.css","assets/js/site.js",
  "assets/brand/publishing-house-banner.webp",
  "assets/brand/publishing-house-banner-mobile.webp",
  "assets/images/editorial/hero-balcony-web.webp",
  "assets/images/editorial/hero-balcony-web.jpg",
  "assets/images/editorial/hero-balcony-mobile.webp",
  "assets/images/social/og-author.jpg",
  "assets/images/social/og-publishing-house.jpg"
];

const errors = [];
for (const file of required) {
  try { await stat(resolve(root, file)); }
  catch { errors.push(`Missing ${file}`); }
}

const books = JSON.parse(await readFile(resolve(root, "content/books.json"), "utf8"));
const slugs = new Set();
for (const book of books) {
  if (!book.slug) errors.push("Book record missing slug");
  if (slugs.has(book.slug)) errors.push(`Duplicate slug: ${book.slug}`);
  slugs.add(book.slug);
  try { await stat(resolve(root, `book-${book.slug}.html`)); }
  catch { errors.push(`Missing book-${book.slug}.html`); }
}

const html = (await readdir(root)).filter(name => name.endsWith(".html"));
const rx = /(?:href|src|srcset)=["']([^"']+)["']/g;
for (const file of html) {
  const text = await readFile(resolve(root, file), "utf8");
  if (!/<!doctype html>/i.test(text)) errors.push(`${file}: missing doctype`);
  if (!/<title>[^<]+<\/title>/i.test(text)) errors.push(`${file}: missing title`);
  if (!/<meta\s+name=["']description["']/i.test(text)) errors.push(`${file}: missing meta description`);
  if (!/<meta\s+name=["']viewport["']/i.test(text)) errors.push(`${file}: missing viewport`);
  let match;
  while ((match = rx.exec(text))) {
    const candidates = match[1].split(",").map(part => part.trim().split(/\s+/)[0]);
    for (const candidate of candidates) {
      const ref = candidate.split("#")[0].split("?")[0];
      if (!ref || /^(https?:|mailto:|tel:|javascript:|data:|\/\/)/.test(ref)) continue;
      try { await stat(resolve(root, ref.replace(/^\//, ""))); }
      catch { errors.push(`${file}: broken ${ref}`); }
    }
  }
}

for (const jsonFile of [
  "config/site.json","content/books.json","content/pages.json",
  "content/fragments.json","content/notes.json","site.webmanifest"
]) {
  try { JSON.parse(await readFile(resolve(root, jsonFile), "utf8")); }
  catch (error) { errors.push(`${jsonFile}: ${error.message}`); }
}

const index = await readFile(resolve(root, "index.html"), "utf8");
if (!index.includes("hero-balcony-web.webp")) errors.push("index.html: stable hero slot not connected");
if (!index.includes("publishing-house-banner.webp")) errors.push("index.html: publishing house banner not connected");
if (!(await readFile(resolve(root, "sitemap.xml"), "utf8")).includes("publishing-house.html")) {
  errors.push("sitemap.xml: publishing-house.html missing");
}

if (errors.length) {
  console.error([...new Set(errors)].join("\n"));
  process.exit(1);
}
console.log(`Validated ${html.length} HTML pages, ${books.length} books, brand assets, metadata, and local references.`);
