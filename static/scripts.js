window.onload = function() {
    // Get the flash message element
    var flashMessage = document.getElementById('flash-message');
    if (flashMessage) {
        // Set a timeout to hide the message after 5 seconds
        setTimeout(function() {
            flashMessage.classList.add('hide');
        }, 5000);  // 5000ms = 5 seconds
    }
};