import requests
from bs4 import BeautifulSoup


BASE_URL = "https://brzozowiak.pl"
MOTO_URL = BASE_URL + "/samochody-osobowe/?str="


def gather_offers_urls_from_page(page_number: int):
    url = MOTO_URL + str(page_number)
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    page_offers = soup.find_all("a", class_="aImgT")

    if not page_offers:
        print(f"No offers found on page {page_number}.")
        return []

    offers_urls = [offer["href"] for offer in page_offers]
    print(f"Found {len(offers_urls)} offers on page {page_number}.")

    return offers_urls


def gather_all_offers_urls(max_pages: int = 300):
    all_offers_urls = []
    previous_page_urls = []

    for page in range(1, max_pages + 1):
        print(f"Gathering offers from page {page}...")
        offers_urls = gather_offers_urls_from_page(page)

        if not offers_urls or offers_urls == previous_page_urls:
            break

        all_offers_urls.extend(offers_urls)
        previous_page_urls = offers_urls

    print(f"Total offers URLs gathered: {len(all_offers_urls)}")
    return all_offers_urls


def get_offer_data(path):
    offer_url = BASE_URL + path
    response = requests.get(offer_url, timeout=40)
    response.raise_for_status()
    response.encoding = "utf-8"
    bs = BeautifulSoup(response.text, features="html.parser")
    offer_data = bs.find("div", class_="stdBxC")

    if not offer_data:
        return {"error": "Offer data container not found"}

    details = {}

    selectors = {
        "title": ("h2", {"class": "presTitle"}),
        "description": ("p", {"class": "presDesc"}),
        "date": ("date", {"class": "presPubDate"}),
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
        found_element = offer_data.find(tag, attrs)
        details[key] = clean_text(found_element)


    details["price"] = "NULL"
    price_element = offer_data.find("p", class_="presPrice")
    if price_element:
        details["price"] = price_element.text.replace(" PLN", "").replace(" ", "").strip()

    details["capacity"] = "NULL"
    capacity_element = offer_data.find("th", string="Pojemność silnika")
    if capacity_element and capacity_element.next_sibling:
        details["capacity"] = capacity_element.next_sibling.text.strip()
    
    details["hp"] = "NULL"
    km_element = offer_data.find("th", string="Moc silnika ")
    if km_element and km_element.next_sibling:
        details["hp"] = km_element.next_sibling.text.strip()
    
    details["mileage"] = "NULL"
    mileage_element = offer_data.find("span", string="Przebieg:")
    if mileage_element and mileage_element.parent and mileage_element.parent.b:
        details["mileage"] = mileage_element.parent.b.text.replace(" KM", "").replace(" ", "").strip()


    details["id"] = offer_url[-12:-5]
    details["url"] = offer_url
    
    # Image URL
    details["img"] = "NULL"
    img_element = offer_data.find("a", class_="ath")
    if img_element and img_element.get("href"):
        details["img"] = img_element["href"]

    return details


def clean_text(element, default="NULL"):
    """
    Extracts text from a BeautifulSoup element and returns a default
    value if the element is None.
    """
    if element is None:
        return default
    return element.text.strip()


if __name__ == "__main__":
    offers = gather_offers_urls_from_page(1)
    # gather_all_offers_urls(10)
    print(get_offer_data(offers[0]))