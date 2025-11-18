/****************************************************************************
 **
 ** qwebchannel.js from Qt source (MIT licensed)
 **
 ****************************************************************************/
(function () {
  "use strict";
  alert("QWebChannel.js");
  if (window.qt && window.qt.webChannelTransport) {
    new QWebChannel(qt.webChannelTransport, function (channel) {
      window.channel = channel;
    });
  }

  window.QWebChannel = function (transport, initCallback) {
    var channel = this;
    this.transport = transport;

    this.send = function (data) {
      channel.transport.send(JSON.stringify(data));
    };

    this.transport.onmessage = function (message) {
      var data = JSON.parse(message.data);
      if (data.type === "signal") {
        var object = channel.objects[data.object];
        if (object) {
          var signal = object[data.signal];
          if (signal) signal.apply(object, data.args);
        }
      }
    };

    this.objects = {};

    transport.send(JSON.stringify({ type: "init" }));

    this.execCallbacks = [];

    transport.onmessage = function (message) {
      var data = JSON.parse(message.data);
      if (data.type === "init") {
        for (var name in data.objects) {
          var obj = {};
          obj.__id__ = name;
          channel.objects[name] = obj;
        }
        initCallback(channel);
      }
    };
  };
})();
