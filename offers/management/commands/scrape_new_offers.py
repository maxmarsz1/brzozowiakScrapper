from django.core.management.base import BaseCommand
from offers.models import Offer

from offers import scraper

class Command(BaseCommand):
    help = 'Scrape new offers from the website and save them to the database.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting to scrape new offers...")
        new_offers_paths = scraper.gather_new_offers_paths()
        
        if not new_offers_paths:
            self.stdout.write("No new offers found.")
            return
        
        for offer_url in new_offers_paths:
            offer_data = scraper.get_offer_data(offer_url)
            if "error_message" not in offer_data:
                scraper.save_offer_to_db(offer_data)
            else:
                self.stdout.write(f"Failed to scrape data for {offer_url}: {offer_data['error_message']}")
        
        self.stdout.write(f"Scraped and saved {len(new_offers_paths)} new offers.")
