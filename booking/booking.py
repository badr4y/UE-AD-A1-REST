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
    date = req.get("date")
    movieid = req.get("movieid")

    if not date or not movieid:
        return make_response(jsonify({"error": "Missing 'date' or 'movieid'"}), 400)

    showtime_response = requests.get(f"http://127.0.0.1:3202/showmovies/{date}")

    if showtime_response.status_code != 200:
        return make_response(jsonify({"error": "Invalid date"}), 400)

    try:
        showtime_data = showtime_response.json()

        if not showtime_data or not isinstance(showtime_data, list):
            return make_response(jsonify({"error": "Invalid response format from showtime service"}), 500)

        available_movies = showtime_data[0].get("movies", [])

        if movieid not in available_movies:
            return make_response(
                jsonify({"error": f"Invalid movie ID {movieid} for the given date"}), 400
            )

    except ValueError:
        return make_response(jsonify({"error": "Invalid response format from showtime service"}), 500)

    # Check if the booking already exists
    for booking in bookings:
        if booking["userid"] == userid and any(d['date'] == date and movieid in d.get('movies', []) for d in booking["dates"]):
            return make_response(jsonify({"error": "Booking already exists"}), 409)

    # Create or update the booking
    user_booking = next((booking for booking in bookings if booking["userid"] == userid), None)
    if user_booking:
        # Add the new movie to the existing date or create a new date entry
        user_dates = user_booking["dates"]
        existing_date = next((d for d in user_dates if d["date"] == date), None)
        if existing_date:
            existing_date["movies"].append(movieid)
        else:
            user_dates.append({"date": date, "movies": [movieid]})
    else:
        user_booking = {
            "userid": userid,
            "dates": [
                {
                    "date": date,
                    "movies": [movieid]
                }
            ]
        }
        bookings.append(user_booking)

    write_bookings(bookings)

    return make_response(jsonify(user_booking), 200)

def write_bookings(bookings):
    with open('./databases/bookings.json', 'w') as f:
        json.dump({"bookings": bookings}, f)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
