document.addEventListener('DOMContentLoaded', function() {
    // Get all flash message elements
    let flashMessages = document.querySelectorAll('.flash-message');
    console.log("Flash Messages Found:", flashMessages);

    flashMessages.forEach(function(flashMessage) {
        if (flashMessage) {
            // Set a timeout to hide the message after 5 seconds
            setTimeout(function() {
                flashMessage.classList.add('fade-out');
            }, 5000);
        }
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const images = document.querySelectorAll('.project-image');

    images.forEach(function(img) {
        img.onload = function() {
            const width = img.naturalWidth;
            const height = img.naturalHeight;

            if (width > height && width > 600){
                console.log("wide")
                img.closest('.gallery').classList.add('wide'); // Add class to landscape images
            }

            if (height > width && height > 600){
                console.log("tall")
                img.closest('.gallery').classList.add('tall')
            }
            if (height == width && height > 600){
                console.log("big")
                img.closest('.gallery').classList.add('big')
            }
        };

        // Handle cached images that load instantly
        if (img.complete) {
            img.onload();
        }
    });
});