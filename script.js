// script.js

document.addEventListener('DOMContentLoaded', function() {
    // Modal functionality
    const modal = document.getElementById('myModal');
    const btn = document.getElementById('myBtn');
    const span = document.getElementsByClassName('close')[0];

    btn.onclick = function() {
        modal.style.display = 'block';
    };

    span.onclick = function() {
        modal.style.display = 'none';
    };

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    };

    // Form handling
    const form = document.getElementById('myForm');
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent form submission
        // Handle form data here
        const formData = new FormData(form);
        console.log('Form submitted:', Object.fromEntries(formData));
        // Optionally reset the form
        form.reset();
    });

    // UI interactions
    const toggleButton = document.getElementById('toggleButton');
    toggleButton.addEventListener('click', function() {
        const content = document.getElementById('content');
        content.classList.toggle('hidden');
    });
});
