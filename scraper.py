# Web Scraper #
# Started: 14.Mar.2021#
import os
import string
from typing import Optional, Dict

import requests
from bs4 import BeautifulSoup


def main():
    initial_directory = os.getcwd()
    print("Current directory:", initial_directory)
    # url_link = input("Input the URL:")
    page_num = int(input("Enter Nature article catalog page number: "))
    article_type_request = input("Enter article type: ")
    for i in range(1, page_num+1):
        os.chdir(initial_directory)
        url_link = f"https://www.nature.com/nature/articles?searchType=journalSearch&sort=PubDate&page={i}"
        make_page_dir(i)
        operation = check_status(page_num, url_link, article_type_request)
        print(f"Output: {operation}")
        os.chdir(initial_directory)
        print(f"Page {i} done.\n")


def check_status(page_num, url, request_type):
    response = requests.get(url)
    status = response.status_code
    try:
        if not (status < 200 or status > 299):
            return get_article(url, request_type)
        else:
            print(f"The URL returned {response.status_code}!")
    except (KeyError, TypeError):
        print(f"The URL returned {response.status_code}!")


def get_article(url, request_type):
    output_list = []
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    articles = soup.find_all('article')
    for article in articles:
        if article.find('span', {'class': 'c-meta__type'}).string == request_type:
            article_name = article.find('a', {'data-track-label': 'link'}).string
            print(f"Article [{article_name}] found.")
            article_url = f"https://www.nature.com{article.find('a').get('href')}"
            filename_cleaner: dict[int, Optional[int]] = str.maketrans(string.punctuation + " ", "_" * (len(string.punctuation) + 1),
                                             "!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~")
            article_filename = article_name.translate(filename_cleaner)
            output_list.append(article_filename + ".txt")
            save_content(article_name, article_url, article_filename)

    print("Article scraping done.")
    return output_list


def save_content(article_name, article_url, article_filename):
    article_content = []
    article_response = requests.get(article_url)
    article_soup = BeautifulSoup(article_response.content, 'html.parser')
    article_body = None
    if article_soup.find('div', {'class': 'article__body cleared'}):
        article_body = article_soup.find('div', {'class': 'article__body cleared'})
    elif article_soup.find('div', {'class': 'article-item__body'}):
        article_body = article_soup.find('div', {'class': 'article-item__body'})
    else:
        return "Body not found."
    for line in article_body.find_all(['p', 'h2']):
        article_content.append(line.text)
        article_text = "".join(article_content)
        with open(f"{article_filename}.txt", "wb", ) as output:
            output.write(article_text.encode('utf8'))
    print(f"[{article_name}] has been successfully saved.\n")


def make_page_dir(i):
    if os.path.isdir(f"Page_{i}"):
        print(f"Directory for Page {i} articles already exists.")
        os.chdir(f"Page_{i}")
    else:
        print(f"Making directory for Page {i} articles.")
        os.mkdir(f"Page_{i}")
        os.chdir(f"Page_{i}")


if __name__ == '__main__':
    main()
