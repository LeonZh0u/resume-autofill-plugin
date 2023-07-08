console.log("The script has started running.");

// This function adds a "Generate Answer" button above every textarea on the webpage
function addButtonToTextarea() {
    // Get all textarea elements on the page
    const textareas = document.getElementsByTagName('textarea');

    console.log("Found " + textareas.length + " textarea fields.");

    // Iterate through all textarea fields
    for(let i = 0; i < textareas.length; i++) {
        console.log("Found a textarea field.");

        // Find the parent label associated with this textarea field
        const parentLabel = textareas[i].closest('label');

        if (parentLabel) {
            // Filter out unnecessary elements and get just the label text
            const labelText = Array.from(parentLabel.childNodes)
                .filter(node => node.nodeType === Node.TEXT_NODE && node.textContent.trim() !== '')
                .map(node => node.textContent.trim())
                .join(' ');

            console.log("Label text: " + labelText);
        } else {
            console.log("No label found");
        }

        // Create a new button element
        const button = document.createElement('button');

        // Set the button text
        button.innerHTML = 'Generate Answer';

        // Set an onclick function for the button
        button.onclick = function() {
            // Here you would call your backend API to generate an answer
            // For now, we'll just put some dummy text in the field
            textareas[i].value = 'AI-generated answer';
        };

        // Insert the button into the DOM before the textarea field
        textareas[i].parentNode.insertBefore(button, textareas[i]);

        console.log("Inserted a button.");
    }
}

// Call the function when the webpage has fully loaded
window.onload = function() {
    console.log("The window has loaded.");
    addButtonToTextarea();
};
