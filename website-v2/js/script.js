// Mobile navigation
const menuToggle = document.getElementById("menuToggle");
const navLinks = document.getElementById("navLinks");

if (menuToggle && navLinks) {
  menuToggle.addEventListener("click", () => {
    const isOpen = navLinks.classList.toggle("open");
    menuToggle.setAttribute("aria-expanded", String(isOpen));
  });

  // Close the mobile menu after the visitor chooses a section.
  navLinks.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      navLinks.classList.remove("open");
      menuToggle.setAttribute("aria-expanded", "false");
    });
  });
}

// Show the current year when the footer includes its year element.
const yearElement = document.getElementById("year");

if (yearElement) {
  yearElement.textContent = new Date().getFullYear();
}

// Validate the enquiry form and send it to Formspree.
const contactForm = document.getElementById("contactForm");
const formMessage = document.getElementById("formMessage");
const formspreeEndpoint = "https://formspree.io/f/mvkzalbb";

if (contactForm) {
  const submitButton = contactForm.querySelector('button[type="submit"]');
  const nameField = contactForm.elements.namedItem("name");
  const messageField = contactForm.elements.namedItem("message");
  let isSubmitting = false;

  // Clear custom errors as the visitor corrects a whitespace-only value.
  [nameField, messageField].forEach((field) => {
    if (field && "setCustomValidity" in field) {
      field.addEventListener("input", () => field.setCustomValidity(""));
    }
  });

  contactForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (isSubmitting) return;

    // A field containing only spaces should count as empty.
    if (nameField && "setCustomValidity" in nameField) {
      nameField.setCustomValidity(
        nameField.value.trim() ? "" : "Please enter your name."
      );
    }

    if (messageField && "setCustomValidity" in messageField) {
      messageField.setCustomValidity(
        messageField.value.trim() ? "" : "Please describe your project."
      );
    }

    if (!contactForm.checkValidity()) {
      contactForm.reportValidity();

      if (formMessage) {
        formMessage.textContent =
          "Please check the highlighted fields and try again. Your enquiry has not been sent.";
      }
      return;
    }

    isSubmitting = true;
    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = "Sending…";
    }
    if (formMessage) {
      formMessage.textContent = "Sending your enquiry…";
    }

    try {
      const response = await fetch(formspreeEndpoint, {
        method: "POST",
        body: new FormData(contactForm),
        headers: { Accept: "application/json" },
      });

      let result = {};
      try {
        result = await response.json();
      } catch {
        // Keep a useful fallback if the server returns a non-JSON response.
      }

      if (!response.ok) {
        const serverErrors = Array.isArray(result.errors)
          ? result.errors
              .map((error) =>
                typeof error === "string" ? error : error?.message
              )
              .filter(Boolean)
              .join(" ")
          : "";
        const statusMessage =
          response.status === 429
            ? "Too many recent submissions. Please wait a moment, then try again."
            : `Formspree could not accept your enquiry (HTTP ${response.status}). Please try again.`;
        throw new Error(
          serverErrors || result.error || statusMessage
        );
      }

      if (formMessage) {
        formMessage.textContent =
          "Thank you! Formspree confirmed your enquiry was received.";
      }
      contactForm.reset();
    } catch (error) {
      if (formMessage) {
        formMessage.textContent =
          error instanceof TypeError
            ? "We couldn’t reach Formspree. Check your connection and try again. Your details are still in the form."
            : error.message ||
              "We couldn’t send your enquiry. Please check your connection and try again.";
      }
    } finally {
      isSubmitting = false;
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = "Send enquiry ↗";
      }
    }
  });
}
