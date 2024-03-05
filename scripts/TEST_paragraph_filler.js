// Locate the paragraph element with class "jstest"
var paragraph = document.querySelector('.jstest');

// Check if the paragraph element is found
if (paragraph) {
    // Change the text content of the paragraph
    paragraph.textContent = "The JavaScript successfully changed this text. Yippee!";
} else {
    console.log("Paragraph element with class 'jstest' not found.");
}