document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("SUBMIT");

    form.addEventListener("submit", function(event) {
        event.preventDefault();
    
        const formData = new FormData(form);
    
        fetch('https://script.google.com/macros/s/AKfycbyB4xsEL4lxP30N_oh6AaSFFB6Nm1viTXFW-RMqJRQQXQ1pdORTQtYo9nqOXn98mKTg/exec', {
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