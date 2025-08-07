import googlemaps
import pandas as pd
import time

gmaps = googlemaps.Client(key='AIzaSyC--KqspPMVMZ1IvqjAKqcFuT9o21mf80U')

def get_restaurants(location, radius=5000):
    results = gmaps.places_nearby(
        location=location,
        radius=radius,
        type='restaurant'
    )
    
    restaurants = []
    for place in results['results']:
        details = gmaps.place(
            place['place_id'], 
            fields=[
                'name', 'place_id', 'geometry', 'rating', 
                'price_level', 'formatted_address', 'business_status',
                'website', 'international_phone_number', 'reviews',
            ]
        )
        
        restaurant_info = {
            'name': details['result'].get('name', 'N/A'),
            'place_id': details['result'].get('place_id', 'N/A'),
            'lat': details['result']['geometry']['location']['lat'],
            'lon': details['result']['geometry']['location']['lng'],
            'rating': details['result'].get('rating', 3.0), 
            'price_level': details['result'].get('price_level', 2), 
            'types': ', '.join(place.get('types', [])) 
        }
        restaurants.append(restaurant_info)
        time.sleep(0.2)  
    
    return pd.DataFrame(restaurants)

print("Collecting restaurant data for Moratuwa...")
moratuwa_restaurants = get_restaurants((6.795, 79.898))

# Save to CSV
output_filename = 'restaurants_raw.csv'
moratuwa_restaurants.to_csv(output_filename, index=False)
print(f"Data saved to {output_filename}")
print(moratuwa_restaurants.head()) 