document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("SUBMIT");

    form.addEventListener("submit", function(event) {
        event.preventDefault();
    
        const formData = new FormData(form);
    
        fetch('https://script.google.com/macros/s/AKfycbz34SmZmzQDiu2FKEx9bOB2te0kGiTIC9f6sicV2zBWbvGooh2EA759qwE5ltI2aNbJ/exec', {
          method: 'POST',
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