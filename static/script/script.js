let socket;
let isJoining = false;

function initializeWebSocket() {
  if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
    return;
  }

  socket = new WebSocket('ws://localhost:8000/messages/message');

  socket.onopen = function () {
    console.log('WebSocket connection established.');
  };

  socket.onmessage = function (event) {
    const data = JSON.parse(event.data);

    if (!data.username || !data.data || !data.time) {
      console.warn("Incomplete message data received, skipping:", data);
      return;
  }
    const msgClass = data.isMe ? 'user-message' : 'other-message';
    const sender = data.isMe ? 'You' : data.username;
    const message = data.data;
    const time = data.time;

    const messageElement = $('<li>').addClass('clearfix');
    messageElement.append($('<div>').addClass(msgClass).text(`[${time}] ${sender}: ${message}`));
    $('#messages').append(messageElement);
    $('#chat').scrollTop($('#chat')[0].scrollHeight);
  };

  socket.onerror = function () {
    console.error('WebSocket encountered an error.');
    if (socket.readyState === WebSocket.CLOSED) {
      showJoinModal();
    }
  };

  socket.onclose = function (event) {
    console.log('WebSocket closed:', event.code);
    if (!isJoining) {
      showJoinModal();
    }
  };
}

function showJoinModal() {
  $('#username-form').show();
  $('#chat').hide();
  $('#message-input').hide();
  $('#usernameModal').modal('show');
}

// Show the modal when the page loads
$('#open-modal').click(showJoinModal);

// Handle the join button click
$('#join').click(function () {
  const username = $('#usernameInput').val().trim();
  if (username) {
    isJoining = true;
    initializeWebSocket();
    $('#username-form').hide();
    $('#chat').show();
    $('#message-input').show();
    isJoining = false;
  } else {
    alert("Please enter a valid username.");
  }
});

// Attach event listener to "Send" button
$('#send').off('click').on('click', sendMessage);

// Enable "Enter" key to send message
$('#message').keydown(function (event) {
  if (event.key === "Enter") {
    sendMessage();
  }
});

function sendMessage() {
  const message = $('#message').val().trim();
  const username = $('#usernameInput').val().trim();
  
  // Set sender_id and receiver_id for testing; these should be dynamically set in a real app
  const senderId = 1;  // Replace with actual sender ID
  const receiverId = 2; // Replace with actual receiver ID
  
  if (message && username && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({
      "message": message,
      "username": username,
      "sender_id": senderId,
      "receiver_id": receiverId
    }));
    $('#message').val(''); // Clear the input after sending
  } else {
    console.error("Message could not be sent. Either the WebSocket is not open or required fields are missing.");
  }
}
