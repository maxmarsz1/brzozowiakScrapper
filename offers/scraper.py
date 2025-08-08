import requests
from bs4 import BeautifulSoup
import django.core.exceptions

import offers.utils as utils

try:
    from offers.models import Offer, OfferFailed
except django.core.exceptions.ImproperlyConfigured:
    print("Running this script directly doesn't allow using Django models")


BASE_URL = "https://brzozowiak.pl"
MOTO_URL = BASE_URL + "/samochody-osobowe/?str="


def gather_offers_paths_from_page(page_number: int):
    """
    Gather offer paths from a specific page of the website.
    :param page_number: Page number to scrape
    :return: List of offer paths
    """

    url = MOTO_URL + str(page_number)
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    page_offers_links = soup.find_all("a", class_="aImgT")

    if not page_offers_links:
        print(f"No offers found on page {page_number}.")
        return []

    offers_paths = [offer_link["href"] for offer_link in page_offers_links]
    print(f"Found {len(offers_paths)} offers on page {page_number}.")

    return offers_paths


def gather_all_offers_paths(max_pages: int = 300):
    """
    Gather all offers paths from the website up to a specified number of pages.
    :param max_pages: Maximum number of pages to scrape
    :return: List of offer paths
    """

    all_offers_paths = []
    previous_page_paths = []

    for page in range(1, max_pages + 1):
        print(f"Gathering offers from page {page}...")
        offers_urls = gather_offers_paths_from_page(page)

        if not offers_urls or offers_urls == previous_page_paths:
            break

        all_offers_paths.extend(offers_urls)
        previous_page_paths = offers_urls

    print(f"Total offers paths gathered: {len(all_offers_paths)}")
    return all_offers_paths


def gather_all_new_offers_paths(max_pages: int = 300):
    """
    Gather all new offers paths from the website up to a specified number of pages.
    :param max_pages: Maximum number of pages to scrape
    :return: List of offer paths
    """

    all_offers_paths = []
    previous_page_paths = []

    for page in range(1, max_pages + 1):
        print(f"Gathering offers from page {page}...")
        offers_paths = gather_offers_paths_from_page(page)

        if not offers_paths or offers_paths == previous_page_paths:
            break

        all_offers_paths.extend(offers_paths)
        previous_page_paths = offers_paths
    
    all_new_offers_paths = utils.filter_new_paths(all_offers_paths)

    print(f"Total new offers paths gathered: {len(all_new_offers_paths)}")
    return all_new_offers_paths


def gather_new_offers_paths():
    """
    Gather new offers paths that are not already in the database.
    :return: List of new offer paths
    """

    page_number = 1
    new_path_on_page = True

    new_offers_paths = []

    while new_path_on_page:
        print("Gathering new offers from page ", page_number)
        page_offers_paths = gather_offers_paths_from_page(page_number)
        new_found_offers_paths = utils.filter_new_paths(page_offers_paths)

        print(f"Found {len(new_found_offers_paths)} new offers on page {page_number}.")
        
        if len(new_found_offers_paths) == 0:
            new_path_on_page = False    #When all paths found on page already exist in db
        else:
            new_offers_paths.extend(new_found_offers_paths)
            page_number += 1

    return new_offers_paths



