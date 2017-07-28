# AISTLab IOT DEMO
> A simplest framework of IOT

> Demo is simulation of MOBIKE system

> winxos 2017-07-20

## System Elements
1. UDP SERVER (OR MQTT EQ)
2. ARDUINO DEVICE(ESP8266)
3. HTTP SERVER(USING FLASK IN DEMO)
4. APP(USING WEB BROWSER)

## Sequence
1. User scan the QR code in DEVICE. The QR code encode the http request contain server host and device id or others.
2. App deal the Authorization, and pass the id to http server.
3. Http server pass through the command to the UDP server(OR MQTT server).
4. Each DEVICE keep alive with UDP server.
5. UDP server route the command to the DEVICE through ID.
6. After the Device received the command, unlock, send 'unlocked' message to the UDP server.
7. UDP server pass through the message to the HTTP server.
8. HTTP server pass through 'unlocked' message to App.
