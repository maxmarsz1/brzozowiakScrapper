from django.core.management.base import BaseCommand
from offers.models import Offer

from offers import scraper

class Command(BaseCommand):
    help = 'Scrape all offers from the website and save them to the database.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting to scrape offers...")
        offers_paths = scraper.gather_all_offers_paths()
        created_offers = 0
        
        if not offers_paths:
            self.stdout.write("No offers found.")
            return
        
        for offer_path in offers_paths:
            offer_data = scraper.get_offer_data(offer_path)
            if "error_message" not in offer_data:
                if scraper.save_offer_to_db(offer_data):
                    created_offers += 1
            else:
                self.stdout.write(f"Failed to scrape data for {offer_path}: {offer_data['error_message']}")
        
        self.stdout.write(f"Scraped and saved {len(offers_paths)} offers.")
