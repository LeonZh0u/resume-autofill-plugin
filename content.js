console.log("The script has started running.");

// This function adds a "Generate Answer" button above every text input field on the webpage
function addButtonToInputFields() {
    // Get all input elements on the page
    const inputFields = document.getElementsByTagName('input');

    console.log("Found " + inputFields.length + " input fields.");

    // Iterate through all input fields
    for(let i = 0; i < inputFields.length; i++) {
        // Check if the input field is a text field
        if(inputFields[i].type.toLowerCase() === 'text') {
            console.log("Found a text input field.");

            // Create a new button element
            const button = document.createElement('button');
            
            // Set the button text
            button.innerHTML = 'Generate Answer';
            
            // Set an onclick function for the button
            button.onclick = function() {
                // Here you would call your backend API to generate an answer
                // For now, we'll just put some dummy text in the field
                inputFields[i].value = 'AI-generated answer';
            };
            
            // Insert the button into the DOM before the input field
            inputFields[i].parentNode.insertBefore(button, inputFields[i]);

            console.log("Inserted a button.");
        }
    }
}

// Call the function when the webpage has fully loaded
window.onload = function() {
    console.log("The window has loaded.");
    addButtonToInputFields();
};
