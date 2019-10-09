
document.addEventListener('DOMContentLoaded', () => {
  // Connect to websocket
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  socket.on('connect', () => {

    // Each button should emit a "submit message" event
    button = document.querySelector('#submitMessage');
      button.onclick = () => {
        const message = document.querySelector('#messageInput').value;
        socket.emit('submit message', {'message': message});
      };

      // emit 'join' when the user enters the join_room
          socket.emit('joined');
          currentChannel = document.querySelector('#span').innerText;
          localStorage.setItem('currentChannel', currentChannel);

     // emit 'leave' when user clicks the leave dropdownMenuButton
     leaveButton = document.querySelector('#leaveChannel');
       leaveButton.onclick = () => {
         socket.emit('left');
         localStorage.removeItem('currentChannel');
         window.location.replace('/');
       };

       // when user clicks on create channel or the Flack logo or logout, remove local storage in each case
       document.querySelector('#flack').onclick = () => {
         if (localStorage.getItem('currentChannel')) {
             localStorage.removeItem('currentChannel');
             window.location.replace('/');
             console.log("reached the redirect");
         };
       };

       document.querySelector('#create').onclick = () => {
         if (localStorage.getItem('currentChannel')) {
            localStorage.removeItem('currentChannel');
            window.location.replace('/');
            console.log("reached the redirect");
         };
       };

       document.querySelector('#logout').onclick = () => {
         if (localStorage.getItem('currentChannel')) {
            localStorage.removeItem('currentChannel');
            window.location.replace('/');
            console.log("reached the redirect");
         };
       };

      // lets user press enter as well as submit
      document.querySelector('#messageInput').addEventListener("keydown", event => {
    if (event.key == "Enter" && document.querySelector('#messageInput').value != "") {
        document.querySelector("#submitMessage").click();
    };
});

  });

  // This receives what the server broadcasts outwards
  socket.on('broadcast message', data => {
    document.querySelector('#ListOfMessages').append(`${data.author} at ${data.timestamp}: ${data.message}\n`);
    // as soon as this is done, clear the text area
    document.querySelector('#messageInput').value = '';
  });

  // implement functionality that writes in chat when a user joins a room
  socket.on('joined', data => {
    document.querySelector('#ListOfMessages').append(`${data.author} has entered the room.\n`);
  });

  // implement functionality that emits something when a user leaves a room here
  socket.on('left', data => {
    document.querySelector('#ListOfMessages').append(`${data.author} has left the room.\n`);
  });


 });
