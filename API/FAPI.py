from flask import Flask, request, jsonify
import folium
from folium import plugins
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import numpy as np
import pandas as pd

app = Flask(__name__)

def get_coordinates(location):
    geolocator = Nominatim(user_agent="my-app")  # Create a geolocator object
    location = geolocator.geocode(location)  # Get the coordinates of the location
    return location.latitude, location.longitude

@app.route('/api/top_restaurants', methods=['GET'])
def get_top_restaurants_api():
    dish_name = request.args.get('dish_name')
    location = request.args.get('location')

    if not dish_name or not location:
        return jsonify({'error': 'Please provide both dish_name and location parameters.'}), 400

    location_with_city = location + ', Bengaluru, India'
    location_coords = get_coordinates(location_with_city)

    df = pd.read_csv("API.csv")

   # Filter the DataFrame based on the dish name
    filtered_df = df[df['liked_food_from_review'].apply(lambda x: dish_name in x)].copy()

    # Drop rows with missing coordinates
    filtered_df = filtered_df.dropna(subset=['latitude', 'longitude'])

    # Calculate the distances from the specified location
    filtered_df['distance'] = filtered_df.apply(lambda row: geodesic((row['latitude'], row['longitude']), location_coords).km, axis=1)

    # Sort the DataFrame by distance in ascending order
    sorted_df = filtered_df.sort_values('rank')

    # Filter the top 3 restaurants within a 2km radius
    top_restaurants = sorted_df[sorted_df['distance'] <= 5.0].head(3)

    # Get the restaurant names and addresses
    restaurant_names = top_restaurants['name'].tolist()
    restaurant_addresses = top_restaurants['address'].tolist()

    # Create a list of dictionaries with restaurant names and addresses
    results = [{'name': name, 'address': address} for name, address in zip(restaurant_names, restaurant_addresses)]

    return jsonify({'top_restaurants': results})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
