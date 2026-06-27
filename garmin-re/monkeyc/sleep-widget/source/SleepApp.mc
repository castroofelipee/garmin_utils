using Toybox.Application as App;
using Toybox.WatchUi as Ui;
using Toybox.Communications as Comm;

// FR55: CIQ widget. Pulls last-night sleep from the relay (../relay/server.py)
// via makeWebRequest when the phone is BT-connected, then renders it.
// SKELETON — set RELAY_URL/RELAY_TOKEN, build with the Connect IQ SDK, sideload .PRG.

const RELAY_URL   = "https://your-relay.example/sleep";  // or http://<phone-ip>:8765/sleep
const RELAY_TOKEN = "somesecret";

class SleepApp extends App.AppBase {
    function initialize() { AppBase.initialize(); }
    function getInitialView() {
        return [ new SleepView() ];
    }
}

class SleepView extends Ui.View {
    hidden var data = null;     // parsed sleep dict
    hidden var status = "Loading...";

    function initialize() { View.initialize(); }

    function onShow() { fetch(); }

    function fetch() {
        var opts = {
            :method => Comm.HTTP_REQUEST_METHOD_GET,
            :responseType => Comm.HTTP_RESPONSE_CONTENT_TYPE_JSON
        };
        Comm.makeWebRequest(RELAY_URL + "?t=" + RELAY_TOKEN, {}, opts,
            method(:onResponse));
    }

    function onResponse(code, body) {
        if (code == 200 && body != null) {
            data = body;            // {date,total_min,deep_min,light_min,rem_min,awake_min,score}
            status = null;
        } else {
            status = "No data (" + code + ")";
        }
        Ui.requestUpdate();
    }

    function hm(m) {
        if (m == null) { return "--"; }
        return (m / 60).format("%d") + "h" + (m % 60).format("%02d");
    }

    function onUpdate(dc) {
        dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_BLACK);
        dc.clear();
        var cx = dc.getWidth() / 2;
        if (status != null) {
            dc.drawText(cx, dc.getHeight()/2, Graphics.FONT_MEDIUM, status,
                Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
            return;
        }
        var y = 18;
        dc.drawText(cx, y, Graphics.FONT_SMALL, "Last night", Graphics.TEXT_JUSTIFY_CENTER); y += 28;
        dc.drawText(cx, y, Graphics.FONT_NUMBER_MEDIUM, hm(data["total_min"]), Graphics.TEXT_JUSTIFY_CENTER); y += 44;
        dc.drawText(cx, y, Graphics.FONT_TINY,
            "Deep " + hm(data["deep_min"]) + "  REM " + hm(data["rem_min"]),
            Graphics.TEXT_JUSTIFY_CENTER); y += 22;
        dc.drawText(cx, y, Graphics.FONT_TINY,
            "Light " + hm(data["light_min"]) + "  Awake " + hm(data["awake_min"]),
            Graphics.TEXT_JUSTIFY_CENTER); y += 22;
        var sc = data["score"];
        dc.drawText(cx, y, Graphics.FONT_TINY, "Score " + (sc == null ? "--" : sc.toString()),
            Graphics.TEXT_JUSTIFY_CENTER);
    }
}
