import time
import requests
import database_connection as db
from bs4 import BeautifulSoup


def get_auctions(url, pages_count):
    '''
    Iterating through pages_count amount of pages of url
    Takes two arguments:
        url - base url to iterate
        pages_count - amount of pages to iterate

    Returns list with all auctions of scraped pages
    '''

    pages = []
    failed = []

    for page in range(pages_count):
        try:
            print(f"Getting {page+1} page...")
            r = requests.get(url+str(page+1))
            bs = BeautifulSoup(r.text, features="html.parser")
            auctions = bs.find("div", class_="list")

            # Checking if pages aren't the same
            if len(pages):
                if pages[-1] == auctions:
                    print("Went through all pages. Breaking...")
                    break
            pages.append(auctions)

        except Exception as e:
            print(e)
            failed.append(page)

    if len(failed):
        print("Retrying on failed pages.")
        for page in failed:
            failed_again = []
            try:
                print(f"Retrying on {page+1} page...")
                r = requests.get(url+str(page+1))
                bs = BeautifulSoup(r.text, features="html.parser")
                auctions = bs.find("div", class_="list")
                pages.append(auctions)

            except Exception as e:
                print(e)
                failed_again.append(page)

            if len(failed_again):
                print(f"Number of errors: {len(failed_again)}")
            else:
                print("Success")
    else:
        print("Success")

    

    

    return pages


def get_auction_urls(auctions):
    '''
    Scraping all urls of offers
    Takes one argument:
        auctions - element of scraped page with all auctions

    Returns list of all urls of offers from provided element
    '''

    urls = []
    for page in auctions:
        offers = page.find_all("div", class_="listRow")
        urls.extend([offer.find("a")['href'] for offer in offers])
    return urls


def get_data_from_url(url):
    '''Scraping all data from provided url'''

    r = requests.get(url, timeout=40)
    r.encoding = "utf-8"
    bs = BeautifulSoup(r.text, features="html.parser")
    offer_data = bs.find("div", class_="stdBxC")

    details = {}

    details["title"] = offer_data.find("h2", class_="presTitle")
    details["description"] = offer_data.find("p", class_="presDesc")
    details["date"] = offer_data.find("date", class_="presPubDate")
    details["location"] = offer_data.find("address", class_="presLoc")

    details["brand"] = offer_data.find("td", itemprop="brand")
    details["model"] = offer_data.find("td", itemprop="model")
    details["capacity"] = offer_data.find("th", text="Pojemność silnika")
    details["year"] = offer_data.find("td", itemprop="productionDate")
    details["transmission"] = offer_data.find("td", itemprop="vehicleTransmission")
    details["fuel"] = offer_data.find("td", itemprop="fuelType")
    details["body"] = offer_data.find("td", itemprop="bodyType")
    details["color"] = offer_data.find("td", itemprop="color")

    details = {key: ("NULL" if value is None else value.text) for key, value in details.items()}

    
    details["price"] = "NULL" if offer_data.find("p", class_="presPrice") is None else str(offer_data.find("p", class_="presPrice").text).replace(" PLN", "").replace(" ", "")
    details["km"] = "NULL" if offer_data.find("th", text="Moc silnika ") is None else offer_data.find("th", text="Moc silnika ").next_sibling.text
    details["mileage"] = "NULL" if offer_data.find("span", text="Przebieg:") is None else offer_data.find("span", text="Przebieg:").parent.b.text.replace(" KM", "").replace(" ", "")
    details["equipment"] = "NULL" if offer_data.find("p",  itemprop="description") is None else offer_data.find("p",  itemprop="description").text
    
    details["id"] = url[-12:-5]
    details["url"] = url
    details["img"] = "NULL" if offer_data.find("a", class_="ath") is None else offer_data.find("a", class_="ath").href
    return details


def add_new_offers(mysql, urls):
    '''
    Creates list of details from all urls and then adds them to database
    '''
    all_details = []
    for index, url in enumerate(urls):
        print(f"{round((index+1)/(len(urls))*100)}% - Offer: {index+1}/{len(urls)}")
        all_details.append(get_data_from_url(url)) 
    
    db.add_offer(mysql, all_details)


def update_offers(mysql, urls):
    for index, url in enumerate(urls):
        print(f"{round((index+1)/(len(urls))*100)}% - Offer: {index+1}/{len(urls)}")
        details = get_data_from_url(url)
        db.update_offer(mysql, details)


def main():
    base_url = "https://brzozowiak.pl"
    url = "https://brzozowiak.pl/samochody-osobowe/?str="
    pages_count = 200

    try:
        #Acquiring connection with database
        mysql = db.connection("localhost", "root", "")
        db.init(mysql.cursor())

        #Getting urls from database
        cu = mysql.cursor()
        cu.execute("select url from offers")
        db_urls = [url[0] for url in cu]

        #Getting auctions from provided amount of pages from url
        auctions_start = time.perf_counter()
        auctions = get_auctions(url, pages_count)
        auctions_time = time.perf_counter() - auctions_start

        #Getting offer urls from auctions
        urls_start = time.perf_counter()
        urls = [base_url+url for url in get_auction_urls(auctions)]
        urls_time = time.perf_counter() - urls_start

        #Diffrence of two arrays: 
        # urls - list of all available offers urls
        # db_urls - list of all urls in db
        new_auctions = [url for url in urls if url not in db_urls]

        #Adding new offers
        if len(new_auctions):
            print("Adding new offers to database.")
            add_start = time.perf_counter()
            add_new_offers(mysql, new_auctions)
            add_time = time.perf_counter() - add_start
            overall_time = add_time + urls_time + auctions_time
            print(f"Finished succesfuly! Adding new offers took {round(add_time, 2)} seconds!")
            print(f"Getting all auctions: {round(auctions_time, 2)} seconds")
            print(f"Getting all urls: {round(urls_time, 2)} seconds")
            print(f"Summed: {round(overall_time, 2)} seconds.")

        else:
            print("Database up to date.")

        # update_offers(mysql, urls)


    except Exception as e:
        print(e)

    

    



if __name__ == "__main__":
    main()
