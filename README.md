
# Data Mining Project

This is a web scraping project for scraping metadata regarding articles from CoinDesk website.
CoinDesk is a news site specializing in bitcoin and digital currencies. Shakil Khan founded the site, which covers sections like Business, Technology, Regulation, and more.
#### Purpose:
The purpose of this project is to collect data that, when analyzed further, may reveal trends regarding articles.
Upon entering the desired section and the number of scroll downs (each scroll-down will add about 9 articles), the program will output the metadata about the relevant articles.
On each article, the following metadata is collected:
The title, author, date, tags, and a short description.

#### Technology:
There are two main technologies in this project:

Beautiful Soup - 
Beautiful Soup is a Python package for parsing HTML and XML documents. It creates a parse tree for parsed pages that can be used to extract data from HTML, which is useful for web scraping. We scraped the metadata of the articles using it.

Selenium - 
Selenium WebDriver is a collection of open source APIs which are used to automate the testing of a web application. We used it to automate the CoinDesk website navigation and make scraping faster.


## Run Locally

Prerequisites:
For Chrome users, WebDriver is available from this website:
https://chromedriver.chromium.org/downloads

Clone the project

```bash
  git clone https://github.com/AkivaCrouse/Datamining-Project.git
```

Go to the project directory

```bash
  cd venv
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Run the program

```bash
  Coindesk-Scraper.py [ENTER SECTION] [ENTER REQUIRED NUMBER OF ARTICLES]
```

  
## Acknowledgements

 - [Selenium with Python](https://selenium-python.readthedocs.io/)
 - [Beautiful Soup Tutorial](https://www.dataquest.io/blog/web-scraping-python-using-beautiful-soup/)
 - [ChromeDriver](https://chromedriver.chromium.org/getting-started)
 - [CoinDesk Website](https://www.coindesk.com/)

  
## Authors

- [@AkivaCrouse](https://github.com/AkivaCrouse)
- [@Ohad95](https://www.github.com/Ohad95)
  
