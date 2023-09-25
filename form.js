document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("wf-form-");

    form.addEventListener("submit", function(event) {
        event.preventDefault();
    
        const formData = new FormData(form);
    
        fetch('https://script.google.com/macros/s/AKfycbzx7uU9voRqQEcwmzv9vthuAJq-kBp26LbAqsxPJObJuMdFIYaqv6OLG4alEbk19SzT/exec', {
            method: 'POST',
            mode: 'no-cors', // Add this line
            body: JSON.stringify({
                name: formData.get('name'),
                email: formData.get('email'),
                social: formData.get('social'),
                comments: formData.get('comments'),
            
            }),
            headers: {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST",
                "Access-Control-Allow-Headers": "Content-Type",
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