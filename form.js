document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("SUBMIT");

    form.addEventListener("submit", function(event) {
        event.preventDefault();
    
        const formData = new FormData(form);
    
        fetch('https://script.google.com/macros/s/AKfycbyMm1cxcOy6ZS2XeBViym3EX0ywaiVpa7PH6soUUvJPzT6BKba8weOsqbk_FBlP11LP/exec', {
            method: 'POST',
            mode: 'cors', // Add this line
            body: JSON.stringify({
                name: formData.get('Name'),
                email: formData.get('Email'),
                social: formData.get('Social'),
                comments: formData.get('Comments'),
            
          }),
          headers: {
            'Content-Type': 'application/json'
          }
        })
        .then(response => {
          if (response.ok) {
            alert('Form submitted successfully!');
          } else {
            alert('Form submission failed. Please try again later.');
          }
        })
        .catch(error => {
          console.error('Error:', error);
          alert('An error occurred. Please try again later.');
        });
    
        form.reset();
      });
    });