// Load existing messages
fetch('/posts')
.then(response => response.json())
    .then(data => {
        // Function to add a new message to the list
        function addMessage(message) {
            const listItem = document.createElement('li');

            // Add a profile pic right next to the message
            if (message.profile_pic) {
                const profilePic = document.createElement('img');

                if (message.profile_pic != "./images/TEST_SniperDecoy.png"){
                    profilePic.src = "./uploads/" + message.profile_pic;
                }
                else {
                    profilePic.src = message.profile_pic;
                }

                profilePic.alt = 'Profile Picture';
                profilePic.className = 'profile-pic';
                listItem.appendChild(profilePic);
            }

            if (message.type === 'text'){
                    // Create a text node for the message content by extracting the profile pic, username, and the message content
                    const messageText = document.createTextNode(`${message.username}: ${message.body}`);
                    listItem.appendChild(messageText);
            }

            else if (message.type == 'dice'){
                // Create a text node for the message content by extracting the profile pic, username, input, output, and total
                const messageText = document.createTextNode(`${message.profile_pic} ${message.username} rolled ${message.input} and got ${message.total} ${message.output}`);
                listItem.appendChild(messageText);
            }

            document.getElementById('messages').appendChild(listItem);
        }

        // Loop through each message in the list
        data.forEach(message => {
            addMessage(message);
        })
    }).catch(error => {
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
    //  Create a unordered list with first contains a img tag follow by the message content
    const listItem = document.createElement('li');
    const profilePic = document.createElement('img');
    if (message.profile_pic != "./images/TEST_SniperDecoy.png"){
        profilePic.src = "./uploads/" + message.profile_pic;
    }
    else {
        profilePic.src = message.profile_pic;

    }
    profilePic.alt = 'Profile Picture';
    profilePic.className = 'profile-pic';
    listItem.appendChild(profilePic);

    if (message.type === 'text'){
        // Create a text node for the message content by extracting the profile pic, username, and the message content
        const messageText = document.createTextNode(`${message.username}: ${message.body}`);
        listItem.appendChild(messageText);
    }

    else if (message.type == 'dice'){
        // Create a text node for the message content by extracting the profile pic, username, input, output, and total
        const messageText = document.createTextNode(`${message.profile_pic} ${message.username} rolled ${message.input} and got ${message.total} ${message.output}`);
        listItem.appendChild(messageText);
    }

    document.getElementById('messages').appendChild(listItem);
}


// Receive messages from server
socket.on('message', function(message) {
    addMessage(message);
});