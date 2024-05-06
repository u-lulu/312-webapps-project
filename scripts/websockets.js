// Websocket handling
var socket = io();
socket.on('connect', function() {
    socket.emit('my event', {data: 'I\'m connected!'});
});

// Receive messages from server
socket.on('message', function(message) {
    console.log(message);
    addMessage(message);
});

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

            // Format the expiration date
            const messageDate = new Date(message.expiration_date);
            const boldTextExpireElement = document.createElement('span');
            const countdownId = 'expires-body_' + message.uuid;
            if (message.expiration_date){
                boldTextExpireElement.style.fontWeight = 'bold';
                boldTextExpireElement.id = countdownId;
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
                messageContainer.append(boldTextExpireElement);
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
                messageContainer.append(boldTextExpireElement);
                listItem.appendChild(messageContainer);
            }

            document.getElementById('messages').appendChild(listItem);
            updateCountdown(messageDate, countdownId);
        }

        // Loop through each message in the list
        data.forEach(message => {
            addMessage(message);
        })
    }).catch(error => {
    console.error('Error fetching messages:', error);
});

// Handle form submission
$('#message_form').submit(function(event) {
    event.preventDefault(); // Prevent default form submission behavior

    // Get the message from the input field
    var message = $('#body_text').val().trim();
    var expires = $('#display_duration').val();
    var expiresDate = Date(expires.expiration_date)
    console.log("Message created at " + expiresDate.toLocaleString());

    // Check if the message is not empty
    if (message !== '') {
        // Send the message and expiration date to the server via WebSocket
        socket.emit('chat_message', {text: message, date: expires});

        // Clear the input field
        $('#body_text').val('');
        $('#display_duration').val('');
    }
});


// Handle dice submission
$('#dice_form').submit(function(event) {
    event.preventDefault(); // Prevent default form submission behavior

    // Get the message and expiration date from the input field
    var message = $('#dice_text').val().trim();
    var expires = $('#display_durations').val();
    var expiresDate = Date(expires.expiration_date)
    console.log("Message created at " + expiresDate.toLocaleString());

    // Check if the message is not empty
    if (message !== '') {
        // Send the message to the server via WebSocket
        socket.emit('dice_message', {text: message, date: expires});
        // Clear the input field
        $('#dice_text').val('');
        $('#display_durations').val('');
    }
});


// Function to add a new message to the list
function addMessage(message) {
    // Create a unique id for the message element
    const messageId = message.uuid;
    //  Create a unordered list with first contains a img tag follow by the message content
    const listItem = document.createElement('li');
    listItem.className = "messageDiv";
    listItem.id = messageId; // Set the unique id for the message element

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

    // Format the expiration date
    const messageDate = new Date(message.expiration_date);
    const countdownId = 'expires-body_' + message.uuid;
    const boldTextExpireElement = document.createElement('span');
    if (message.expiration_date) {
        boldTextExpireElement.style.fontWeight = 'bold';
        boldTextExpireElement.id = countdownId;
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
        messageContainer.append(boldTextExpireElement);
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
        messageContainer.append(boldTextExpireElement);
        listItem.appendChild(messageContainer);
    }

    document.getElementById('messages').appendChild(listItem);
    updateCountdown(messageDate, countdownId);


    const chatMessageContainer = document.getElementById("left-container");
    chatMessageContainer.scrollTop = chatMessageContainer.scrollHeight;
}

// Function to update the countdown timer
function updateCountdown(expirationTime, messageId) {
    var currentTime = new Date();

    var countdownElement = document.getElementById(messageId);

    if (countdownElement) {
    // Calculate the remaining time until expiration
        var remainingTime = expirationTime - currentTime;

        // Convert remaining time to seconds
        var seconds = Math.floor((remainingTime / 1000) % 60);
        var minutes = Math.floor((remainingTime / 1000 / 60) % 60);
        var hours = Math.floor((remainingTime / (1000 * 60 * 60)) % 24);
        var days = Math.floor(remainingTime / (1000 * 60 * 60 * 24));

        // Format the countdown timer
        var countdownText = '';
        if (days >= 1) {
            countdownText += days + 'd ' + hours + 'h ' + minutes + 'm ' + seconds + 's';
        }
        if (days < 0 && hours >= 1){
            countdownText += hours + 'h ' + minutes + 'm ' + seconds + 's';
        }
        if (hours <= 1) {
            countdownText += minutes + 'm ' + seconds + 's';
        }
        if (minutes <= 1) {
            countdownText += seconds + 's'
        }
        if (seconds < 0) {
            countdownText = ''
        }

        // Update the innerHTML of the countdown element
        countdownElement.innerHTML = countdownText;
    }

    // Update the countdown timer every second
    setTimeout(function() {
        updateCountdown(expirationTime, messageId);
    }, 1000);
}