// Load existing messages
fetch('/posts')
.then(response => response.json())
    .then(data => {
        // Function to add a new message to the list
        function addMessage(message) {
            const listItem = document.createElement('li');
            listItem.className = "messageDiv";

            // Create a message container div
            const messageContainer = document.createElement('div');
            messageContainer.className = 'message-container';

            const profilePic = document.createElement('img');

            // Add a profile pic right next to the message
            if (message.profile_pic) {

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
                // Create a text node for the message content by extracting the username and the message content
                const usernameText = document.createTextNode(`${message.username}`);

                // Creating a span elements so I can add a class
                const usernameSpanElement = document.createElement('span');
                usernameSpanElement.appendChild(usernameText);
                usernameSpanElement.className = "username";


                const messageText = document.createTextNode(`${message.body}`);
                const messageSpanElement = document.createElement('span');
                messageSpanElement.appendChild(messageText);
                messageSpanElement.className = "message-body";

                messageContainer.append(profilePic);
                messageContainer.append(usernameSpanElement);
                messageContainer.append(messageSpanElement);

                listItem.appendChild(messageContainer);
            }

            else if (message.type == 'dice'){
                // Create a text node for the message content by extracting the username, input, output, and total
                const usernameText = document.createTextNode(`${message.username} `);

                // Create a span element so I can add a class
                const usernameSpanElement = document.createElement('span');
                usernameSpanElement.appendChild(usernameText);
                usernameSpanElement.className = "username";


                const messageResultText = document.createTextNode(` Rolled ${message.input} and got ${message.total} ${message.output}`);
                const messageSpanElement = document.createElement('span');
                messageSpanElement.appendChild(messageResultText);
                messageSpanElement.className = "message-body";

                messageContainer.append(profilePic);
                messageContainer.append(usernameSpanElement);
                messageContainer.append(messageSpanElement);

                listItem.appendChild(messageContainer);
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
    console.log(message);

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
    console.log(message);

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
    listItem.className = "messageDiv";

    // Create a message container div
    const messageContainer = document.createElement('div');
    messageContainer.className = 'message-container';

    const profilePic = document.createElement('img');

    if (message.profile_pic != "./images/TEST_SniperDecoy.png"){
        profilePic.src = "./uploads/" + message.profile_pic;
    }
    else {
        profilePic.src = message.profile_pic;
    }

    profilePic.alt = 'Profile Picture';
    profilePic.className = 'profile-pic';


    if (message.type === 'text'){
        // Create a text node for the message content by extracting the username and the message content
        const usernameText = document.createTextNode(`${message.username}`);

        // Creating a span elements so I can add a class
        const usernameSpanElement = document.createElement('span');
        usernameSpanElement.appendChild(usernameText);
        usernameSpanElement.className = "username";


        const messageText = document.createTextNode(`${message.body}`);
        const messageSpanElement = document.createElement('span');
        messageSpanElement.appendChild(messageText);
        messageSpanElement.className = "message-body";

        messageContainer.append(profilePic);
        messageContainer.append(usernameSpanElement);
        messageContainer.append(messageSpanElement);

        listItem.appendChild(messageContainer);
    }

    else if (message.type == 'dice'){
        // Create a text node for the message content by extracting the username, input, output, and total
        const usernameText = document.createTextNode(`${message.username} `);

        // Create a span element so I can add a class
        const usernameSpanElement = document.createElement('span');
        usernameSpanElement.appendChild(usernameText);
        usernameSpanElement.className = "username";


        const messageResultText = document.createTextNode(` Rolled ${message.input} and got ${message.total} ${message.output}`);
        const messageSpanElement = document.createElement('span');
        messageSpanElement.appendChild(messageResultText);
        messageSpanElement.className = "message-body";

        messageContainer.append(profilePic);
        messageContainer.append(usernameSpanElement);
        messageContainer.append(messageSpanElement);

        listItem.appendChild(messageContainer);
    }

    document.getElementById('messages').appendChild(listItem);

    const chatMessageContainer = document.getElementById("messages");
    chatMessagesContainer.scrollTop = chatMessages.scrollHeight;
}


// Receive messages from server
socket.on('message', function(message) {
    console.log(message);
    addMessage(message);
});