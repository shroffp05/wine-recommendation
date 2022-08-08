from requests import get
from bs4 import BeautifulSoup
import datetime
import pandas as pd
import urllib.request
import requests
import re

def filter_wine_links(wine_links):
    output = []
    for wines in wine_links:
        if "category" not in str(wines.get('href')):
            output.append(wines.get('href'))
            
    return output 

def scrape_wine_links(base_url, min_page_number, max_page_number, proxies, header):
    wine_pages_to_mine = []
    for page_number in range(min_page_number, max_page_number):
        url_to_mine = base_url + str(page_number)
        print(url_to_mine)
        r = requests.Session()
        r.proxies = proxies
        r.headers = header
        try:
            response = r.get(url_to_mine, headers=header)
            soup = BeautifulSoup(response.content, 'html.parser')
            all_wine_links = soup.find_all("a", href=re.compile("review/"))
            all_wine_links = filter_wine_links(all_wine_links)
            #all_wine_links = [a.get('href') for a in all_wine_links]
            wine_pages_to_mine.extend(all_wine_links)
        except:
            continue

    series_wine_pages = pd.Series(wine_pages_to_mine)
    series_wine_pages.to_csv('wine_pages_to_mine.csv')
    return wine_pages_to_mine


class WineInfoScraper:

    def __init__(self, wine_page_to_mine, proxies, header):
        self.page = wine_page_to_mine
        self.proxies = proxies
        self.user_agent = header


    def get_soup_wine_page(self):

        r = requests.Session()
        r.proxies = self.proxies
        r.headers = self.user_agent
        wine_review_response = r.get(self.page, headers=self.user_agent)

        wine_review_soup = BeautifulSoup(wine_review_response.content, 'html.parser')
        return wine_review_soup


    def get_wine_name(self, soup):
        wine_name_raw = soup.find("h1")
        wine_name_clean = wine_name_raw.text
        print(wine_name_clean)
        return wine_name_clean
    
    def scrape_all_info(self):
        wine_info_dict = {}
        wine_review_soup = self.get_soup_wine_page()
    
        wine_info_dict['Name'] = self.get_wine_name(wine_review_soup)
        
        wine_attributes = wine_review_soup.find_all("td", class_="rcr-data-label")
        
        for attrs in wine_attributes:
            if len(str(attrs.text).strip()) > 0:
                if str(attrs.text).strip() == 'Price':
                    key = str(attrs.text).strip()
                    value = str(attrs.next_sibling.next_sibling.text).strip().split()[0]
                else:
                    key = str(attrs.text).strip()
                    value = str(attrs.next_sibling.next_sibling.text).strip()
                
                wine_info_dict[key] = value
        
        for link in wine_review_soup.find_all('h2'):
            key = str(link.next_element).strip()

            if key != "Related Reads":

                if "Review" in key:
                    val = ""
                    for value in link.next_sibling.next_sibling.contents:
                        val = val + str(value.string).strip()
                    wine_info_dict["Review"] = val
                else:
                    val = ""
                    for value in link.next_sibling.next_sibling.contents:
                        if len(str(value.string)) > 0:
                            val = val + str(value.string).strip()
                    wine_info_dict[key] = val

        wine_info_dict['image'] = wine_review_soup.find("link", href=re.compile("jpg")).get("href")
        wine_info_dict['link'] = self.page
        return wine_info_dict


def mine_all_wine_info(base_url, min_page_number, max_page_number):
    
    all_wine_links = scrape_wine_links(base_url=base_url,
                                       min_page_number=min_page_number,
                                       max_page_number=max_page_number,
                                       proxies={'http': 'http://user:pass@13.59.204.225:8080'},
                                       header={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})

    all_wine_info = []
    all_wine_links = list(set(all_wine_links))
    print(len(all_wine_links))
    for link in all_wine_links:
        #scraper = WineInfoScraper(wine_page_to_mine=link, proxies={'http': 'http://user:pass@13.59.204.225:8080'}, header={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
        #wine_info = scraper.scrape_all_info()
        #all_wine_info.append(wine_info)
        
        try:
            scraper = WineInfoScraper(wine_page_to_mine=link, proxies={'http': 'http://user:pass@13.59.204.225:8080'}, header={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
            wine_info = scraper.scrape_all_info()
            all_wine_info.append(wine_info)
            print(wine_info)
        except:
            continue
        
    
    full_wine_info_dataframe = pd.DataFrame(all_wine_info)
    print(full_wine_info_dataframe.head())
    fileName = 'all_scraped_wine_info.csv'
    full_wine_info_dataframe.to_csv(fileName)


if __name__ == "__main__":
	base_url = 'https://vinepair.com/review/category/wine/?fwp_paged='
	min_page_number = 1
	max_page_number = 51 
	mine_all_wine_info(base_url, min_page_number, max_page_number)