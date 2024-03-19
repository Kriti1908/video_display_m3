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
            return response.json();
        } else {
            throw new Error('Failed to send selected filenames');
        }
    })
    .then(data => {
        if (!data.video_url) {
            throw new Error('No video_url in response');
        }
        let videoUrl = data.video_url;
        let videoTag = document.getElementById('video-preview');
        // Create a new source element
        // let source = document.getElementById("video-preview");
        // Set the source element's src and type attributes
        // videoTag.src = videoUrl;
        // videoTag.type = 'video/mp4';
        // Remove any existing sources from the video tag
        // while (videoTag.firstChild) {
        //     videoTag.firstChild.remove();
        // }
        // Add the new source to the video tag
        // videoTag.appendChild(source);
        // Load the new video data and play the video
        videoTag.load();
        videoTag.play(); // Start playing the video automatically
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




