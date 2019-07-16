from bs4 import BeautifulSoup
from requests import get
from contextlib import closing
from requests.exceptions import RequestException
from csv import writer
import json
import matplotlib.pyplot as plt

#from urllib import request
#from urllib import parse

class url_to_parse:
    """
    define the website that we will parse
    """
    #url_out = ""
    def __init__(self, base = "https://www.zillow.com/", 
                 homeType = "homes/",
                 isForSale = "for_sale/",
                 location = "Ann_Arbor-MI/",
                 drawnArea = "",
                 bedNum = "3-_beds/",
                 priceRange = "",
                 blah1 = "",
                 blah2 = "",
                 isForRent = "",
                 searchArea = "",
                 isPotentialListing = ""):
        self.base = base
        self.homeType = homeType # "homes/"
        self.isForSale = isForSale # "for_sale/"
        self.location = location # "Ann-Arbor-MI/"
        self.drawnArea = drawnArea # "8097_rid/"
        self.bedNum = bedNum # "3-_beds/"
        self.priceRange = priceRange # "184000-636000_price/"
        self.blah1 = blah1 # "702-2427_mp/"
        self.blah2 = blah2 # "mostrecentchange_sort/"
        self.isForRent = isForRent # globalrelevanceex_sort/" # 1_fr/ ?
        self.searchArea = searchArea # "42.396333,-83.576775,42.183758,-83.945847_rect/"
        self.isPotentialListing = isPotentialListing # "0_mmm/"
        self.url = (self.base + self.homeType + self.isForSale +
                                self.location + self.drawnArea + self.bedNum +
                                self.priceRange + self.blah1 + self.blah2 +
                                self.searchArea)
    def getURL(self):
        return self.url 

    def promt_for_input(self):
        pass

    def show_website(self):
        print(self.url)

def parse_url():
    pass

def page_read():
    url_str = url_to_parse().getURL()
    # print(url_str)
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
    }
    response = get(url_str,headers=headers)
    html = BeautifulSoup(response.content,'lxml')
    # print(html.prettify())
    list_results = html.find(class_ = "photo-cards photo-cards_wow")
    listings = list_results.find_all("li")
    home_details = {}
    address_list = []
    link_list = []
    price_list = []
    dim_list = []
    for home_html in listings:
        address = home_html.find(class_ = "list-card-addr")
        if address != None:
            if address not in home_details["address"]:
                home_details["address"] = home_details["address"].append(address)
            else:
                home_details["address"]
            home_details["address"] = address.get_text()
        link = home_html.find("a")
        hyperlink = link.attr['href']
        if link != None:
            # if home_details["link"] == []
            home_details["link"] = hyperlink
        price = home_html.find(class_ = "list-card-price")
        if price != None:
            home_details["price"] = price.get_text()
        home_dimensions = home_html.find(class_ = "list-card-details").find_all("li")
        home_details["dimensions"] = (home_dimensions[0].get_text() + "beds" + home_dimensions[1].get_text() + "baths" + home_dimensions[2].get_text() + "sqft")
    # print(listings)

def main():
    page_read()

if __name__ == "__main__":
    main()

