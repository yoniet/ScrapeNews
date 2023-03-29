
import pandas as pd
from pip._vendor import requests
from bs4 import BeautifulSoup as bs
import datetime
import os
import re

FilePath = os.getcwd()
print(FilePath)
print(os.listdir(FilePath))
dateCurrent = datetime.date.today()

today = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
today = str(today)
today = today

time_re = re.compile(r'^(([01]\d|2[0-3]):([0-5]\d)|24:00)$')

def is_time_format(s):
    return bool(time_re.match(s))

name_file = 'art'+today+'e.xlsx'
name_sheet = 'sheet_articles'
index_sheet = True

# Database for all article before insert excel
database_today = []
database_title = []
database_description = []
database_domain = []
database_text = []
database_img = []
database_tag = []

links_for_category = []
# You can remove or add categories
List_of_categories = [
    'פוליטי',
    'ביטחוני',
    'פלילי',
    'בעולם',
    'ספורט',
    'כלכלה',
    'בריאות',
    'אוקראינה',
    'פנים',
]

# Clean text from "new line"
def clean_text(text):
    newList = []
    for t in text:
        newList.append(t.replace("\n", ""))
    return newList

def write_to_file(data_today, data_title, data_description,
                  data_domain, data_text, data_img, data_tag):

    ARTICLES = {
        'Date': [t for t in data_today],
        'Title': [t for t in data_title],
        'Description': [t for t in data_description],
        'Domain': [t for t  in data_domain],
        'Text_Article': [t for t in data_text],
        'Images_Link': [t for t in data_img],
        'Tag': [t for t in data_tag]
    }
    # dataFrame Date, Title, Description, Domain, Text_Article, Images_Link
    df = pd.DataFrame(ARTICLES)
    with pd.ExcelWriter(name_file) as writer:
        df.to_excel(writer, sheet_name=name_sheet, index=False)

def remove_duplicates(list_argument):
    return list(dict.fromkeys(list_argument))


def correct_url(correct):
    if "http" in correct:
        return correct
    else:
        correct = 'https://www.n12.co.il/' + correct
        return correct


def get_article(link, domain):
    text_data = []
    tags = []
    imgs = []
    source = requests.get(correct_url(link["href"])).text
    soup = bs(source, "html.parser")
    title = soup.find("h1").text
    description = soup.find("h2").text
    article_page = soup.find(class_="article-body")
    article_body = article_page.find_all("p")
    # Get texts article
    for article_text in article_body:
        text_data.append(article_text.text)
    text = clean_text(text_data)
    text = "".join(text).rstrip()
    # Get tags article
    tags_article = article_page.find(class_="tags")
    for tag in tags_article.find_all('a'):
        tags.append(tag.text)
        tags.append(" | ")
    tag = clean_text(tags)
    tag = "".join(tag).rstrip()
    # Get imgs article
    imgs_article = article_page.find_all("img")
    for img in imgs_article:
        imgs.append(img["src"])
        imgs.append(" | ")
    img = clean_text(imgs)
    img = "".join(img)
  
    database_today.append(dateCurrent)
    database_title.append(title)
    database_description.append(description)
    database_domain.append(domain)
    database_text.append(text)
    database_img.append(img)
    database_tag.append(tag)
    
def get_articles_of_category(link):
    source = requests.get(correct_url(link["href"])).text
    soup = bs(source, "html.parser")
    domain = ''
    try:
        domain = soup.find("h1").text
        main_item = soup.find(class_="mainItem")
        for link_article in main_item.find_all("li"):
            link = link_article.find("strong").find("a")
            span = link_article.find_all("span")
            if is_time_format(span[2].text):
                get_article(link, domain)
                
        regular_item = soup.find(class_ = "regular")
        for link_article in regular_item.find_all("li"):
            link = link_article.find("strong").find("a")
            span = link_article.find_all("span")
            if is_time_format(span[2].text):
                get_article(link, domain)
    except:
        ("Not article")

url = 'https://www.n12.co.il/'
source = requests.get(url).text
soup = bs(source, "html.parser")
x = soup.find(class_="menu responsive v-2020")

for each in x.find_all('li'):
    href_link = each.find("a")
    if href_link is None:
        continue
    elif href_link.text != "":
        links_for_category.append(href_link)
    else:
        continue

links_for_category = remove_duplicates(links_for_category)
for link in links_for_category:
    if link.text in List_of_categories:
        get_articles_of_category(link)
        
    write_to_file(database_today,database_title, database_description,
                  database_domain, database_text, database_img, database_tag)
