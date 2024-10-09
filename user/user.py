from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

with open('{}/databases/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/users/<user_Id>", methods=['GET'])
def getUserInfoById(user_Id):
    # Convert filter result to a list and check if a user was found
    user = list(filter(lambda x: x['id'] == user_Id, users))
    if user:  # If the user list is not empty
        return make_response(jsonify(user[0]), 200)  # Return the first user found
    else:
        return make_response(jsonify({'error': 'User not found'}), 400)


@app.route("/users", methods=['GET'])
def getUserSinceTime():
    timeSinceLastActivity = request.args.get('timeSinceLastActivity')
    if timeSinceLastActivity is None:
        return make_response(jsonify({"error": "timeSinceLastActivity parameter is required"}), 400)

    userArray = list(filter(lambda x: x['last_active'] > int(timeSinceLastActivity), users))
    return make_response(jsonify(userArray), 200)

@app.route("/users/<userId>/booking", methods=['POST'])
def createBookingForUser(userId):
    req = request.get_json()
    date = req.get("date")
    movieId = req.get("movieid")
    makeBooking = requests.post(f"http://127.0.0.1:3201/bookings/{userId}", json=req)
    if makeBooking.status_code == 200:
        return make_response(jsonify(f"Reservation at date {date} for movie {movieId} made"), 200)
    else:
        return make_response(makeBooking.text, makeBooking.status_code)

@app.route("/users/<userId>/bookingsInfo", methods=['GET'])
def getMoviesInfoBookedByUser(userId):
    userBookingResponse = requests.get(f"http://127.0.0.1:3201/bookings/{userId}")
    if userBookingResponse.status_code == 200:
        userBooking = userBookingResponse.json()
        datesWithMovieId = [booking for booking in userBooking['dates'] if "movies" in booking]      
        print(datesWithMovieId)
        moviesIds = {(movieId, movieList['date']) 
                    for movieList in datesWithMovieId
                    for movieId in movieList["movies"]}
        print(moviesIds)
        listInfoMovies = []
        for movieId in moviesIds:   
            movieResponse = requests.get(f"http://127.0.0.1:3200/movies/{movieId[0]}")
            if movieResponse.status_code == 200:
                movie_info = dict()
                movie_info['filmInfo'] = movieResponse.json()
                movie_info['BookingDate'] = movieId[1]  # Append booking date to the movie info

                listInfoMovies.append(movie_info)
        # Check if we found movie information
        if len(listInfoMovies) > 0:
            return make_response(jsonify(listInfoMovies), 200)
        else:
            return make_response(jsonify({'error': 'No movies found'}), 400)
    else:
        return make_response(jsonify({'error': 'No user booking found'}), 400)

@app.route("/users/<userId>", methods=['GET'])
def getAllBookedMoviesRaw(userId):
    # Fetch the user's booking data
    userBookingResponse = requests.get(f"http://127.0.0.1:3201/bookings/{userId}")
    if userBookingResponse.status_code == 200:
        userBooking = userBookingResponse.json()
        return make_response(jsonify(userBooking), 200)
    else:
        return make_response(jsonify({'error': 'Bookings not found'}), 400)

if __name__ == "__main__":
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT,debug=True)
