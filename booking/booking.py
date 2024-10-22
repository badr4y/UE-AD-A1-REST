from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201  # Define the port on which the Flask app will run
HOST = '0.0.0.0'  # The host where the app will be accessible

# Load the existing bookings from the JSON file at the start of the application
with open('{}/databases/bookings.json'.format("."), "r") as jsf:
    bookings = json.load(jsf)["bookings"]  # Read bookings data into a Python object

@app.route("/", methods=['GET'])
def home():
    # Home route that returns a welcome message
    return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/bookings", methods=['GET'])
def get_bookings():
    # Endpoint to retrieve all bookings
    res = make_response(jsonify(bookings), 200)  # Create a response with the bookings data
    return res

@app.route("/bookings/<userid>", methods=['GET'])
def get_bookings_byuserid(userid):
    # Endpoint to retrieve bookings for a specific user identified by userid
    json = ""
    for booking in bookings:
        # Check if the booking belongs to the specified userid
        if str(booking["userid"]) == str(userid):
            json = booking  # Store the found booking

    if not json:
        # If no booking is found, return an error message
        res = make_response(jsonify({"error":"booking not found"}), 400)
    else:
        # Return the found booking
        res = make_response(jsonify(json), 200)
    return res

@app.route("/bookings/del/<userid>", methods=['DELETE'])
def remove_booking_fromuserid(userid):
    # Endpoint to delete a movie from a booking for a specific user identified by userid
    req = request.get_json()  # Get JSON data from the request body
    date = req.get("date")  # Extract the date from the request body
    movieid = req.get("movieid")  # Extract the movieid from the request body

    if not date or not movieid:
        # Return an error if the required data is missing
        return make_response(jsonify({"error": "Missing 'date' or 'movieid' in the request"}), 400)

    # Find the user's booking by userid
    user_booking = next((booking for booking in bookings if booking["userid"] == userid), None)

    if not user_booking:
        # Return an error if no booking exists for the user
        return make_response(jsonify({"error": f"No booking found for user {userid}"}), 404)

    # Find the specified date in the user's bookings
    date_booking = next((d for d in user_booking["dates"] if d["date"] == date), None)

    if not date_booking:
        # Return an error if the date is not found in the user's bookings
        return make_response(jsonify({"error": f"No booking found for the given date {date}"}), 404)

    if movieid not in date_booking["movies"]:
        # Return an error if the movie is not found in the movies list for the date
        return make_response(jsonify({"error": f"Movie ID {movieid} not found for the given date {date}"}), 404)

    # Remove the movie from the movies list for the given date
    date_booking["movies"].remove(movieid)

    if not date_booking["movies"]:
        # If the movie list for the date is now empty, remove the entire date entry
        user_booking["dates"].remove(date_booking)

    if not user_booking["dates"]:
        # If there are no more bookings for the user, remove the entire booking
        bookings.remove(user_booking)

    # Persist the updated bookings
    write_bookings(bookings)

    # Return a success message
    return make_response(jsonify({"message": f"Movie ID {movieid} for date {date} removed successfully for user {userid}"}), 200)

@app.route("/bookings/<userid>", methods=['POST'])
def add_booking_byuserid(userid):
    # Endpoint to add a new booking for a specific user
    req = request.get_json()  # Get JSON data from the request
    date = req.get("date")    # Extract the date from the request
    movieid = req.get("movieid")  # Extract the movie ID from the request

    # Check for missing parameters in the request
    if not date or not movieid:
        return make_response(jsonify({"error": "Missing 'date' or 'movieid'"}), 400)

    # Verify if the specified date has available movies
    showtime_response = requests.get(f"http://127.0.0.1:3202/showmovies/{date}")

    if showtime_response.status_code != 200:
        # Return an error if the date is invalid
        return make_response(jsonify({"error": "Invalid date"}), 400)

    try:
        showtime_data = showtime_response.json()  # Parse the response JSON

        # Validate the response from the showtime service
        if not showtime_data or not isinstance(showtime_data, list):
            return make_response(jsonify({"error": "Invalid response format from showtime service"}), 500)

        available_movies = showtime_data[0].get("movies", [])  # Get the list of available movies

        if movieid not in available_movies:
            # Return an error if the movie ID is not available for the given date
            return make_response(
                jsonify({"error": f"Invalid movie ID {movieid} for the given date"}), 400
            )

    except ValueError:
        # Handle any JSON decoding errors from the showtime service response
        return make_response(jsonify({"error": "Invalid response format from showtime service"}), 500)

    # Check if the booking already exists for the user on the given date
    for booking in bookings:
        if booking["userid"] == userid and any(d['date'] == date and movieid in d.get('movies', []) for d in booking["dates"]):
            # If a booking already exists, return a conflict error
            return make_response(jsonify({"error": "Booking already exists"}), 409)

    # Create or update the booking
    user_booking = next((booking for booking in bookings if booking["userid"] == userid), None)
    if user_booking:
        # Update existing booking
        user_dates = user_booking["dates"]
        existing_date = next((d for d in user_dates if d["date"] == date), None)
        if existing_date:
            existing_date["movies"].append(movieid)  # Append movie ID to existing date
        else:
            user_dates.append({"date": date, "movies": [movieid]})  # Add new date entry
    else:
        # Create a new booking for the user
        user_booking = {
            "userid": userid,
            "dates": [
                {
                    "date": date,
                    "movies": [movieid]
                }
            ]
        }
        bookings.append(user_booking)  # Add the new booking to the list

    write_bookings(bookings)  # Persist the updated bookings

    return make_response(jsonify(user_booking), 200)  # Return the created or updated booking

def write_bookings(bookings):
    # Function to write the updated bookings back to the JSON file
    with open('./databases/bookings.json', 'w') as f:
        json.dump({"bookings": bookings}, f)  # Dump the bookings into the JSON file

if __name__ == "__main__":
    print("Server running in port %s"%(PORT))  # Print server status message
    app.run(host=HOST, port=PORT)  # Start the Flask application
