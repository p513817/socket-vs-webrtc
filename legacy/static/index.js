const DOMAIN = "172.16.92.130";
const PORT = "4444";
const IMG_EVENT = "images";
const URL = `http://${DOMAIN}:${PORT}/stream`;

const img = document.getElementById('img');

const socketButton = document.getElementById("socketButton");
const rtspButton = document.getElementById("rtspButton");
const intervalTime = 1/30*1000;

let temp_msg = "";
let frame_idx = 0;

// streamSocket.on(IMG_EVENT, function (msg) {
//     frame_idx = frame_idx + 1;
//     img.src = "data:image/jpeg;base64," + msg;

//     // document.querySelector('#fullpage').style.backgroundImage = 'url(' + img.src + ')';
// });
const socket = new WebSocket('ws://' + location.host + '/echo');
const socketStream = new WebSocket('ws://' + location.host + '/stream');

$(document).ready(async function () {

    // const log = (text, color) => {
    //     document.getElementById('log').innerHTML += `<span style="color: ${color}">${text}</span><br>`;
    // };

    // socket.addEventListener('message', ev => {
    //     log('<<< ' + ev.data, 'blue');
    // });

    socketStream.addEventListener('message', ev => {
        let data = JSON.parse(ev.data);
        // log('<<< ' + data["images"], 'blue');
        img.src = "data:image/jpeg;base64," + data["images"];
    });

    // document.getElementById('form').onsubmit = ev => {
    //     ev.preventDefault();
    //     const textField = document.getElementById('text');
    //     log('>>> ' + textField.value, 'red');
    //     socket.send(textField.value);
    //     textField.value = '';
    // };


});

function getTaskFrame() {
    try { 
        socketStream.send('{ "task": "TASK"}');
    } catch(e) { 
        console.log(e);
    }
}

function startSocketStream() {
    
    $.ajax({
        url: `http://${DOMAIN}:${PORT}/socket/start/`,
        type: "GET",
        dataType: "json",
        success: function (data, textStatus, xhr) {
            console.log(data);
        },
        error: function (err) {
            console.log(err);
        },
    });

    window.setInterval(getTaskFrame, intervalTime);
}

async function startRTSPStream() {

    // document.getElementById("videoElem").style.display = 'block';

    // $('#' + suuid).addClass('active');
    // getCodecInfo();

    await $.ajax({
        url: `http://${DOMAIN}:${PORT}/rtsp/start/`,
        type: "GET",
        dataType: "json",
        success: function (data, textStatus, xhr) {
            console.log(data);     
            console.log("Start Stream");

        },
        error: function (err) {
            console.log(err);
        },
    });

    
}

function stopSocketStream() {
    $.ajax({
        url: `http://${DOMAIN}:${PORT}/socket/stop/`,
        type: "GET",
        dataType: "json",
        success: function (data, textStatus, xhr) {
            console.log(data);
        },
        error: function (err) {
            console.log(err);
        },
    });
}

function stopRTSPStream() {
    console.log("Stop");
    $.ajax({
        url: `http://${DOMAIN}:${PORT}/rtsp/stop/`,
        type: "GET",
        dataType: "json",
        success: function (data, textStatus, xhr) {
            console.log(data);
        },
        error: function (err) {
            console.log(err);
        },
    });
}

// --------------------------------------
// RTSP


