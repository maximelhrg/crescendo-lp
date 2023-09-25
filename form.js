document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("wf-form-");

    form.addEventListener("submit", function(event) {
        event.preventDefault();
    
        const formData = new FormData(form);
    
        fetch('https://script.google.com/macros/s/AKfycbzTp7CLkM3eZkoU_O5ktAGHAj0ope8CMQIZEJtYwkJj4Gq-zAgRNHNZkSw8164yaxmJ/exec', {
            method: 'POST',
            mode: 'cors',
            body: JSON.stringify({
                name: formData.get('name'),
                email: formData.get('email'),
                social: formData.get('social'),
                comments: formData.get('comments'),
            
            }),
            headers: {
                "Content-Type": "application/json",
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