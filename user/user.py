from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

# Define the port and host for the service
PORT = 3203
HOST = '0.0.0.0'

# Load user data from a JSON file into a variable
with open('{}/databases/users.json'.format("."), "r") as jsf:
    users = json.load(jsf)["users"]

# Define the home route, which returns a welcome message
@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"

# Endpoint to get user information by user ID
@app.route("/users/<user_Id>", methods=['GET'])
def getUserInfoById(user_Id):
    # Filter the users to find the one with the specified user_Id
    user = list(filter(lambda x: x['id'] == user_Id, users))
    if user:  # If the user list is not empty
        return make_response(jsonify(user[0]), 200)  # Return the first user found
    else:
        return make_response(jsonify({'error': 'User not found'}), 400)  # Return an error if user not found

# Endpoint to get users who have been active since a specified time
@app.route("/users", methods=['GET'])
def get_users():
    # Endpoint to retrieve all bookings
    res = make_response(jsonify(users), 200)  # Create a response with the bookings data
    return res
@app.route("/users/time/<timeSinceLastActivity>")
def getUserSinceTime(timeSinceLastActivity):
    if timeSinceLastActivity is None:
        return make_response(jsonify({"error": "timeSinceLastActivity parameter is required"}), 400)

    # Filter users based on their last active timestamp
    userArray = list(filter(lambda x: x['last_active'] > int(timeSinceLastActivity), users))
    return make_response(jsonify(userArray), 200)  # Return the filtered list of users



# Endpoint to create a booking for a specific user
@app.route("/users/<userId>/booking", methods=['POST'])
def createBookingForUser(userId):
    req = request.get_json()  # Get the JSON request body
    date = req.get("date")
    movieId = req.get("movieid")

    # Make a POST request to the booking service to create a new booking
    makeBooking = requests.post(f"http://127.0.0.1:3201/bookings/{userId}", json=req)
    if makeBooking.status_code == 200:
        return make_response(jsonify(f"Reservation at date {date} for movie {movieId} made"), 200)  # Return success message
    else:
        return make_response(makeBooking.text, makeBooking.status_code)  # Return the error from the booking service

# Endpoint to get information about movies booked by a specific user
@app.route("/users/<userId>/bookingsInfo", methods=['GET'])
def getMoviesInfoBookedByUser(userId):
    # Request booking information from the booking service
    userBookingResponse = requests.get(f"http://127.0.0.1:3201/bookings/{userId}")
    if userBookingResponse.status_code == 200:
        userBooking = userBookingResponse.json()
        # Extract the movies booked by the user
        datesWithMovieId = [booking for booking in userBooking['dates'] if "movies" in booking]      
        print(datesWithMovieId)
        
        # Create a set of tuples containing movie IDs and their respective booking dates
        moviesIds = {(movieId, movieList['date']) 
                     for movieList in datesWithMovieId
                     for movieId in movieList["movies"]}
        print(moviesIds)
        
        listInfoMovies = []
        for movieId in moviesIds:
            # Request movie information from the movie service
            movieResponse = requests.get(f"http://127.0.0.1:3200/movies/{movieId[0]}")
            if movieResponse.status_code == 200:
                movie_info = dict()
                movie_info['filmInfo'] = movieResponse.json()  # Store movie information
                movie_info['BookingDate'] = movieId[1]  # Append booking date to the movie info

                listInfoMovies.append(movie_info)  # Add to the list of movie information
                
        # Check if we found movie information
        if len(listInfoMovies) > 0:
            return make_response(jsonify(listInfoMovies), 200)  # Return the list of movies
        else:
            return make_response(jsonify({'error': 'No movies found'}), 400)  # Return an error if no movies found
    else:
        return make_response(jsonify({'error': 'No user booking found'}), 400)  # Return an error if no booking found

# Endpoint to get raw booking data for a specific user
@app.route("/users/<userId>", methods=['GET'])
def getAllBookedMoviesRaw(userId):
    # Fetch the user's booking data from the booking service
    userBookingResponse = requests.get(f"http://127.0.0.1:3201/bookings/{userId}")
    if userBookingResponse.status_code == 200:
        userBooking = userBookingResponse.json()
        return make_response(jsonify(userBooking), 200)  # Return the user's booking data
    else:
        return make_response(jsonify({'error': 'Bookings not found'}), 400)  # Return an error if no bookings found
    
@app.route("/users/<userId>/booking", methods=['DELETE'])
def remove_booking_for_user(userId):
    req = request.get_json()  # Get the JSON request body
    date = req.get("date")
    movieId = req.get("movieid")

    # Check if date and movieId are provided
    if not date or not movieId:
        return make_response(jsonify({"error": "Missing 'date' or 'movieid' in request body"}), 400)

    # Create a request to the booking service to delete the booking
    deleteBookingResponse = requests.delete(f"http://127.0.0.1:3201/bookings/del/{userId}", json=req)

    if deleteBookingResponse.status_code == 200:
        return make_response(jsonify(f"Successfully deleted booking for user {userId} on date {date} for movie {movieId}"), 200)  # Return success message
    else:
        return make_response(deleteBookingResponse.json(), deleteBookingResponse.status_code)  # Return error from the booking service
# Start the Flask application
if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT, debug=True)  # Enable debug mode for development
