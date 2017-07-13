import re

import requests
from bs4 import BeautifulSoup

from objects.tender import Tender


class Scraper(object):
    def __init__(self, url):
        html = requests.get(url)
        self.soup = BeautifulSoup(html.text, 'lxml')
        html.close()

    def get_tenders(self):
        wpb_wrapper_tag = self.soup.find(class_='wpb_wrapper')
        wpb_content_element_tags = wpb_wrapper_tag.find_all(
            class_='wpb_content_element')
        tenders = []
        for element in wpb_content_element_tags:
            temp = Tender()
            temp.pdf_url = element.find('a').get('href')

            table = element.find('table')

            data = []
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                data.append(cols[1].text)

            temp.title, temp.number, temp.closing_date = data
            tenders.append(temp)

        return tenders

    def find_tender_by_number(self, tender_number):
        for tender in self.get_tenders():
            if tender.number == tender_number:
                return tender
        return None

    def search_tenders(self, query):
        results = []
        search_terms = query.lower().split(" ")
        number_of_terms = len(search_terms)
        for tender in self.get_tenders():
            terms_matched = 0
            for term in search_terms:
                regex = re.compile(term)
                if regex.search(tender.title.lower()):
                    terms_matched += 1
            if terms_matched == number_of_terms:
                results.append(tender)

        return results
