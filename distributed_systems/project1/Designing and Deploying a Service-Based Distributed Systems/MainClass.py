from flask import Flask, render_template,request
import googlemaps
import json
import urllib.request
import requests

app = Flask(__name__)
gmaps = googlemaps.Client(key='')
app.config['SECRET_KEY'] = 'AfrvR9BdVEzmCBY1idZDBxA134OxHWiy'
openWeatherMapKey = ""
def decode_polyline(polyline_str):
    index, lat, lng = 0, 0, 0
    coordinates = []
    changes = {'latitude': 0, 'longitude': 0}

    # Coordinates have variable length when encoded, so just keep
    # track of whether we've hit the end of the string. In each
    # while loop iteration, a single coordinate is decoded.
    while index < len(polyline_str):
        # Gather lat/lon changes, store them in a dictionary to apply them later
        for unit in ['latitude', 'longitude']:
            shift, result = 0, 0

            while True:
                byte = ord(polyline_str[index]) - 63
                index+=1
                result |= (byte & 0x1f) << shift
                shift += 5
                if not byte >= 0x20:
                    break

            if (result & 1):
                changes[unit] = ~(result >> 1)
            else:
                changes[unit] = (result >> 1)

        lat += changes['latitude']
        lng += changes['longitude']

        coordinates.append((lat / 100000.0, lng / 100000.0))

    return coordinates

def callMap():
    origin='seattle'
    destination='buffalo'
    directions_result = gmaps.directions("Seattle",
                                         "buffalo",
                                         mode="driving",
                                         departure_time='now')
    for route in directions_result:
            polyline=route['overview_polyline']

    coordinates=decode_polyline(polyline['points'])
    weather_data=[]
    for coordinate in coordinates:
        if(coordinates.index(coordinate)%2==0):
            lat=coordinate[0]
            lng=coordinate[1]
            print("http://api.openweathermap.org/data/2.5/weather?lat=" + str(lat) + "&lon=" + str(lng) + "&appid=" + openWeatherMapKey + "&units=metric")
            # weather_result=urllib.request.urlopen("http://api.openweathermap.org/data/2.5/weather?lat=" + str(lat) + "&lon=" + str(lng) + "&appid=" + openWeatherMapKey + "&units=metric")
            # output = weather_result.read().decode('utf-8')
            # raw_api=json.loads(output)
            # weather_data.append(raw_api)

    temperature=[]
    for weather_main in weather_data:
        temperature=weather_main['main']['temp']
    

# callMap()



@app.route("/")
def hello():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug="true")
