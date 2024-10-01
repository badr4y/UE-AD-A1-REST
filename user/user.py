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

@app.route("/users/<timeSinceLastActivity>", methods=['GET'])
def getUserSinceTime(timeSinceLastActivity):  
   userArray = list(filter(lambda x: x['last_active'] > int(timeSinceLastActivity),users))
   return make_response(jsonify(userArray), 200)

@app.route("/users/<userId>/bookings/moviesInfo", methods=['GET'])
def getMoviesInfoBookedByUser(userId):
    userBookingResponse = requests.get(f"http://127.0.0.1:3201/bookings/{userId}")
    if userBookingResponse.status_code == 200:
        userBooking = userBookingResponse.json()
        datesWithMovieId = [booking["movies"] for booking in userBooking if "movies" in booking]      
        moviesIds = set(movieId for movieList in datesWithMovieId for movieId in movieList)
        
        listInfoMovies = []
        for movieId in moviesIds:
            movieResponse = requests.get(f"http://127.0.0.1:3201/movies/{movieId}")
            if movieResponse.status_code == 200:
                listInfoMovies.append(movieResponse.json())
        
        # Check if we found movie information
        if len(listInfoMovies) > 0:
            return make_response(jsonify(listInfoMovies), 200)
        else:
            return make_response(jsonify({'error': 'No movies found'}), 400)
    else:
        return make_response(jsonify({'error': 'No user booking found'}), 400)


@app.route("/users/<userId>/<movieId>", methods=['GET'])
def getBookedDateForMovieId(userId, movieId):
    # Fetch the user's booking data
    userBookingResponse = requests.get(f"http://127.0.0.1:3201/bookings/{userId}")
    
    if userBookingResponse.status_code == 200:
        userBooking = userBookingResponse.json()    
        datesWithMovieId = [booking for booking in userBooking if movieId in booking["movies"]]
        if datesWithMovieId:
            dates = [booking['date'] for booking in datesWithMovieId if 'date' in booking]
            return make_response(jsonify(dates), 200)
        else:
            return make_response(jsonify({'error': 'Booking not found'}), 400)
    else:
        return make_response(jsonify({'error': 'No user booking found'}), 400)


@app.route("/users/<userId>", methods=['GET'])
def getAllBookedMovies(userId):
    # Fetch the user's booking data
    userBookingResponse = requests.get(f"http://127.0.0.1:3201/bookings/{userId}")
    
    if userBookingResponse.status_code == 200:
        userBooking = userBookingResponse.json()
        return make_response(jsonify(userBooking), 200)
    else:
        return make_response(jsonify({'error': 'Bookings not found'}), 400)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
