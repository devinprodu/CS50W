document.addEventListener('DOMContentLoaded', function() {
    // Add event listener to all edit anchor tags.
    var editAnchors = document.querySelectorAll(".edit");
    editAnchors.forEach(anchor => {
        anchor.onclick = function() {
            edit_post(anchor.id);
        }
    })

    var likeBtns = document.querySelectorAll(".likes");
    likeBtns.forEach(like => {
        like.onclick = function() {
            like_toggle(like.id);
        }
    })

    
  });
  
  function edit_post(id) {
    var contentDiv = document.querySelector(`#post_content_${id}`)
    var prevValue = contentDiv.children[0].innerHTML
    contentDiv.innerHTML = `<input class="form-control mb-2" name="content" id="editbox" aria-describedby="editPost" value="${prevValue}"></input>
    <button id="editBtn"type="submit" class="css-button-rounded--sky-small float-right">Submit</button>`
    
    document.querySelector('#editBtn').onclick = function () {

    var csrftoken = document.querySelector('[name="csrfmiddlewaretoken"]').value
    fetch('/edit', {
        method: 'PUT',
        body: JSON.stringify({
            id: id,
            content: contentDiv.children[0].value,
            
        }),
        credentials: 'same-origin',
        headers: {
            "X-CSRFToken": csrftoken
        }
    })
    .then(response => response.json())
    .then(result => {
        var msgBox = document.querySelector('#editResponse')
        if (result['error']) {
            msgBox.style.display = 'block'
            msgBox.innerHTML = result['error']
            contentDiv.innerHTML = prevValue

        }
        else { 
            msgBox.style.display = 'block'
            msgBox.innerHTML = result['message']
            contentDiv.innerHTML = `<div id="post_content_${id}"><p>${contentDiv.children[0].value}</p></div>`
        }
    })
  }
  }
  

  function like_toggle(id) {
    // Get CSRF Token from template
    var csrftoken = document.querySelector('[name="csrfmiddlewaretoken"]').value
    // Send PUT request with post id only
    fetch('/like', {
        method: 'PUT',
        body: JSON.stringify({
            id: id,
                        
        }),
        credentials: 'same-origin',
        headers: {
            "X-CSRFToken": csrftoken
            }
        })
        .then(response => response.json())
        .then(result => {
            console.log(result);
        })
  }