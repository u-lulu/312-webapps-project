// Load existing messages
fetch('/posts')
.then(response => response.json())
.then(data => {
    // Function to add a new message to the list
    function addMessage(message) {
        const listItem = document.createElement('li');
        listItem.textContent = message;
        document.getElementById('messages').appendChild(listItem);
    }

    // Loop through each message in the list
    data.forEach(message => {
        // Check the type of the message
        if (message.type === 'text') {
            // Extract username and body
            const formattedMessage = `${message.username}: ${message.body}`;
            addMessage(formattedMessage);
        } else if (message.type === 'dice') {
            // Extract username, input, output, and total
            const formattedMessage = `${message.username} rolled ${message.input} and got ${message.total} (${message.output})`;
            addMessage(formattedMessage);
        }
    });
})
.catch(error => {
    console.error('Error fetching messages:', error);
});

// Websocket handling
var socket = io();
socket.on('connect', function() {
    socket.emit('my event', {data: 'I\'m connected!'});
});

// Handle form submission
$('#message_form').submit(function(event) {
    event.preventDefault(); // Prevent default form submission behavior

    // Get the message from the input field
    var message = $('#body_text').val().trim();

    // Check if the message is not empty
    if (message !== '') {
        // Send the message to the server via WebSocket
        socket.emit('chat_message', message);

        // Clear the input field
        $('#body_text').val('');
    }
});

// Handle dice submission
$('#dice_form').submit(function(event) {
    event.preventDefault(); // Prevent default form submission behavior

    // Get the message from the input field
    var message = $('#dice_text').val().trim();

    // Check if the message is not empty
    if (message !== '') {
        // Send the message to the server via WebSocket
        socket.emit('dice_message', message);

        // Clear the input field
        $('#dice_text').val('');
    }
});

// Function to add a new message to the list
function addMessage(message) {
    $('#messages').append($('<li>').text(message));
}

// Receive messages from server
socket.on('message', function(message) {
    if (message.type === 'text') {
        // Extract username and body
        const formattedMessage = `${message.username}: ${message.body}`;
        addMessage(formattedMessage);
    } else if (message.type === 'dice') {
        // Extract username, input, output, and total
        const formattedMessage = `${message.username} rolled ${message.input} and got ${message.total} (${message.output})`;
        addMessage(formattedMessage);
    }
});