var videoid = '';
var watchTime = 0;
var setT = null;
function loadedHandler() {
    if (CKobject.getObjectById('ckplayer_a1').getType()) {
        CKobject.getObjectById('ckplayer_a1').addListener('paused', pausedHandler);
        CKobject.getObjectById('ckplayer_a1').addListener('ended', endHandler);
        CKobject.getObjectById('ckplayer_a1').addListener('play', playHandler);
    }
    else {
        CKobject.getObjectById('ckplayer_a1').addListener('paused', 'pausedHandler');
        CKobject.getObjectById('ckplayer_a1').addListener('ended', "endHandler");
        CKobject.getObjectById('ckplayer_a1').addListener('play', "playHandler");
    }
}

function playHandler(b) {
    //$("#llltest").html($("#llltest").html()+"　playHandler");
}


function pausedHandler(b) {
    if (setT) {
        window.clearInterval(setT);
    }
    if (!b) {
        setT = window.setInterval(setFunction, 1000);
    }
}
function endHandler(b) {
    //alert(CKobject.getObjectById('ckplayer_a1').getStatus().totalTime);
    //if (getCookie("watchTime")==null)
    //{
    //	return;	
    //}
    if (watchTime == null) {
        return;
    }
    $("#nyv").val(watchTime);
    $("#iptflag").val("0");
    //alert("endHandler:"+$("#vform\\:nyv").val());
    clearwt();
    rc();
    $("#btnsavexs").attr("disabled", "disabled");
    CKobject.getObjectById('ckplayer_a1').videoClear();
    //CKobject.getObjectById('ckplayer_a1').changeFace();
}
function setFunction() {
    watchTime += 1;
    //SetCookie("watchTime",$("#ouid").val() + '#' + videoid + '#' + $("#btime").val() + '#' + getDateTime(new Date()) + '#' + watchTime + '#' + CKobject.getObjectById('ckplayer_a1').getStatus().time);
    SetCookie("watchTime", watchTime);
    //CKobject._K_('nowTime').innerHTML='当前观看时间：'+watchTime+"  t:" + getCookie("watchTime");
    CKobject._K_('nowTime').innerHTML = '当前观看时间：' + watchTime;
}
function SetCookie(name, value) {
    var Days = 30; //此 cookie 将被保存 30 天
    var exp = new Date(); //new Date("December 31, 9998");
    exp.setTime(exp.getTime() + Days * 24 * 60 * 60 * 1000);
    document.cookie = name + "=" + escape(value) + ";expires=" + exp.toGMTString();
}
function getCookie(name) {
    var arr = document.cookie.match(new RegExp("(^| )" + name + "=([^;]*)(;|$)"));
    if (arr != null) return unescape(arr[2]); return null;
}
function checkold() {
    if (getCookie("watchTime") != null) {
        //$("#vform\\:oyv").val(getCookie("watchTime"));
        //$("#vform\\:iptflag").val("1");
        //alert("checkold:"+$("#vform\\:oyv").val());
        clearwt();
        //rc();
        //$("#llltest").html($("#llltest").html()+"　checkold");
    }
}

function clearwt() {
    SetCookie("watchTime", null);
    watchTime = null;
    $("#llltest").html($("#llltest").html() + "　clearwt");
}

var lsflagpause = false;
function lspause() {
    CKobject.getObjectById('ckplayer_a1').videoPause();
    lsflagpause = true;
    $("#nyv").val(getCookie("watchTime"));
    $("#iptflag").val("0");
    $("#btnsavexs").attr("disabled", "disabled");
    clearwt();
}

function videochange(kjfid) {
    lsflagpause = false;
    checkold();
    clearwt();

    videoid = kjfid;
    $("#vid").val(videoid);
    var bcfid;

    //alert(getCookie("watchTime"));
    rcplay();
    $("#llltest").html($("#llltest").html() + "　change");
}

