document.addEventListener('DOMContentLoaded', () => {
  const navToggle = document.querySelector('.nav-toggle');
  const navMenu = document.getElementById('nav-menu');
  const cards = document.querySelectorAll('.action-card');
  const modal = document.getElementById('uploadModal');
  const modalTitle = document.getElementById('modalTitle');
  const closeModalBtn = document.getElementById('closeModal');
  const uploadForm = document.querySelector('.upload-form');
  const loading = document.getElementById('loading');
  const idleMessage = document.getElementById('idleMessage');
  const scoreValue = document.getElementById('scoreValue');
  const progressFill = document.getElementById('progressFill');

  navToggle?.addEventListener('click', () => {
    const isOpen = navMenu.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', String(isOpen));
  });

  cards.forEach((card) => {
    card.addEventListener('click', () => {
      const mediaType = card.dataset.media || 'Media';
      modalTitle.textContent = `Upload ${mediaType} File`;
      modal.hidden = false;
    });
  });

  closeModalBtn?.addEventListener('click', () => {
    modal.hidden = true;
  });

  modal?.addEventListener('click', (event) => {
    if (event.target === modal) {
      modal.hidden = true;
    }
  });

  uploadForm?.addEventListener('submit', (event) => {
    event.preventDefault();
    modal.hidden = true;
    idleMessage.hidden = true;
    loading.hidden = false;

    window.setTimeout(() => {
      loading.hidden = true;
      idleMessage.hidden = false;
      idleMessage.textContent = 'Analysis complete. Review your updated trust score below.';
      const simulatedScore = 91;
      scoreValue.textContent = `${simulatedScore}%`;
      progressFill.style.width = `${simulatedScore}%`;
      document.querySelector('.progress')?.setAttribute(
        'aria-label',
        `Trust score progress bar showing ${simulatedScore} percent confidence`
      );
    }, 1400);
  });
});
