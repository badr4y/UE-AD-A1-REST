from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
   bookings = json.load(jsf)["bookings"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/bookings", methods=['GET'])
def get_bookings():
    res = make_response(jsonify(bookings), 200)
    return res

@app.route("/bookings/<userid>", methods=['GET'])
def get_bookings_byuserid(userid):
   json = ""
   for booking in bookings:
      if str(booking["userid"]) == str(userid):
         json = booking

   if not json:
      res = make_response(jsonify({"error":"booking not found"}),400)
   else:
      res = make_response(jsonify(json),200)
   return res


@app.route("/bookings/<userid>", methods=['POST'])
def add_booking_byuserid(userid):
    req = request.get_json()
    dates = req['dates']
    for date in dates:
        showtime_response = requests.get(f"http://127.0.0.1:3202/showmovies/{date.get('date')}")
        print(date)
        # Check if the response is successful
        if showtime_response.status_code != 200:
            return make_response(jsonify({"error": "Invalid date"}), 400)

        try:
            # The showtime service returns a list of movie objects; we need to extract the 'movies' field
            showtime_data = showtime_response.json()

            if not showtime_data or not isinstance(showtime_data, list):
                return make_response(jsonify({"error": "Invalid response format from showtime service"}), 500)

            # Extract the movies list from the first item in the showtime data
            available_movies = showtime_data[0].get("movies", [])

            # Log the movies for debugging
            print(f"Movies available on {date.get('date')}: {available_movies}")

            # Validate movie IDs in the date
            invalid_movies = [
                movie_id for movie_id in date.get("movies", [])
                if movie_id not in available_movies
            ]

            if invalid_movies:
                return make_response(
                    jsonify({"error": f"Invalid movie IDs {invalid_movies} for the given date"}), 400
                )

        except ValueError:
            return make_response(jsonify({"error": "Invalid response format from showtime service"}), 500)

    new_booking = {
        "userid": userid,
        "dates": dates
    }

    for booking in bookings:
        if booking["userid"] == userid and booking["dates"] == dates:
            return make_response(jsonify({"error": "Booking already exists"}), 409)

    bookings.append(new_booking)
    write_bookings(bookings)

    return make_response(jsonify({"message": "Booking created"}), 200)


def write_bookings(bookings):
    with open('./databases/bookings.json', 'w') as f:
        json.dump({"bookings": bookings}, f)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
