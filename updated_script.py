import googlemaps
import pandas as pd
import time
import numpy as np

gmaps = googlemaps.Client(key='AIzaSyCZG6NIu2UAbKiTCzFPoljbXzxQf_VAhoY')

def get_restaurants(location, radius=5000, next_page_token=None):
    """
    Fetches restaurants for a given location and radius,
    handling pagination to retrieve up to 60 results.
    """
    all_restaurants = []
    
    results = gmaps.places_nearby(
        location=location,
        radius=radius,
        type='restaurant',
        page_token=next_page_token 
    )
    
    for place in results['results']:
        try:
            details = gmaps.place(
                place['place_id'], 
                fields=[
                    'name', 'place_id', 'geometry', 'rating', 
                    'price_level', 'formatted_address', 'business_status',
                    'website', 'international_phone_number', 'reviews',
                    'user_ratings_total'
                ]
            )
            restaurant_info = {
                'name': details['result'].get('name', 'N/A'),
                'place_id': details['result'].get('place_id', 'N/A'),
                'lat': details['result']['geometry']['location']['lat'],
                'lon': details['result']['geometry']['location']['lng'],
                'rating': details['result'].get('rating', 3.0),
                'price_level': details['result'].get('price_level', 2),
                'types': ', '.join(place.get('types', [])), 
                'formatted_address': details['result'].get('formatted_address', 'N/A'),
                'business_status': details['result'].get('business_status', 'N/A'),
                'website': details['result'].get('website', 'N/A'),
                'international_phone_number': details['result'].get('international_phone_number', 'N/A'),
                'reviews_count': details['result'].get('user_ratings_total', 0) 
            }
            all_restaurants.append(restaurant_info)
            time.sleep(0.1) 
        except Exception as e:
            print(f"Error fetching details for {place.get('name', 'Unknown Place')}: {e}")
            continue 

    return all_restaurants

def collect_restaurants_for_area(coords_list, radius=5000, output_csv_path='restaurants_colombo.csv'):
    """
    Collects restaurant data by iterating through a list of coordinates
    and saves/appends to a single CSV file.
    """
    all_collected_data = pd.DataFrame() 
    
    for i, (lat, lon) in enumerate(coords_list):
        print(f"Searching around point {i+1}/{len(coords_list)}: ({lat}, {lon})")
        
        current_location_data = []
        next_page_token = None
        
        for page_num in range(3): 
            try:
                results = gmaps.places_nearby(
                    location=(lat, lon),
                    radius=radius,
                    type='restaurant',
                    page_token=next_page_token
                )
                
                for place in results['results']:
                    try:
                        details = gmaps.place(
                            place['place_id'], 
                            fields=[
                                'name', 'place_id', 'geometry', 'rating', 
                                'price_level', 'formatted_address', 'business_status',
                                'website', 'international_phone_number', 'reviews',
                                'user_ratings_total'
                            ]
                        )
                        restaurant_info = {
                            'name': details['result'].get('name', 'N/A'),
                            'place_id': details['result'].get('place_id', 'N/A'),
                            'lat': details['result']['geometry']['location']['lat'],
                            'lon': details['result']['geometry']['location']['lng'],
                            'rating': details['result'].get('rating', 3.0),
                            'price_level': details['result'].get('price_level', 2),
                            'types': ', '.join(place.get('types', [])),
                            'formatted_address': details['result'].get('formatted_address', 'N/A'),
                            'business_status': details['result'].get('business_status', 'N/A'),
                            'website': details['result'].get('website', 'N/A'),
                            'international_phone_number': details['result'].get('international_phone_number', 'N/A'),
                            'reviews_count': details['result'].get('user_ratings_total', 0)
                        }
                        current_location_data.append(restaurant_info)
                        time.sleep(0.1) 
                    except Exception as e:
                        print(f"  Error fetching details for {place.get('name', 'Unknown Place')}: {e}")
                        continue
                
                next_page_token = results.get('next_page_token')
                if next_page_token:
                    print(f"  Found next page token for ({lat}, {lon}). Waiting for 2 seconds before next page request...")
                    time.sleep(2) 
                else:
                    break 
                    
            except googlemaps.exceptions.ApiError as e:
                print(f"  API Error for ({lat}, {lon}) - Page {page_num+1}: {e}")
                if "OVER_QUERY_LIMIT" in str(e):
                    print("  Hit query limit. Waiting for 60 seconds...")
                    time.sleep(60) 
                    continue 
                break 
            except Exception as e:
                print(f"  An unexpected error occurred for ({lat}, {lon}) - Page {page_num+1}: {e}")
                break
                
        if current_location_data:
            df_current_location = pd.DataFrame(current_location_data)
            all_collected_data = pd.concat([all_collected_data, df_current_location], ignore_index=True)
            print(f"  Collected {len(current_location_data)} restaurants from this point. Total collected: {len(all_collected_data)}")
        
        time.sleep(1)

    initial_count = len(all_collected_data)
    all_collected_data.drop_duplicates(subset=['place_id'], inplace=True)
    final_count = len(all_collected_data)
    print(f"\nRemoved {initial_count - final_count} duplicates. Final unique restaurant count: {final_count}")


    all_collected_data.to_csv(output_csv_path, index=False, encoding='utf-8-sig') 
    print(f"All unique data saved to {output_csv_path}")
    print(all_collected_data.head()) 


min_lat, max_lat = 6.75, 7.05
min_lon, max_lon = 79.8, 80.05

lat_step = 0.04
lon_step = 0.04

grid_coords = []
for lat in np.arange(min_lat, max_lat + lat_step, lat_step):
    for lon in np.arange(min_lon, max_lon + lon_step, lon_step):
        grid_coords.append((lat, lon))

print(f"Generated {len(grid_coords)} search points for Colombo District.")

collect_restaurants_for_area(grid_coords, radius=5000, output_csv_path='restaurants_colombo_district.csv')