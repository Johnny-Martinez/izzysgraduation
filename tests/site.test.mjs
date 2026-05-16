import assert from "node:assert/strict";
import { readFileSync, existsSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const read = (path) => readFileSync(join(root, path), "utf8");

const index = read("index.html");
const script = read("script.js");
const styles = read("styles.css");

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
assert.match(index, /fonts\.googleapis\.com\/css2\?family=Graduate/);
assert.match(index, /family=Space\+Grotesk/);
assert.match(styles, /--font-display: "Graduate"/);
assert.match(styles, /--font-body: "Space Grotesk"/);

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
