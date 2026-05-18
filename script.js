const RSVP_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScHXf6Nk9xX7A36_lYZqaUMQdFO4KmRSxG4onfcCRnk90Fb2A/viewform";
const EVENT_DATE = new Date("2026-06-06T14:00:00-06:00");

const rsvpLinks = document.querySelectorAll("[data-rsvp-link]");
const dialog = document.querySelector("[data-rsvp-dialog]");
const closeDialog = document.querySelector("[data-dialog-close]");
const lightboxTriggers = document.querySelectorAll("[data-lightbox-trigger]");
const lightbox = document.querySelector("[data-lightbox]");
const lightboxImage = document.querySelector("[data-lightbox-image]");
const lightboxCaption = document.querySelector("[data-lightbox-caption]");
const closeLightbox = document.querySelector("[data-lightbox-close]");

function openRsvp(event) {
  if (RSVP_FORM_URL) {
    event.currentTarget.setAttribute("href", RSVP_FORM_URL);
    event.currentTarget.setAttribute("target", "_blank");
    event.currentTarget.setAttribute("rel", "noopener noreferrer");
    return;
  }

  event.preventDefault();
  if (dialog && typeof dialog.showModal === "function") {
    dialog.showModal();
  } else {
    window.alert("The RSVP link could not open. Please refresh the page and try again.");
  }
}

rsvpLinks.forEach((link) => {
  link.addEventListener("click", openRsvp);
});

if (closeDialog) {
  closeDialog.addEventListener("click", () => dialog.close());
}

function openLightbox(trigger) {
  const image = trigger.querySelector("img");
  if (!image) {
    return;
  }

  const figure = trigger.closest("figure");
  const caption = figure?.querySelector("figcaption")?.textContent?.trim() || image.alt;

  if (!lightbox || !lightboxImage || typeof lightbox.showModal !== "function") {
    window.open(image.currentSrc || image.src, "_blank", "noopener,noreferrer");
    return;
  }

  lightboxImage.src = image.currentSrc || image.src;
  lightboxImage.alt = image.alt;

  if (lightboxCaption) {
    lightboxCaption.textContent = caption;
  }

  document.body.classList.add("is-lightbox-open");
  lightbox.showModal();
}

lightboxTriggers.forEach((trigger) => {
  trigger.addEventListener("click", () => openLightbox(trigger));
});

if (closeLightbox && lightbox) {
  closeLightbox.addEventListener("click", () => lightbox.close());
}

if (lightbox) {
  lightbox.addEventListener("click", (event) => {
    if (event.target === lightbox) {
      lightbox.close();
    }
  });

  lightbox.addEventListener("close", () => {
    document.body.classList.remove("is-lightbox-open");
    if (lightboxImage) {
      lightboxImage.removeAttribute("src");
      lightboxImage.alt = "";
    }
  });
}

function updateCountdown() {
  const now = new Date();
  const remainingMs = Math.max(EVENT_DATE.getTime() - now.getTime(), 0);
  const totalMinutes = Math.floor(remainingMs / 60000);
  const days = Math.floor(totalMinutes / 1440);
  const hours = Math.floor((totalMinutes % 1440) / 60);
  const minutes = totalMinutes % 60;

  document.querySelector("[data-countdown-days]").textContent = String(days);
  document.querySelector("[data-countdown-hours]").textContent = String(hours).padStart(2, "0");
  document.querySelector("[data-countdown-minutes]").textContent = String(minutes).padStart(2, "0");
}

updateCountdown();
window.setInterval(updateCountdown, 60000);
