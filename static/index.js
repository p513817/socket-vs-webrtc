
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

    getStreamList();

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

function getStreamList(){
    let url;
    url = "http://demo:demo@127.0.0.1:8083/streams";
    url = "http://172.16.92.130:8083/streams"

    const steamList = document.getElementById("stream-list");

    $.ajax({
        url:url,
        type:'GET',
        beforeSend: function (xhr) {
            xhr.setRequestHeader ("Authorization", "Basic " + btoa('demo' + ":" + 'demo'));
        },        
        success: function(data){

            steamList.innerHTML = "";
            
            data = data["payload"]
            for ( const key in data ){
                console.log(key, data[key]);
                var option = document.createElement("option");
                option.value = key;
                option.text = key;
                steamList.appendChild(option);
            }
        }
    })
}

function delStream(){
    let url;
    let streamID;

    streamID = document.getElementById("rtsp-name").value;
    url = `http://172.16.92.130:8083/stream/${streamID}/delete`

    $.ajax({
        url:url,
        type:'GET',
        beforeSend: function (xhr) {
            xhr.setRequestHeader ("Authorization", "Basic " + btoa('demo' + ":" + 'demo'));
        },        
        success: function(data){
            console.log(data);
            getStreamList();
        }
    })
}

function addStream(){
    let url;
    let streamID;
    let streamRTSP;
    
    streamID = document.getElementById("rtsp-name").value;
    streamRTSP = document.getElementById("rtsp-url").value;

    url = `http://172.16.92.130:8083/stream/${streamID}/add`;

    let inData =  {
        "name": "custom video",
        "channels": {
            "0": {
                "name": "ch1",
                "url": streamRTSP,
                "on_demand": false,
                "debug": false,
                "status": 0
            }
        }
    }

    $.ajax({
        url:url,
        type:'POST',
        data: JSON.stringify(inData),
        dataType: "json",
        contentType: "application/json;charset=utf-8",
        beforeSend: function (xhr) {
            xhr.setRequestHeader ("Authorization", "Basic " + btoa('demo' + ":" + 'demo'));
        },        
        success: function(data){
            console.log(data);
            getStreamList();
        }
    })
}