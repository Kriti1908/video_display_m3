document.getElementById("select_photo").addEventListener("click", function() {
    document.querySelector(".editor").scrollIntoView({ 
        behavior: 'smooth' 
    });
});


document.getElementById("upload").addEventListener("click", function() {
    window.location.href = "/photos/{{username}}";
});



let selectedFilenames = [];

function toggleSelection(element, filename) {
    element.classList.toggle('selected');
    if (selectedFilenames.includes(filename)) {
        console.log("Selected filenames:", selectedFilenames);
        // Deselecting: remove filename from the array
        const index = selectedFilenames.indexOf(filename);
        if (index !== -1) {
            selectedFilenames.splice(index, 1);
        }
    } else {
        // Selecting: add filename to the array
        selectedFilenames.push(filename);
    }
    console.log("***Selected filenames:", selectedFilenames);
}

function saveSelection() {
    // Send selected filenames to Python using AJAX
    fetch('/save_selected_photos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ filenames: selectedFilenames })
    })
    .then(response => {
        if (response.ok) {
            console.log('Selected filenames sent successfully');
        } else {
            console.error('Failed to send selected filenames');
        }
    })
    .catch(error => {
        console.error('Error sending selected filenames:', error);
    });
}

function searchImages() {
    // Get the search query from the input field
    var query = document.getElementById('search-bar').value.trim();

    // Send an AJAX request to the server
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/search?query=' + encodeURIComponent(query), true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            // Process the response
            var response = JSON.parse(xhr.responseText);
            if (response.success) {
                displaySearchResults(response.images);
            } else {
                displaySearchResults([]);
            }
        }
    };
    xhr.send();
}

function displaySearchResults(images) {
    var resultDiv = document.getElementById('search-result-message');
    resultDiv.innerHTML = '';

    if (images.length > 0) {
        var resultMessage = 'Found ' + images.length + ' image(s):<br>';
        resultMessage += images.join(', ');
        resultDiv.innerHTML = resultMessage;
    } else {
        resultDiv.innerHTML = 'No images found for the given query.';
    }
}


// Function to clear previous search results
function clearSearchResults() {
    var editBoxes = document.querySelectorAll('.edit-box');
    editBoxes.forEach(function(box) {
        box.classList.remove('matched-filename');
    });
}

// Function to apply style for matched filenames
function applyMatchedStyle(matchedFilenames) {
    matchedFilenames.forEach(function(filename) {
        var matchedBox = document.querySelector('.edit-box[data-filename="' + filename + '"]');
        if (matchedBox) {
            matchedBox.classList.add('matched-filename');
        }
    });
}

// Function to display "Filename not found" message on the page
function displayNotFoundMessage() {
    var messageContainer = document.getElementById('search-message');
    messageContainer.textContent = 'Filename not found.';
}

// Function to display error message on the page
function displayErrorMessage() {
    var messageContainer = document.getElementById('search-message');
    messageContainer.textContent = 'Error occurred while searching.';
}




