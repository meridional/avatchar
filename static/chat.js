/**
 * Created by ye on 12/15/13.
 */

var conn;

var users = [];
var msgs = [];

function post_to_msgs(dom) {
    var msgsDom = document.getElementById("msgs");
    msgsDom.insertBefore(dom,msgsDom.firstChild);
}

function received_msg(msg) {
    var newDiv = document.createElement("div");
    var imgSpan = document.createElement("span");
    var img = document.createElement("img");
    img.src = msg["img"];
    imgSpan.appendChild(img);
    var user_tag = document.createElement("span");
    var time = new Date(msg["datetime"]);
    user_tag.innerHTML = (msg["datetime"] + ", " + escape(msg["name"]) + ": " + msg["msg"]);
    newDiv.appendChild(imgSpan);
    newDiv.appendChild(user_tag);
    post_to_msgs(newDiv);
}

function user_joined(user) {
    for (var i = 0; i < users.length; i++) {
        if (users[i]["name"] == user["name"]) {
            return;
        }
    }
    users.push(user);

    var msgDiv = document.createElement("span");
    //newDiv.id = "user-" + user["name"];
    var usersDom = document.getElementById("users");
    //usersDom.appendChild(newDiv);
    msgDiv.innerHTML = escape(user["name"]) + " joined.";
    post_to_msgs(msgDiv);

    var userDiv = document.createElement("span");
    userDiv.id = "user-" + escape(user["name"]);
    var img = document.createElement("img");
    img.src = user["img"];
    var imgSpan = document.createElement("span");
    imgSpan.appendChild(img);
    var namediv = document.createElement("span");
    namediv.innerHTML = escape(user["name"]);
    userDiv.appendChild(imgSpan);
    userDiv.appendChild(namediv);
    usersDom.appendChild(userDiv);
}

function user_left(user) {
    var userDom = document.getElementById("user-" + escape(user["name"]));
    userDom.parentNode.removeChild(userDom);

    var msgDom = document.createElement("div");
    msgDom.innerHTML = escape(user["name"]) + " left.";
    post_to_msgs(msgDom);
}

function host() {
    var loc = window.location, new_uri;
    return "http://" + loc.host;
}

function init_conn () {
    var loc = window.location, new_uri;
    if (loc.protocol === "https:") {
        new_uri = "wss:";
    } else {
        new_uri = "ws:";
    }
    new_uri += "//" + loc.host;
    new_uri += "/rush/123";
    conn = new WebSocket(new_uri);
    conn.onopen = function () {
        get_recent_msgs();
        get_current_users();
        console.log("opened");
    };
    conn.onmessage = function (msg) {
        data = JSON.parse(msg.data);
        if ("data" in data) {
            received_msg(data["data"][0]);
        } else if ("user_left" in data) {
            user_left(data["user_left"]);
        } else if ("user_joined" in data) {
            user_joined(data["user_joined"]);
        }
    };
    conn.onclose = function () {
        //TODO: update some ui
        var reloadDom = document.createElement("div");
        reloadDom.innerHTML = "Connection lost, refresh to continue";
        post_to_msgs(reloadDom);
    };
}


function send_get_request(url, callback) {
    var request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        console.log(request.responseText);
        if (request.readyState == 4 && request.status == 200) {
            callback(request.responseText)
        }
    };
    console.log(host() + url);
    request.open("GET",host()+url,true);
    request.send();
}

function get_recent_msgs() {
    send_get_request("/hist", function(r) {
        msgs = JSON.parse(r);
        // TODO: ready ui
        msgs = msgs["data"];
        console.log(msgs);
        var i = msgs.length - 1;
        for (; i >= 0; i--) {
            received_msg(msgs[i]);
        }
    });
}


function send_pressed() {
    var text = document.getElementById("input");
    if (text.value.length >= 1 && conn.readyState == 1) {
        conn.send(text.value);
        text.value = "";
    }
}

function get_current_users() {
    send_get_request("/current", function(r) {
        usersGot = JSON.parse(r)["users"];
        //console.log(users);
        var i, n = usersGot.length;
        for (i = 0; i < n; i++) {
            user_joined(usersGot[i]);
        }
    });
}

function init() {
    init_conn();
}
