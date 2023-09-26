document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("wf-form-");
    const successSection = document.getElementById("success-section");
    const failureSection = document.getElementById("failure-section");

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
                "Content-Type": "text/plain;charset=utf-8",
            }
        })
        .then(response => {
          if (response.ok) {
            successSection.style.display = "block";
            failureSection.style.display = "none";
          } else {
            successSection.style.display = "none";
            failureSection.style.display = "block";
          }
        })
        .catch(error => {
          console.error('Error:', error);
          successSection.style.display = "none";
        failureSection.style.display = "block";
        });
    
        form.reset();
      });
    });