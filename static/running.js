const socket_img = new WebSocket('ws://' + location.host + '/image');
console.log("connected ws")
socket_img.addEventListener('message', ev => {
    msg = JSON.parse(ev.data);
    var pic = document.getElementById('refresh_img');
    // console.log(msg.img_src);
    pic.src = msg.img_src;
});

const socket_progress = new WebSocket('ws://' + location.host + '/progress');
console.log("connected ws")
socket_progress.addEventListener('message', ev => {
    msg = JSON.parse(ev.data);
    console.log(msg.progress)
    var progress_bar = document.getElementById('progress-bar-fill');
    progress_bar.style = "width:" + msg.progress + ";";

    var success = document.getElementById('wrapper-success')
    if (msg.progress.includes('100')){
        success.style.display = 'block'; // show the section
    }
    else {
        success.style.display = 'none'; // hide the section
    }
});