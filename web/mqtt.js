class messagesHandle{
    constructor(n_messages){
        this.n_messages = n_messages;
        this.messages = new Array(n_messages);
    };

    get getMessages(){
        return this.messages;
    };

    addMessage(message){
        if(this.messages.length >= this.n_messages){
            this.messages.shift();}
        this.messages.push(message);
    };
};

// Create a client instance
// var host = "broker.hivemq.com";
// var port = 8000;
// var path = "/mqtt";
var host = "192.168.178.107";
var port = 9002
var path = ""
var clientID = "browser_client_"+makeid(5);
var topic = "heating";
var mqttClient = new Paho.MQTT.Client(host,port,path,clientID);

var Messages = new messagesHandle(20);
var charger_http_connected = true;
var charging_state = undefined;

// set callback handlers
mqttClient.onConnectionLost = onConnectionLost;
mqttClient.onMessageArrived = onMessageArrived;

// connect the client
mqttClient.connect({
    onSuccess:onConnect
});

// called when the client connects
function onConnect() {
    // Once a connection has been made, make a subscription and send a message.
    //console.log("onConnect");
    mqttClient.subscribe(topic+"/#");
    payload = "Client connected successfully";
    mqttClient.send(topic, payload, qos=0, retained=false);
};

// called when the client loses its connection
function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
        console.log("onConnectionLost: "+responseObject.errorMessage);
    };
};

// called when a message arrives
function onMessageArrived(message) {
    // console.log("onMessageArrived: "+message.destinationName+" "+message.payloadString+" "+message.qos+" "+message.retained);
    Messages.addMessage(message);
    $("#messages-table").html("")
    Messages.messages.forEach( element => {
        $("#messages-table").prepend(
            "<tr><th>"+element.destinationName+
            "</th><th>"+element.payloadString+
            "</th><th>"+element.qos+
            "</th><th>"+element.retained+
            "</th></tr>");
    });
    var receivedData = ""
    try{
        receivedData = JSON.parse(message.payloadString);}
    catch(e){}
    var topic = message.destinationName;
    var topics = topic.split("/");
    var messageType = topics[0];
    if(messageType == "heating"){
        var jquery_name = "#"+topics[1]+"-"+topics[2]
        $(jquery_name).html(message.payloadString);
    }
};

$(document).ready(() => {
    $("#http-error-alert").hide();
    /*var counter = 0;
    setInterval(() => {
        if(mqttClient.isConnected()){
            // mqttClient.send(topic+"/subtopic", String(counter), qos=0, retained=true);
            // counter++;
        }
    }, 10000)
    */
});

$('#custom-publish-form').on('submit', event => {
    event.preventDefault();
    input_text = $('#test-text').val();
    //console.log("text ("+input_text+") submitted!");
    text = input_text.split(" ");
    payloadString = text.slice(1).join(" ")
    if(text.length > 1){
        mqttClient.send(topic+"/command/"+text[0], payloadString, qos=0, retained=false)}
});

$('#toggle-charging-form').on('submit', event => {
    event.preventDefault();
    var args = undefined;
    if(charging_state){
        args = "False";
    }
    else{
        args = "True";
    }
    if(mqttClient.isConnected()){
        mqttClient.send(topic+"/command/alw", args, qos=0, retained=false)
    }
});

$('#solar-ratio-form').on('submit', event => {
    event.preventDefault();
    solarRatio = $('#solar-ratio-input').val();
    //console.log("solar-ratio "+solarRatio+" submitted!")
    mqttClient.send(topic+"/command/solar-ratio", solarRatio, qos=0, retained=false)
});
