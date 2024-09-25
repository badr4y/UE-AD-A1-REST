from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3202
HOST = '0.0.0.0'

with open('{}/databases/times.json'.format("."), "r") as jsf:
   schedule = json.load(jsf)["schedule"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Test</h1>"


@app.route("/showtimes", methods=['GET'])
def get_times():
   return make_response(jsonify(schedule), 200)
   

@app.route("/showmovies/<date>", methods=['GET'])
def get_moviesByDate(date):
   movie =  list(filter(lambda x: x["date"] == date,schedule))
   return make_response(jsonify(movie), 200)  # Return the first user found



if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
