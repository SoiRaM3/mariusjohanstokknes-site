import { readFile, readdir, stat } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import process from "node:process";

const root = resolve(import.meta.dirname, "..");

const required = [
  "index.html",
  "books.html",
  "publishing-house.html",
  "fiction.html",
  "framework.html",
  "fragments.html",
  "notes.html",
  "about.html",
  "contact.html",
  "review-copies.html",
  "press.html",
  "privacy.html",
  "404.html",
  "CNAME",
  "sitemap.xml",
  "robots.txt",
  "assets/css/site.css",
  "assets/js/site.js",
  "assets/brand/publishing-house-banner.webp",
  "assets/brand/publishing-house-banner-mobile.webp",
  "assets/images/editorial/hero-balcony-web.webp",
  "assets/images/editorial/hero-balcony-web.jpg",
  "assets/images/editorial/hero-balcony-mobile.webp",
  "assets/images/social/og-author.jpg",
  "assets/images/social/og-publishing-house.jpg",
];

const errors = [];

async function exists(path) {
  try {
    await stat(path);
    return true;
  } catch {
    return false;
  }
}

function hasNamedMeta(text, name) {
  const tags = text.match(/<meta\b[^>]*>/gi) ?? [];
  const escapedName = name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const namePattern = new RegExp(
    String.raw`\bname\s*=\s*["']${escapedName}["']`,
    "i",
  );
  return tags.some((tag) => namePattern.test(tag));
}

for (const file of required) {
  if (!(await exists(resolve(root, file)))) {
    errors.push(`Missing ${file}`);
  }
}

let books = [];
try {
  books = JSON.parse(await readFile(resolve(root, "content/books.json"), "utf8"));
  if (!Array.isArray(books)) {
    errors.push("content/books.json: expected a top-level array");
    books = [];
  }
} catch (error) {
  errors.push(`content/books.json: ${error.message}`);
}

const slugs = new Set();

for (const book of books) {
  if (!book?.slug) {
    errors.push("Book record missing slug");
    continue;
  }

  if (slugs.has(book.slug)) {
    errors.push(`Duplicate slug: ${book.slug}`);
  }
  slugs.add(book.slug);

  // Only public English records are supposed to have individual pages.
  // Spanish catalogue entries, hidden drafts, and internal records may remain
  // in books.json without a standalone public HTML page.
  const language = String(book.language ?? "");
  const visibility = String(book.public_visibility ?? "");
  const requiresPage =
    language === "English" && ["full", "teaser"].includes(visibility);

  if (requiresPage) {
    const page = resolve(root, `book-${book.slug}.html`);
    if (!(await exists(page))) {
      errors.push(`Missing public English page: book-${book.slug}.html`);
    }
  }
}

const html = (await readdir(root)).filter((name) => name.endsWith(".html"));
const referencePattern = /(?:href|src|srcset)=["']([^"']+)["']/gi;

for (const file of html) {
  const text = await readFile(resolve(root, file), "utf8");

  if (!/<!doctype\s+html\s*>/i.test(text)) {
    errors.push(`${file}: missing doctype`);
  }

  if (!/<title\b[^>]*>\s*[^<]+\s*<\/title>/i.test(text)) {
    errors.push(`${file}: missing title`);
  }

  if (!hasNamedMeta(text, "description")) {
    errors.push(`${file}: missing meta description`);
  }

  if (!hasNamedMeta(text, "viewport")) {
    errors.push(`${file}: missing viewport`);
  }

  referencePattern.lastIndex = 0;
  let match;

  while ((match = referencePattern.exec(text))) {
    const candidates = match[1]
      .split(",")
      .map((part) => part.trim().split(/\s+/)[0]);

    for (const candidate of candidates) {
      const ref = candidate.split("#")[0].split("?")[0];

      if (
        !ref ||
        /^(https?:|mailto:|tel:|javascript:|data:|\/\/)/i.test(ref)
      ) {
        continue;
      }

      const localPath = ref.startsWith("/")
        ? resolve(root, `.${ref}`)
        : resolve(root, dirname(file), ref);

      if (!(await exists(localPath))) {
        errors.push(`${file}: broken ${ref}`);
      }
    }
  }
}

for (const jsonFile of [
  "config/site.json",
  "content/books.json",
  "content/pages.json",
  "content/fragments.json",
  "content/notes.json",
  "site.webmanifest",
]) {
  try {
    JSON.parse(await readFile(resolve(root, jsonFile), "utf8"));
  } catch (error) {
    errors.push(`${jsonFile}: ${error.message}`);
  }
}

try {
  const index = await readFile(resolve(root, "index.html"), "utf8");

  if (!index.includes("hero-balcony-web.webp")) {
    errors.push("index.html: stable hero slot not connected");
  }

  if (!index.includes("publishing-house-banner.webp")) {
    errors.push("index.html: publishing house banner not connected");
  }
} catch (error) {
  errors.push(`index.html: ${error.message}`);
}

try {
  const sitemap = await readFile(resolve(root, "sitemap.xml"), "utf8");

  if (!sitemap.includes("publishing-house.html")) {
    errors.push("sitemap.xml: publishing-house.html missing");
  }
} catch (error) {
  errors.push(`sitemap.xml: ${error.message}`);
}

if (errors.length) {
  console.error([...new Set(errors)].join("\n"));
  process.exit(1);
}

console.log(
  `Validated ${html.length} HTML pages, ${books.length} catalogue records, metadata, assets, and local references.`,
);
