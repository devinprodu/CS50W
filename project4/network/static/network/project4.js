document.addEventListener('DOMContentLoaded', function() {

   document.querySelector("#follow_btn").addEventListener('click', () => follow_toggle())
  
    
  });
  
  function follow_toggle() {
    fetch('/follow', {
        method: 'POST',
        body: JSON.stringify({
            followee: document.querySelector("#usertitle").value
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log(result);
    })
  }