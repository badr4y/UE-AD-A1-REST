from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3202  # Define the port on which the Flask app will run
HOST = '0.0.0.0'  # The host where the app will be accessible

# Load the existing showtimes from the JSON file at the start of the application
with open('{}/databases/times.json'.format("."), "r") as jsf:
    schedule = json.load(jsf)["schedule"]  # Read the schedule data into a Python object

@app.route("/", methods=['GET'])
def home():
    # Home route that returns a simple test message
    return "<h1 style='color:blue'>Test</h1>"

@app.route("/showtimes", methods=['GET'])
def get_times():
    # Endpoint to retrieve all available showtimes
    return make_response(jsonify(schedule), 200)  # Return the schedule data in JSON format

@app.route("/showmovies/<date>", methods=['GET'])
def get_moviesByDate(date):
    # Endpoint to retrieve movies scheduled for a specific date
    movie = list(filter(lambda x: x["date"] == date, schedule))  # Filter the schedule for the given date
    return make_response(jsonify(movie), 200)  # Return the filtered list of movies for the specified date

if __name__ == "__main__":
    print("Server running in port %s" % (PORT))  # Print a message indicating the server is running
    app.run(host=HOST, port=PORT)  # Start the Flask application
