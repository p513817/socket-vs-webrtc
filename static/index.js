
const URL = `${SCRIPT_ROOT}/stream`;
const IMG_EVENT = "images";

const img = document.getElementById('img');

const socketButton = document.getElementById("socketButton");
const intervalTime = 1/30*1000;

let temp_msg = "";
let frame_idx = 0;

const socketStream = new WebSocket('ws://' + location.host + '/stream');

$(document).ready(async function () {

    socketStream.addEventListener('message', ev => {
        let data = JSON.parse(ev.data);
        img.src = "data:image/jpeg;base64," + data["images"];
    });

    socketStream.addEventListener('close', ev => {
        console.log('The connection has been closed successfully.');
    });

    document.getElementById('webrtc-video').controls = false;

});

function getTaskFrame() {
    try { 
        socketStream.send('{ "task": "TASK"}');
    } catch(e) { 
        console.log(e);
    }
}

async function startSocketStream() {
    
    let url = `/socket/start/`
    const data = await getAPI(url);
    if (! data) return undefined;
    
    console.log(data);
    window.setInterval(getTaskFrame, intervalTime);
}

async function startRTSPStream() {
    
    let url = `/rtsp/start/`
    const data = await getAPI(url);
    if (! data) return undefined;
    console.log(data);
}

async function stopSocketStream() {

    let url = `/socket/stop/`
    const data = await getAPI(url);
    if (! data) return undefined;
    console.log(data);
}

async function stopRTSPStream() {
    let url = `/rtsp/stop/`
    const data = await getAPI(url);
    if (! data) return undefined;
    console.log(data);

}
