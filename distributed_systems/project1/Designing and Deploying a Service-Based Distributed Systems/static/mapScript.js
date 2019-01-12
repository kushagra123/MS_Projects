function initMap() {
	var markerArray = [];
	var directionsService = new google.maps.DirectionsService;
	var directionsDisplay = new google.maps.DirectionsRenderer({map:map});
	var stepDisplay=new google.maps.InfoWindow
	for (var i = 0; i < markerArray.length; i++) {
		markerArray[i].setMap(null);
	}
	var geocoder = new google.maps.Geocoder();
	var address = document.getElementById("to").value;
	geocoder.geocode( { 'address': address}, function(results, status) {
		if (status == google.maps.GeocoderStatus.OK) {
			var latitude = results[0].geometry.location.lat();
			var longitude = results[0].geometry.location.lng();
			var myLatLng = {lat: latitude, lng: longitude};
			var map = new google.maps.Map(document.getElementById('map'), {
				zoom: 4,
				center: myLatLng,
				mapTypeId: google.maps.MapTypeId.SATELLITE
			});
			directionsDisplay.setMap(map);
			directionsService.route({
				origin: document.getElementById('from').value,
				destination: document.getElementById('to').value,
				travelMode: 'DRIVING'
			}, function(response, status) {
				if (status === 'OK') {
					directionsDisplay.setDirections(response);
					showSteps(response, markerArray, stepDisplay, map);
				} else {
					window.alert('Directions request failed due to ' + status);
				}
			});
		}
	});
}
function showSteps(directionResult, markerArray, stepDisplay, map) {
	var myRoute = directionResult.routes[0].legs[0];
	for (var i = 0; i < myRoute.steps.length; i++) {
		var marker = markerArray[i] = markerArray[i] || new google.maps.Marker;
		marker.setMap(map);
		marker.setPosition(myRoute.steps[i].start_location);
		attachInstructionText(
			stepDisplay, marker, myRoute.steps[i].instructions, map);
	}
}
function attachInstructionText(stepDisplay, marker, text, map) {
	google.maps.event.addListener(marker, 'click', function() {
		stepDisplay.setContent(text);
		stepDisplay.open(map, marker);
	});
}