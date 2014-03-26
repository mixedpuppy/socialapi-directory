var http = require("http");
var console = require('console');
var express = require('express');
var fs = require('fs');
var app = express();
var server;


/*
    /foobar/socailapi-directory/en_US/foobar#foo
    /socailapi-directory/en_US/foobar#foo
    /en_US/foobar#foo
*/
app.get(/^\/?.*?\/\w{2}_\w{2}(\/.*)/, function (req, res) {
    console.log(__dirname + req.path + " => "+req.params[0]);
    if (!req.params[0]) {
      res.sendfile(__dirname + "/index.html");
      return;
    }
    var file = __dirname + req.params[0];
    fs.exists(file, function(exists) {
      if (exists) {
        res.sendfile(__dirname + req.params[0]);
      } else {
        res.sendfile(__dirname + "/index.html");
      }
    })
});

//app.use(/^\/?.*?\/\w{2}_\w{2}\/?.*/, express.static(__dirname));
app.use(express.static(__dirname));

app.start = function(serverPort, callback) {
  console.log("app starting");
  server = http.createServer(this);
  server.listen(serverPort);
  if (callback)
    callback();
};

app.shutdown = function(callback) {
  server.close(callback);
};

module.exports.app = app;
