// Wait until DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {

  const modal = document.getElementById("uploadModal");
  const closeBtn = document.getElementById("closeModal");
  const actionCards = document.querySelectorAll(".action-card");
  const fileInput = document.getElementById("mediaFile");
  const submitBtn = document.querySelector(".submit-btn");

  // ===== Modal Open =====
  if (actionCards.length && modal) {
    actionCards.forEach(card => {
      card.addEventListener("click", () => {
        modal.removeAttribute("hidden");
      });
    });
  }

  // ===== Modal Close (X button) =====
  if (closeBtn && modal) {
    closeBtn.addEventListener("click", () => {
      modal.setAttribute("hidden", true);
    });
  }

  // ===== Close when clicking outside modal =====
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        modal.setAttribute("hidden", true);
      }
    });
  }

  // ===== Disable button until file selected =====
  if (fileInput && submitBtn) {
    submitBtn.disabled = true;

    fileInput.addEventListener("change", () => {
      submitBtn.disabled = !fileInput.files.length;
    });
  }

  // ===== Optional: Fake Verification Animation =====
  const scoreValue = document.getElementById("scoreValue");
  const progressFill = document.getElementById("progressFill");

  if (submitBtn && scoreValue && progressFill) {
    submitBtn.addEventListener("click", (e) => {
      e.preventDefault();

      let score = 0;
      const target = Math.floor(Math.random() * 40) + 60; // random 60–100%

      const interval = setInterval(() => {
        if (score >= target) {
          clearInterval(interval);
        } else {
          score++;
          scoreValue.textContent = score + "%";
          progressFill.style.width = score + "%";
        }
      }, 15);

      modal.setAttribute("hidden", true);
    });
  }

});
