
const MUSIC_URL = 'http://192.168.10.247:8080/function/crud/';

function LoadMusicData() {
    const result = Get(MUSIC_URL);
    if (result) {
        var parsed_result = JSON.parse(result);
        return parsed_result;
    }
    return "";
};


function Get(targetUrl) {
    var Httpreq = new XMLHttpRequest();
    Httpreq.open("GET", targetUrl, false);
    Httpreq.send();
    return Httpreq.responseText;
}
