function initMap(){
	var map = new google.maps.Map(document.getElementById('map'),)
	var directionsService = new google.maps.DirectionsService;
	var directionsDisplay = new google.maps.DirectionsRenderer({map:map});
	var infoWindow=new google.maps.InfoWindow;
	var markerArray=[];
	for (var i = 0; i < markerArray.length; i++) {
		markerArray[i].setMap(null);
	}
	directionsDisplay.setMap(map);
	directionsService.route({
		origin: document.getElementById('from').value,
		destination: document.getElementById('to').value,
		travelMode: 'DRIVING',
		optimizeWaypoints: false,
		provideRouteAlternatives: true,
		}, function(response, status) {
		if (status === google.maps.DirectionsStatus.OK) {
        var directionsDisplay = new google.maps.DirectionsRenderer({
          map: map,
          directions: response,
          draggable: false,
          suppressPolylines: false
        });
		  showSteps(response, markerArray, infoWindow, map);
		} else {
				window.alert('Directions request failed due to ' + status);
		}
	});
}
function showSteps(directionResult, markerArray, stepDisplay, map) {
	var myRoute = directionResult.routes[0].legs[0]
	for (var i = 0; i < myRoute.steps.length; i++) {
		  var marker = markerArray[i] = markerArray[i] || new google.maps.Marker;
	      marker.setMap(map);
	      marker.setPosition(myRoute.steps[i].start_location);
//		attachInstructionText(
//			stepDisplay, marker, myRoute.steps[i].instructions, map);
	}
}