import assert from "node:assert/strict";
import { readFileSync, existsSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const read = (path) => readFileSync(join(root, path), "utf8");

const index = read("index.html");
const script = read("script.js");
const styles = read("styles.css");

function jpegSize(path) {
  const buffer = readFileSync(join(root, path));
  let offset = 2;

  while (offset < buffer.length) {
    if (buffer[offset] !== 0xff) {
      offset += 1;
      continue;
    }

    const marker = buffer[offset + 1];
    const length = buffer.readUInt16BE(offset + 2);
    if (marker >= 0xc0 && marker <= 0xc3) {
      return {
        height: buffer.readUInt16BE(offset + 5),
        width: buffer.readUInt16BE(offset + 7),
      };
    }

    offset += 2 + length;
  }

  throw new Error(`Could not read JPEG dimensions: ${path}`);
}

function publicAssetExists(path) {
  const fullPath = join(root, path);
  assert.ok(existsSync(fullPath), `Missing referenced asset: ${path}`);
  assert.ok(statSync(fullPath).size > 0, `Referenced asset is empty: ${path}`);
}

assert.match(index, /Isaac Andress Martinez/);
assert.match(index, /Class of 2026/);
assert.match(index, /June 6, 2026/);
assert.match(index, /2:00 PM/);
assert.match(index, /Eagle Mountain, Utah/);
assert.match(index, /RSVP for address/);
assert.doesNotMatch(index, /Add the Google Form link/);
assert.match(index, /<meta property="og:image" content="https:\/\/izzysgraduation\.com\/assets\/social-preview\.jpg">/);
assert.match(index, /<meta property="og:image:width" content="1200">/);
assert.match(index, /<meta property="og:image:height" content="630">/);
assert.match(index, /<meta property="twitter:card" content="summary_large_image">/);
assert.match(index, /fonts\.googleapis\.com\/css2\?family=Graduate/);
assert.match(index, /family=Space\+Grotesk/);
assert.match(styles, /--font-display: "Graduate"/);
assert.match(styles, /--font-body: "Space Grotesk"/);
assert.match(styles, /\.photo-grid\s*{[\s\S]*column-count: 3;/, "Gallery should use a masonry column layout on desktop");
assert.match(styles, /\.gallery-photo img\s*{[\s\S]*height: auto;[\s\S]*object-fit: contain;/, "Gallery photos should keep their natural crop");

const [, galleryMarkup = ""] = index.match(
  /<div class="photo-grid" aria-label="Photo gallery">([\s\S]*?)<\/div>\s*<\/section>/,
) ?? [];
assert.ok(galleryMarkup, "Photo gallery markup is missing");

const galleryMatches = [...galleryMarkup.matchAll(/assets\/photos\/gallery-(\d+)\.jpg/g)];
const galleryNumbers = galleryMatches.map(([, number]) => Number(number));
assert.equal(galleryNumbers.length, 16, "Gallery should include the refreshed 16-photo set");
assert.deepEqual(
  galleryNumbers,
  Array.from({ length: 16 }, (_, index) => index + 1),
  "Gallery image references should stay in order",
);

for (const secret of ["5357", "Desert Lilly", "84005", "N. Desert"]) {
  assert.equal(index.includes(secret), false, `Public HTML leaks address detail: ${secret}`);
  assert.equal(script.includes(secret), false, `Public JS leaks address detail: ${secret}`);
  assert.equal(styles.includes(secret), false, `Public CSS leaks address detail: ${secret}`);
}

assert.equal(index.includes("Red 90s detail."), false, "Removed hat gallery caption is still visible");
assert.equal(index.includes("hat-thumb"), false, "Removed hat gallery image is still referenced");
assert.equal(index.includes("hat-detail"), false, "Removed hat detail image is still referenced");

const socialPreviewSize = jpegSize("assets/social-preview.jpg");
assert.deepEqual(socialPreviewSize, { width: 1200, height: 630 }, "Social preview should be the standard OG image size");

for (const [, src] of index.matchAll(/\s(?:src|href)="([^"]+)"/g)) {
  if (
    src.startsWith("#") ||
    src.startsWith("http") ||
    src === "styles.css" ||
    src === "script.js"
  ) {
    continue;
  }

  publicAssetExists(src);
}

assert.match(script, /const EVENT_DATE = new Date\("2026-06-06T14:00:00-06:00"\)/);
assert.match(script, /const RSVP_FORM_URL = "/);
assert.doesNotMatch(script, /Add the Google Form URL/);
assert.doesNotMatch(read("README.md"), /paste the public form URL into `RSVP_FORM_URL`/);

const rsvpMatch = script.match(/const RSVP_FORM_URL = "([^"]*)"/);
assert.ok(rsvpMatch, "RSVP_FORM_URL constant is missing");

if (process.env.ALLOW_PENDING_RSVP === "1" && rsvpMatch[1] === "") {
  console.warn("RSVP_FORM_URL is pending; skipping publish-ready RSVP assertion.");
} else {
  assert.match(
    rsvpMatch[1],
    /^https:\/\/docs\.google\.com\/forms\//,
    "RSVP_FORM_URL must be the published Google Forms URL before publishing the site",
  );
}

console.log("Static invitation checks passed.");