function rcplay() {
    $.ajax({
        url: "/student/videoInfo!videoStudyBegin.action",
        type: "post",
        data: { vid: videoid },
        dataType: "json",
        cache: false,
        async: false,
        success: function (data) {
            //var cToObj=eval("("+data+")");
            //alert(data.kjurl); 
            $("#fdt").val(data.fourTime);
            $("#fsy").val(data.allTime);
            $("#btime").val(data.pxkssj);
            if (data.fourTime == "-1") {
                alert("您当天已经学满4小时，本次视频将不计入学时");
            }
            if (data.fourTime == "1") {
                alert("您已经学满24小时，本次视频将不计入学时");
            }
            $("#llltest").html(data.kjurl);
            var flashvars = {
                f: data.kjurl + ".flv",//'http://192.168.0.108:9999/video/2.flv',
                //f:'http://192.168.0.109/a.flv',
                c: 0,
                p: 1,
                g: 0,
                b: 0,
                h: 4,
                wh: '1080:720',
                //i:'/static/images/letitgo.jpg',
                loaded: 'loadedHandler'
                //my_url:encodeURIComponent(window.location.href)
            };
            var video = [''];
            CKobject.embed('/ckplayer/ckplayer.swf', 'a1', 'ckplayer_a1', '100%', '100%', false, flashvars, video);
        }
    });
}


function rc() {
    if ($("#fdt").val() == "-1") {
        return;
    }
    if ($("#fsy").val() == "1") {
        return;
    }
    $.ajax({
        url: "/student/videoInfo!videoStudyEnd.action",
        type: "post",
        data: { vid: videoid, "kssj": $("#btime").val(), "xxsc": $("#nyv").val() },
        dataType: "json",
        cache: false,
        async: false,
        success: function (data) {
            if (data.studyFlag == "1") {
                alert("学时保存失败，请联系客服！");
            }
        }
    });
}

function videoPause() {
    CKobject.getObjectById('ckplayer_a1').videoPause();
}
function videoPlay() {
    //setTimeout("CKobject.getObjectById('ckplayer_a1').videoPlay();",1000);
    CKobject.getObjectById('ckplayer_a1').videoPlay();
}

function readypage() {
    $(document).mousemove
    (
        function () {
            Close_Notice();
        }
    )
}

//=============================================================================================
var tree, index = 0;
var spid = -1;
var title = '';
var kjurl = '';
var realVideoTime = 0;

var dict = [];


function loadedHandler() {
    if (CKobject.getObjectById('ckplayer_a1').getType()) {
        //CKobject.getObjectById('ckplayer_a1').addListener('paused', pausedHandler);
        //CKobject.getObjectById('ckplayer_a1').addListener('ended', endHandler);
        //CKobject.getObjectById('ckplayer_a1').addListener('play', playHandler);
        CKobject.getObjectById('ckplayer_a1').addListener('totaltime', get_totaltime);
    }
    else {
        //CKobject.getObjectById('ckplayer_a1').addListener('paused', 'pausedHandler');
        //CKobject.getObjectById('ckplayer_a1').addListener('ended', "endHandler");
        //CKobject.getObjectById('ckplayer_a1').addListener('play', "playHandler");
        CKobject.getObjectById('ckplayer_a1').addListener('totaltime', 'get_totaltime');
    }
}


function get_totaltime(realVideoTime) {
    
        dict.push({ 'spid': spid, 'title': title, 'kjurl': kjurl, 'time': realVideoTime });
        console.log({ 'spid': spid, 'title': title, 'kjurl': kjurl, 'time': realVideoTime });
        ++index;
        if (tree && tree.length > index) {
            play()
        } else {
            $("body").html(JSON.stringify(dict, null, 4));
        }
}



function play() {

    var video = tree[index];
    spid = video.attributes['spid'].value;
    title = video.attributes['title'].value;
    $.ajax({
        url: "/student/videoInfo!videoStudyBegin.action",
        type: "post",
        data: { vid: spid },
        dataType: "json",
        cache: false,
        async: false,
        success: function (data) {
            $('#myVideoImg').css('display', 'none');
            kjurl = data.kjurl;
            var flashvars = {
                f: kjurl + ".flv",
                c: 0,
                p: 1,
                g: 0,
                b: 0,
                v: 0,
                h: 4,
                wh: '1080:720',
                loaded: 'loadedHandler'
            };
            var video = [''];
            CKobject.embed('/ckplayer/ckplayer.swf', 'a1', 'ckplayer_a1', '100%', '100%', false, flashvars, video);
        }
    });

}

readypage = function () {

    $('#nowTime').removeClass('display');
    tree = $('.treelist a');
    play();
    //$('.treelist a').each(function (i, video) {
    //    spid = video.attributes['spid'].value;
    //    title = video.attributes['title'].value;
    //    studybegin(spid);
    //});

}
//=============================================================================================


$(document).ready(readypage);