def get_offer_data(path):
    """
    Scrape offer data from the given path.
    :param path: Relative path to the offer page
    :return: Dictionary containing offer data
    """

    try:
        offer_url = BASE_URL + path
        response = requests.get(offer_url, timeout=40)
        response.raise_for_status()
        response.encoding = "utf-8"
        bs = BeautifulSoup(response.text, features="html.parser")
        offer_data_container = bs.find("div", class_="stdBxC")

        if not offer_data_container:
            return {"error": "Offer data container not found"}

        offer_data = {}

        selectors = {
            "title": ("h2", {"class": "presTitle"}),
            "description": ("p", {"class": "presDesc"}),
            "location": ("address", {"class": "presLoc"}),
            "brand": ("td", {"itemprop": "brand"}),
            "model": ("td", {"itemprop": "model"}),
            "year": ("td", {"itemprop": "productionDate"}),
            "transmission": ("td", {"itemprop": "vehicleTransmission"}),
            "fuel": ("td", {"itemprop": "fuelType"}),
            "body": ("td", {"itemprop": "bodyType"}),
            "color": ("td", {"itemprop": "color"}),
            "equipment": ("p", {"itemprop": "description"}),
        }

        for key, (tag, attrs) in selectors.items():
            found_element = offer_data_container.find(tag, attrs)
            offer_data[key] = utils.clean_text(found_element)

        offer_data["date"] = "NULL"
        date_element = offer_data_container.find("date", class_="presPubDate")
        if date_element:
            offer_data["date"] = date_element.text.replace(".", "-").strip()

        offer_data["price"] = 0
        price_element = offer_data_container.find("p", class_="presPrice")
        if price_element:
            offer_data["price"] = price_element.text.replace(" PLN", "").replace(" ", "").strip()

        offer_data["capacity"] = "NULL"
        capacity_element = offer_data_container.find("th", string="Pojemność silnika")
        if capacity_element and capacity_element.next_sibling and capacity_element.next_sibling.text != "---":
            offer_data["capacity"] = capacity_element.next_sibling.text.strip()
        
        offer_data["hp"] = "NULL"
        hp_element = offer_data_container.find("th", string="Moc silnika ")
        if hp_element and hp_element.next_sibling and hp_element.next_sibling.text != "---":
            offer_data["hp"] = hp_element.next_sibling.text.strip()
        
        offer_data["mileage"] = "NULL"
        mileage_element = offer_data_container.find("span", string="Przebieg:")
        if mileage_element and mileage_element.parent and mileage_element.parent.b and "---" not in mileage_element.parent.b.text:
            offer_data["mileage"] = mileage_element.parent.b.text.replace("km", "").replace(" ", "").strip()

        offer_data["offer_id"] = offer_url[-12:-5]
        offer_data["path"] = path
        
        offer_data["img"] = "NULL"
        img_element = offer_data_container.find("a", class_="ath")
        if img_element and img_element.get("href"):
            offer_data["img"] = img_element["href"]

        return offer_data
        
    except Exception as e:
        print(f"Error getting data from {path}: {e}")
        offer_data = {
            "path": path,
            "error_message": str(e)
        }
        utils.save_failed_offer(offer_data)
        return offer_data


def save_offer_to_db(offer_data):
    """
    Save offer data to the database, creating a new Offer object if it doesn't exist.
    :param offer_data: Dictionary containing offer data
    :return: True if a new Offer was created, False if it already exists
    """

    try:
        offer, created = Offer.objects.get_or_create(
            path=offer_data["path"],
            defaults={
                "offer_id": offer_data["offer_id"],
                "title": offer_data["title"],
                "price": int(offer_data["price"]) if offer_data["price"] != "NULL" else None,
                "image": offer_data["img"],
                "description": offer_data["description"],
                "date": offer_data["date"],
                "equipment": offer_data["equipment"],
                "brand": offer_data["brand"],
                "model": offer_data["model"],
                "year": int(offer_data["year"]) if offer_data["year"] != "NULL" else None,
                "fuel": offer_data["fuel"],
                "hp": offer_data["hp"],
                "color": offer_data["color"],
                "body": offer_data["body"],
                "transmission": offer_data["transmission"],
                "mileage": int(offer_data["mileage"]) if offer_data["mileage"] != "NULL" else None,
                "capacity": offer_data["capacity"],
                "location": offer_data["location"]
            }
        )
        if created:
            print(f"Offer {offer.title} saved successfully.")
        else:
            print(f"Offer {offer.title} already exists in the database.")

        return created
    except Exception as e:
        print(f"Error saving offer({offer_data['path']}): {e}")



if __name__ == "__main__":
    gather_new_offers_urls()

    