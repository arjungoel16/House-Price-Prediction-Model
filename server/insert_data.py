from pymongo import MongoClient

TOP_100_CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego",
    "Dallas", "San Jose", "Austin", "Jacksonville", "Fort Worth", "Columbus", "San Francisco", "Charlotte",
    "Indianapolis", "Seattle", "Denver", "Washington", "Boston", "El Paso", "Nashville", "Detroit", "Oklahoma City",
    "Portland", "Las Vegas", "Memphis", "Louisville", "Baltimore", "Milwaukee", "Albuquerque", "Tucson", "Fresno",
    "Mesa", "Sacramento", "Atlanta", "Kansas City", "Colorado Springs", "Miami", "Raleigh", "Omaha", "Long Beach",
    "Virginia Beach", "Oakland", "Minneapolis", "Tulsa", "Arlington", "Tampa", "New Orleans", "Wichita", "Cleveland",
    "Bakersfield", "Aurora", "Anaheim", "Honolulu", "Santa Ana", "Riverside", "Corpus Christi", "Lexington", "Stockton",
    "St. Paul", "Cincinnati", "St. Louis", "Pittsburgh", "Greensboro", "Anchorage", "Plano", "Lincoln", "Orlando",
    "Irvine", "Newark", "Durham", "Chula Vista", "Toledo", "Fort Wayne", "St. Petersburg", "Laredo", "Jersey City",
    "Chandler", "Madison", "Lubbock", "Scottsdale", "Reno", "Buffalo", "Gilbert", "Glendale", "North Las Vegas",
    "Winston-Salem", "Chesapeake", "Norfolk", "Fremont", "Garland", "Boise", "Richmond", "Baton Rouge", "Spokane",
    "Des Moines", "Tacoma", "San Bernardino", "Modesto", "Fontana", "Santa Clarita", "Birmingham"
]

def connect_db():
    return MongoClient("mongodb://localhost:27017/").house_price_db

def insert_locations(db):
    existing_locations = set(db.locations.distinct("location"))
    new_entries = [{"location": loc} for loc in TOP_100_CITIES if loc not in existing_locations]

    if new_entries:
        db.locations.insert_many(new_entries)
        print(f"Inserted {len(new_entries)} new locations.")

def main():
    db = connect_db()
    insert_locations(db)
    print("Top 100 cities added to the database.")

if __name__ == "__main__":
    main()
