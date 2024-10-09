# UE-AD-A1-REST
# Movie Booking Service

## Overview

A microservices-based application for booking movie tickets, consisting of:

- **User Service**: Manages user data.
- **Booking Service**: Handles movie bookings.
- **Showtime Service**: Provides movie showtimes.

## Features

- User management
- Movie booking
- Showtime retrieval

## Technologies

- Flask
- JSON
- Requests

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/movie-booking-service.git
   cd movie-booking-service
   pip3 install requirements

## API Endpoints

### User Service

- **GET** `/users/<user_Id>`  
  Retrieve user info by ID.

- **GET** `/users`  
  Get active users since a given timestamp.  
  **Query Parameters:**  
  - `timeSinceLastActivity`: (required) Timestamp to filter users by their last activity.

- **POST** `/users/<userId>/booking`  
  Create a booking for a user.  
  **Request Body:**  
  ```json
  {
    "date": "YYYYMMDD",
    "movieid": "movie_id"
  }
- **GET** `/users/<userId>/bookingsInfo`
Get booking info for a user.

- **GET** `/users/<userId>`
Get all booking data for a user.
### Booking Service
- **GET** `/bookings`
Retrieve all bookings.
- **GET** `/bookings/<userid>`
Retrieve bookings by user ID.
- **POST** `/bookings/<userid>`  
Add a booking for a user.
 **Request Body:**  
  ```json
  {
    "date": "YYYYMMDD",
    "movieid": "movie_id"
  }
  ```
### Showtime Service
- **GET** `/showtimes`
Retrieve all showtimes.

- **GET** `/showmovies/<date>`
Retrieve movies available on a specific date.

### Movies Endpoints

- **GET** `/json`  
  Retrieve all movies.

- **GET** `/moviesbytitle`  
  Retrieve a movie by its title.  
  **Query Parameters:**  
  - `title`: The title of the movie to search for.

- **POST** `/addmovie/<movieid>`  
  Add a new movie with the specified movie ID.  
  **Request Body:**  
  ```json
  {
    "id": "movie_id",
    "title": "movie_title",
    "rating": "movie_rating"
  }


