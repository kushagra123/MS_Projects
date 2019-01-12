  ar map;
  var geoJSON;
  var request;
  var myLatLng;
  var gettingData = false;
  var openWeatherMapKey = "e6a9dbbf41e5cc3040051f01249d5972"
  var stepDisplay=new google.maps.InfoWindow;


  function initMap() {
	var markerArray = [];
	var directionsService = new google.maps.DirectionsService;
	var directionsDisplay = new google.maps.DirectionsRenderer({map:map});
	for (var i = 0; i < markerArray.length; i++) {
		markerArray[i].setMap(null);
	}
    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 4,
    });
    directionsDisplay.setMap(map);
    directionsService.route({
    origin: 'seattle',
    destination: 'buffalo',
    travelMode: 'DRIVING',
    }, function(response, status) {
    if (status === 'OK') {
        directionsDisplay.setDirections(response);
        showSteps(response, markerArray, stepDisplay, map);
        } else {
        window.alert('Directions request failed due to ' + status);
        }
    });
}
function showSteps(directionResult, markerArray, stepDisplay, map) {
	var myRoute = directionResult.routes[0].legs[0];
	for (var i = 0; i< myRoute.steps.length;i+=5) {
	  //  alert("n here");
        var service = new google.maps.places.PlacesService(map);
	    var lat=myRoute.steps[i].end_location.lat();
	    var lng=myRoute.steps[i].end_location.lng();
	    var latlng={lat:lat,lng:lng};
	    var type='abc';
	    var marker = new google.maps.Marker;
                    marker.setMap(map);
                    marker.setPosition(myRoute.steps[i].end_location);
        attachInstructionText(stepDisplay, marker,myRoute.steps[i].instructions, map,type);
	    var request={
	        location:latlng,
	        radius:'200',
	        type:['locality','political']
	    };
        service.nearbySearch(request,function(result,status){
            if (status == google.maps.places.PlacesServiceStatus.OK) {
              for(var j=0;j<result.length;j+=5){
                    //alert(result[j].name);
                    var marker = new google.maps.Marker;
                    marker.setMap(map);
                    marker.setPosition(result[j].geometry.location);
                    attachInstructionText(stepDisplay, marker,result[j].name, map,type);
                }
            }
        });
	}
}
function attachInstructionText(stepDisplay, marker, text, map,type) {
	google.maps.event.addListener(marker, 'mouseover', function() {
	    var lat = marker.getPosition().lat();
        var lng = marker.getPosition().lng();
        initialize(lat,lng,map,marker,text,type);
	});
	google.maps.event.addListener(marker, 'mouseout', function() {
	    infowindow.close();
	});
}
function initialize(lat,long,map,marker,text,type) {
    var myLatLng1 = {lat: lat, lng: long};
    var mapOptions = {
      zoom: 4,
      center: myLatLng1
    };
    getWeather(lat,long,marker,text,type);
  }
  var getWeather = function(lat,long,marker,text,type) {
    var requestString = "http://api.openweathermap.org/data/2.5/weather?lat=" + lat + "&lon=" + long + "&appid=" + openWeatherMapKey+"&units=metric";
    request = new XMLHttpRequest();
    request.open("get", requestString, false);
    request.send();
    var returned=JSON.parse(request.response);
    var temp=returned.main.temp;
    var weatherCondition=returned.weather[0].main;
    var humidity=returned.main.humidity;
    //alert("Temperature: " + temp + " Weather condition: " + weatherCondition + " Humidity: " + humidity);
    infowindow.setContent(text+" "+"Temperature: " + temp+'\n'+
                          "Weather condition: " + weatherCondition+
                          "Humidity: " + humidity);
    infowindow.open(map,marker);
  };
  var infowindow = new google.maps.InfoWindow();


  // google.maps.event.addDomListener(window, 'load', initialize);