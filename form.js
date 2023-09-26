document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("wf-form-");
    const successSection = document.getElementById("success-section");
    const failureSection = document.getElementById("failure-section");

    form.addEventListener("submit", function(event) {
        event.preventDefault();
    
        const formData = new FormData(form);
    
        fetch('https://script.google.com/macros/s/AKfycby2baXwlWPJLxfXoPtZI8yPBMSQ06PmUdLK7fqssy3tL9QD0ahqNg1SPIo37_C9YHf2/exec', {
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
            form.style.display = "none";
            successSection.style.display = "block";
            failureSection.style.display = "none";
          } else {
            form.style.display = "none";
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