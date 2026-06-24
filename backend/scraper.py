import wikipedia
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os
import time 

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
collection = client["pakshi_vectorless"]["bird_knowledge"]

species_list = [
    "Indian Peafowl", "Greater Flamingo", "Indian Roller",
    "Sarus Crane", "Great Hornbill", "Indian Eagle-owl",
    "Black Kite", "Brahminy Kite", "Crested Serpent Eagle",
    "Indian Paradise Flycatcher", "White-throated Kingfisher",
    "Common Kingfisher", "Purple Sunbird", "Asian Koel",
    "Rose-ringed Parakeet", "Alexandrine Parakeet",
    "Indian Grey Hornbill", "Malabar Pied Hornbill",
    "Red-wattled Lapwing", "Yellow-wattled Lapwing",
    "Indian Pond Heron", "Purple Heron", "Grey Heron",
    "Little Egret", "Great Egret", "Cattle Egret",
    "Painted Stork", "Asian Openbill", "Black-necked Stork",
    "Bar-headed Goose", "Indian Pitta", "Malabar Whistling Thrush",
    "Shikra", "Eurasian Hoopoe", "Indian Robin",
    "Oriental Magpie-robin", "White-breasted Waterhen",
    "Pheasant-tailed Jacana", "Bronze-winged Jacana",
    "River Tern", "Indian Skimmer", "Pied Kingfisher",
    "Stork-billed Kingfisher", "Indian Cormorant",
    "Little Cormorant", "Darter", "Asian Openbill Stork",
    "Woolly-necked Stork", "Lesser Adjutant", "Greater Adjutant"
]

inserted = 0
failed = 0

print(f"Starting scrape of {len(species_list)} species...\n")

for species in species_list:
    try:
        page = wikipedia.page(species, auto_suggest=False)
        collection.insert_one({
            "type": "fact_sheet",
            "species": species,
            "scientific_name": page.title,
            "content": page.content,
            "metadata": {
                "source": "Wikipedia",
                "url": page.url,
                "region": "India",
                "year": 2024
            },
            "created_at": datetime.utcnow()
        })
        inserted += 1
        print(f"✓ {species}")
        time.sleep(0.5)  # add this line

    except wikipedia.DisambiguationError as e:
        try:
            page = wikipedia.page(e.options[0], auto_suggest=False)
            collection.insert_one({
                "type": "fact_sheet",
                "species": species,
                "scientific_name": page.title,
                "content": page.content,
                "metadata": {
                    "source": "Wikipedia",
                    "url": page.url,
                    "region": "India",
                    "year": 2024
                },
                "created_at": datetime.utcnow()
            })
            inserted += 1
            print(f"✓ {species} (via disambiguation: {e.options[0]})")
        except Exception as e2:
            failed += 1
            print(f"✗ {species} — disambiguation failed: {e2}")
    except wikipedia.PageError:
        failed += 1
        print(f"✗ {species} — page not found")
    except Exception as e:
        failed += 1
        print(f"✗ {species} — {e}")

print(f"\nDone. Inserted: {inserted} | Failed: {failed}")