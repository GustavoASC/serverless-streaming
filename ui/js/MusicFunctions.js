
const MUSIC_URL = 'http://192.168.10.247:8080/function/crud/';

function loadMusicData() {
    const result = get(MUSIC_URL);
    if (result) {
        var parsed_result = JSON.parse(result);
        return parsed_result;
    }
    return "";
};


function get(targetUrl) {
    var request = new XMLHttpRequest();
    request.open("GET", targetUrl, false);
    request.send();
    return request.responseText;
}

function playMusic(id) {
    var video = document.getElementById('video');
    var videoSrc = 'http://192.168.10.247:8080/function/streaming/' + id + '/outputlist.m3u8';
    //
    // First check for native browser HLS support
    //
    if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = videoSrc;
        //
        // If no native HLS support, check if HLS.js is supported
        //
    } else if (Hls.isSupported()) {
        var hls = new Hls();
        hls.loadSource(videoSrc);
        hls.attachMedia(video);
    }
    video.play()
}