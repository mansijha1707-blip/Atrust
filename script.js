-// script.js
+document.addEventListener('DOMContentLoaded', () => {
+  const navToggle = document.querySelector('.nav-toggle');
+  const navMenu = document.getElementById('nav-menu');
+  const cards = document.querySelectorAll('.action-card');
+  const modal = document.getElementById('uploadModal');
+  const modalTitle = document.getElementById('modalTitle');
+  const closeModalBtn = document.getElementById('closeModal');
+  const uploadForm = document.querySelector('.upload-form');
+  const loading = document.getElementById('loading');
+  const idleMessage = document.getElementById('idleMessage');
+  const scoreValue = document.getElementById('scoreValue');
+  const progressFill = document.getElementById('progressFill');
 
-document.addEventListener('DOMContentLoaded', function() {
-    // Modal functionality
-    const modal = document.getElementById('myModal');
-    const btn = document.getElementById('myBtn');
-    const span = document.getElementsByClassName('close')[0];
+  navToggle?.addEventListener('click', () => {
+    const isOpen = navMenu.classList.toggle('open');
+    navToggle.setAttribute('aria-expanded', String(isOpen));
+  });
 
-    btn.onclick = function() {
-        modal.style.display = 'block';
-    };
+  cards.forEach((card) => {
+    card.addEventListener('click', () => {
+      const mediaType = card.dataset.media || 'Media';
+      modalTitle.textContent = `Upload ${mediaType} File`;
+      modal.hidden = false;
+    });
+  });
 
-    span.onclick = function() {
-        modal.style.display = 'none';
-    };
+  closeModalBtn?.addEventListener('click', () => {
+    modal.hidden = true;
+  });
 
-    window.onclick = function(event) {
-        if (event.target == modal) {
-            modal.style.display = 'none';
-        }
-    };
+  modal?.addEventListener('click', (event) => {
+    if (event.target === modal) {
+      modal.hidden = true;
+    }
+  });
 
-    // Form handling
-    const form = document.getElementById('myForm');
-    form.addEventListener('submit', function(event) {
-        event.preventDefault(); // Prevent form submission
-        // Handle form data here
-        const formData = new FormData(form);
-        console.log('Form submitted:', Object.fromEntries(formData));
-        // Optionally reset the form
-        form.reset();
-    });
+  uploadForm?.addEventListener('submit', (event) => {
+    event.preventDefault();
+    modal.hidden = true;
+    idleMessage.hidden = true;
+    loading.hidden = false;
 
-    // UI interactions
-    const toggleButton = document.getElementById('toggleButton');
-    toggleButton.addEventListener('click', function() {
-        const content = document.getElementById('content');
-        content.classList.toggle('hidden');
-    });
+    window.setTimeout(() => {
+      loading.hidden = true;
+      idleMessage.hidden = false;
+      idleMessage.textContent = 'Analysis complete. Review your updated trust score below.';
+      const simulatedScore = 91;
+      scoreValue.textContent = `${simulatedScore}%`;
+      progressFill.style.width = `${simulatedScore}%`;
+      document.querySelector('.progress')?.setAttribute(
+        'aria-label',
+        `Trust score progress bar showing ${simulatedScore} percent confidence`
+      );
+    }, 1400);
+  });
 });
