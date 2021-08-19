A customizable web scraping finance research app written in Python in the Django framework. Choose from three default stocks (BYND, AMZN, GOOGL) to create your own stock portfolio in your profile. Click on a stock to view the latest news articles for your stock, web scraped from the latest articles on the Google News page. 

All links are clickable, live articles. To save an article to your portfolio, click "Save". To unsave an article from your profile, click "Unsave" or go back to the articles page to unsave the article. 

Your feed for each stock is also accessible by clicking the stock icon under "My Portfolio" in the dashboard page. 

News articles were web scraped using BeautifulSoup4. HTML tags were targeted, stored into the database, and organized into a visually consistent format using series of dictionaries. Web scraped URLs were stored in one URL tuple, matching articles to the user's chosen stock. 

To read more about the web scraping process, please feel free to check out this site: https://realpython.com/beautiful-soup-web-scraper-python/

