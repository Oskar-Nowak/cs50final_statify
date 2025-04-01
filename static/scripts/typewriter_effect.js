document.addEventListener("DOMContentLoaded", function() {
    const initialText = "All in one place.";
    const finalText = "All on Statify.";
    const typingSpeed = 100;        // Speed is passed in miliseconds.
    const erasingSpeed = 75;         // Speed is passed in miliseconds. 
    const pauseBeforeErase = 500;   // Lenght of that pause is also passed in miliseconds.

    let i = 0;

    const typewriterTextElement = document.getElementById("typewriter-text");
    const cursorElement = document.getElementById("cursor");

    function typeText(text, callback) {
        if (i < text.length) {
            typewriterTextElement.innerHTML += text.charAt(i);
            i++;
            setTimeout(() => typeText(text, callback), typingSpeed)
        }
        else {
            // After typing the full text, trigger the callback (for erasing)
            if (callback) setTimeout(callback, pauseBeforeErase);
        }
    }

    function eraseText(text, callback) {
        if (i > 3) { // Start erasing after "All in "
            typewriterTextElement.innerHTML = text.substring(0, i);
            i--;
            setTimeout(() => eraseText(text, callback), erasingSpeed);
        }
        else {
            // After erasing, trigger the callback (for typing the final text)
            if (callback) callback();
        }
    }

    function typeWriter() {
        // Type "all in one place."
        typeText(initialText, () => {
            // After typing, erase "one place."
            eraseText(initialText, () => {
                i = 4; // Reset i to after "All " to start typing "on Statify"
                // Type "on Statify."
                typeText(finalText, () => {
                    // Remove the cursor after typing is finished.
                    cursorElement.style.display = "none";
                }); 
            });
        });
    }

    // Start the typewriter effect
    typeWriter();
});