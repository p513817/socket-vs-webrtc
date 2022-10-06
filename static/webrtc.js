// Create P2P Service
let webrtc;

const videoEl = document.querySelector('#webrtc-video')

function connectStream() {

    console.log("Start to connect WebRTC");

    // Create RTCPeerConnection
    console.log("Create Peer Connection");
    webrtc = new RTCPeerConnection({
        iceServers: [{
            urls: ['stun:stun.l.google.com:19302']
        }],
        sdpSemantics: 'unified-plan'
    })

    // Check URL
    let trg_url;
    let streamID = document.getElementById('stream-list').value;
    trg_url = `http://172.16.92.130:8083/stream/${streamID}/channel/0/webrtc`;
    console.log(`Get URL: ${trg_url}`);

    // ontrack
    // 完成連線後，透過該事件能夠在發現遠端傳輸的多媒體檔案時觸發，來處理/接收多媒體數據。
    console.log("Define Track Event");
    webrtc.ontrack = function (event) {
        console.log(event.streams.length + ' track is delivered')
        videoEl.srcObject = event.streams[0]
        videoEl.play()
    }

    // Add Transceiver to capture the video
    /* About Transceiver
        Reference   : https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/addTransceiver
        Example     : rtpTransceiver = RTCPeerConnection.addTransceiver(trackOrKind, init);
    */
    console.log("Add Transceiver");
    webrtc.addTransceiver('video', { 'direction': 'sendrecv' })

    // onnegotiationneeded
    // 每當 RTCPeerConnection 要進行會話溝通(連線)時，第一次也就是在addTrack後會觸發該事件， 通常會在此處理createOffer，來通知remote peer與我們連線。
    console.log("Define Negotiation");
    webrtc.onnegotiationneeded = async function handleNegotiationNeeded() {

        const offer = await webrtc.createOffer()

        await webrtc.setLocalDescription(offer)

        $.post(trg_url, {
            data: btoa(webrtc.localDescription.sdp)
        }, function (data) {
            try {
                webrtc.setRemoteDescription(
                    new RTCSessionDescription({
                        type: 'answer',
                        sdp: atob(data)
                    })
                )
            } catch (e) {
                console.warn(e);
            }
        })
    }

    // 建立 P2P 中雙向資料傳輸的通道
    console.log("Create Data Channel");
    const webrtcSendChannel = webrtc.createDataChannel('rtsptowebSendChannel')

    // 當兩邊資料都對接上的時候會執行這個動作
    webrtcSendChannel.onopen = (event) => {
        console.log(`${webrtcSendChannel.label} has opened`)
        webrtcSendChannel.send('ping')
    }
    // 當呼叫 close() method 的時候
    webrtcSendChannel.onclose = (_event) => {
        console.log(`${webrtcSendChannel.label} has closed`);
        // startPlay(videoEl, url)
    }
    // 呼叫 send() 並且兩邊都連接上的時候
    webrtcSendChannel.onmessage = event => console.log(event.data)
}

function startStream() {
    document.getElementById('webrtc-video').controls = true;
    console.log("Start Video");
    videoEl.play();
}

function pauseStream() {
    console.log("Pause Video");
    videoEl.pause();
}

function stopStream() {
    console.log("Stop Stream");
    videoEl.pause();
    webrtc.close();
}
