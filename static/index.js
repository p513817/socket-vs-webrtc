
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

    getListHandler();

    document.getElementById("source-type").addEventListener("change", sourceControlEvent)

});


function getTaskFrame() {
    try { 
        socketStream.send('{ "task": "TASK"}');
    } catch(e) { 
        console.log(e);
    }
}

async function startSocketStream() {
    
    const streamID = document.getElementById("stream-list").value;
    const url = `/socket/${streamID}/start/`
    
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

async function getListHandler(){
    // getSourceList();
    getStreamList();
}

async function getSourceList(){

    let url = `/sources`
    let data = await getAPI(url, LOG, true);
    if(!data) return undefined;

    console.log(data);

    const steamList = document.getElementById("stream-list");
    steamList.innerHTML = "";

    for ( let i=0; i<data.length; i++){
        var option = document.createElement("option");
        option.value = data[i];
        option.text = data[i];
        steamList.appendChild(option);
    }
}

async function getStreamList(){
    let url;
    url = "http://demo:demo@127.0.0.1:8083/streams";
    url = "http://172.16.92.130:8083/streams"

    const steamList = document.getElementById("stream-list");

    let data = await getAPI( url, LOG, true, "demo:demo");
    if(!data) return undefined;

    steamList.innerHTML = "";
    data = data["payload"];
    for ( const key in data ){
        console.log(key, data[key]);
        var option = document.createElement("option");
        option.value = key;
        option.text = key;
        steamList.appendChild(option);
    }

}

async function delStream(streamID){
    
    if(!streamID) { alert("Unknown streamID ... " ); return undefined; };

    let url = `http://172.16.92.130:8083/stream/${streamID}/delete`;

    let data = await getAPI( url, LOG, false, "demo:demo");
    if(!data) return undefined;
    console.log(data);
    getStreamList();
}

async function addStream(streamID, streamURL){
    let api;

    // Create RTSP
    // api = `/rtsp/start`
    // let runRTSPData = await getAPI( api, LOG, true, "demo:demo" );
    // if(!runRTSPData) return undefined;
    // console.log(runRTSPData);

    // Create WebRTC
    if(!streamID) streamID = document.getElementById("rtsp-name").value;
    if(!streamURL) { alert("Unkown Stream URL"); return undefined; }

    api = `http://172.16.92.130:8083/stream/${streamID}/add`;

    let inData =  {
        "name": streamID,
        "channels": {
            "0": {
                "name": "ch1",
                "url": streamURL,
                "on_demand": false,
                "debug": false,
                "status": 0
            }
        }
    }

    let runRtcData = await postAPI( api, inData, JSON_FMT, LOG, true, "demo:demo");
    if(!runRtcData) return undefined;
    console.log(runRtcData);
    getStreamList();

}

async function sourceControlEvent(event){
    sourceElementHandler(this.value);
}

async function sourceElementHandler(intype){

    let sourceEleList = [ 'source-v4l2-div', 'source-rtsp-div', 'source-file-div' ];

    for(let i=0; i<sourceEleList.length; i++){
        const srcName   = sourceEleList[i];
        const srcEle    = document.getElementById(srcName);
        let displayKey  = "none";

        if( srcName.includes(intype.toLowerCase()) ){
            console.log(`Select ${srcName}`);
            await sourceEvent(intype);
            displayKey = "block";
        }
        srcEle.style = `display: ${displayKey}`;
    }

}

async function sourceEvent(intype){
    if( intype.toLowerCase() === "v4l2" ){
        const data = await getAPI('/get_v4l2');
        if(!data) return undefined;
        console.log(data);

        const trgList = document.getElementById(`source-v4l2`);
        trgList.innerHTML = "";
        for(let i=0; i<data.length; i++){
            var option = document.createElement("option")
            option.value    = data[i];
            option.text     = data[i];
            trgList.appendChild(option);
        }
    }
}

async function addSrc(){

    console.log("Add Source");

    const addSrcAPI       = "/src/add";
    const inName    = document.getElementById("source-name").value;
    const inType    = document.getElementById("source-type").value;
    let sendType = JSON_FMT;
    let inSrc = document.getElementById(`source-${inType.toLowerCase()}`).value;

    if ( inType.toLowerCase() === "file" ) {
        inSrc = document.getElementById(`source-${inType.toLowerCase()}`).files[0];
        sendType = FORM_FMT
    }
    
    const inData = {
        "name"      : inName,
        "type"      : inType,
        "source"    : inSrc
    }

    let formData = new FormData()
    for ( let key in inData ) {
        console.log(key, inData[key]);
        formData.append(key, inData[key]);
    }
    console.log("Finish Form Data");
    
    // Create Source
    let createSrcResp = await postAPI( addSrcAPI, formData, FORM_FMT, LOG, true, "demo:demo");
    if(!createSrcResp) return undefined;
    console.log(createSrcResp);

    // Start Source and Enable RTSP
    const startRtspAPI = `/src/${inName}/start/`;
    let startRtspResp = await getAPI( startRtspAPI, JSON_FMT, LOG, true, "demo:demo");
    if(!startRtspResp) return undefined;
    console.log(startRtspResp);
    
    console.log("Add WebRTC");
    await addStream( startRtspResp['id'], startRtspResp['url'] );
    await getStreamList();
}

async function delSrc(){
    console.log("Delete Source");
    const inName    = document.getElementById("source-name").value;
    delStream(inName);

    // Stop the source
    const stopSrcAPI = `/src/${inName}/stop/`;
    let stopRtspResp = await getAPI( stopSrcAPI, JSON_FMT, LOG, true, "demo:demo");
    if(!stopRtspResp) return undefined;
    console.log(stopRtspResp);

    await getStreamList();
}