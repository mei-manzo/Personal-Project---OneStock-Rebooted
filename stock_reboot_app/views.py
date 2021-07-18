from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from .models import *
from django.db.models import Count
import requests, urllib.parse
from bs4 import BeautifulSoup

url_tuple = (
    ["GOOGL", 'https://www.google.com/search?q=google&rlz=1C1CHBF_enUS898US898&biw=1536&bih=534&tbm=nws&sxsrf=ALeKk02sMEdIqbvRgGDYGxQnCwwJCVwGfA%3A1625683430806&ei=5vXlYIfZMInM-gSr853ABA&oq=google&gs_l=psy-ab.3..0i433i131i67k1l2j0i433i67k1l2j0i433i131i67k1j0i433i67k1j0i433i131i67k1j0i433k1j0i433i67k1j0i67k1.28577185.28577714.0.28578680.6.3.0.2.2.0.265.549.0j2j1.3.0....0...1c.1.64.psy-ab..2.4.389...0i433i131k1.0.5KINMOYh_Pg', 'https://www.google.com/finance/quote/GOOGL:NASDAQ'],
    ["AMZN", 'https://www.google.com/search?q=amazon&rlz=1C1CHBF_enUS898US898&biw=1536&bih=754&tbm=nws&sxsrf=ALeKk00UgnFgnWgj2T_wGxHHJw-6YfiTVw%3A1625724146440&ei=8pTmYKenGsz_-wSFiJL4Dw&oq=amazon&gs_l=psy-ab.3..0i433i131i67k1l2j0i67k1j0i433i131k1j0i433i131i67k1j0i433k1j0i67k1j0i433i131k1j0i433k1l2.2159.4399.0.4666.17.8.0.3.3.0.127.605.3j3.7.0....0...1c.1.64.psy-ab..9.7.414.0..0i433i67k1.300.dJxWc9207vM', 'https://www.google.com/finance/quote/AMZN:NASDAQ'],
    ["BYND", 'https://www.google.com/search?q=beyond+meat&rlz=1C1CHBF_enUS898US898&sxsrf=ALeKk00IH9jp1Kz5-LSyi7FUB4rd6--_hw:1624935518812&source=lnms&tbm=nws&sa=X&ved=2ahUKEwicqIbD7LvxAhVWo54KHXgRA9oQ_AUoAXoECAEQAw&biw=1536&bih=754', 'https://www.google.com/finance/quote/BYND:NASDAQ?sa=X&ved=2ahUKEwjJuJGoyr7xAhXVkWoFHX7jA6cQ_AUoAXoECAEQAw']
)

def index(request):
    return render(request, "index.html")

def check_registration(request):
    errors = User.objects.basic_validator(request.POST)
    email = request.POST['email']
    if request.method == "GET":
        return redirect('/')
    elif len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/')
    #changed to check len of dictionary
    elif len(User.objects.filter(email=email)) >= 1:
        messages.error(request, "Email is already in use")
        return redirect('/')
    else:
        hashed_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        new_user = User.objects.create(first_name = request.POST['first-name'], last_name = request.POST['last-name'], username = request.POST['username'], email = request.POST['email'], password = hashed_pw)
        request.session['user_id'] = new_user.id
        return redirect('/success')

def check_login(request):
    if request.method == "GET":
        return redirect ("/")
    else:
        errors = User.objects.login_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/')
        this_user = User.objects.filter(email=request.POST['email'])
        request.session['user_id'] = this_user[0].id
        return redirect('/success')

def success(request):
    if 'user_id' not in request.session:
        return redirect('/')
    this_user = User.objects.filter(id = request.session['user_id'])
    portfolio = Stock.objects.filter(user=User.objects.get(id = request.session['user_id']))
    number_of_stocks = len(Stock.objects.filter(user=User.objects.get(id = request.session['user_id'])))
    context = {
        "current_user" : this_user[0].first_name,
        "portfolio": portfolio,
        "number_of_stocks": number_of_stocks,
        }
    return render(request, "dashboard.html", context)

def feed_parser(request, id):
    #check if user in session
    if 'user_id' not in request.session:
        return redirect('/')
    this_user = User.objects.filter(id = request.session['user_id'])
    #get stock we're looking at
    this_stock = Stock.objects.filter(id = id)
    #get URL for webscraping
    for t in url_tuple:
        if this_stock[0].stock_name == t[0]:
            URL = t[1]
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    #headers data parsed below:
    headers = soup.find_all('div', class_='BNeawe vvjwJb AP7Wnd')
    header_dict = []
    for h in headers: 
        head = h.text
        head=head.replace("?", "").replace("/", "-") 
        header_dict.append(head)
    links = soup.find_all('a', style='text-decoration:none;display:block')
    link_dict = []
    full_links = []
    #get all links from page using 'a' tag
    for link in soup.find_all('a'):
        input_string = str(link.get('href'))
        input_string=input_string.replace('/url?q=', "")
        link_dict.append(input_string)
    #get links in index that we want
    for x in range (16, 36, 2):
        full_links.append(link_dict[x])
    corrected_link=[]
    #add clickable links
    for string in full_links:
        split_string = string.split("&sa=", 1)
        substring = split_string[0]
        corrected_link.append(substring)
    consolidated = {} 
    for x in range (0, 10, 1):
            consolidated[(header_dict[x])] = corrected_link[x]
    for x in range (0, 10, 1): #investigate range, make sure catching correct headers
        if len(Article.objects.filter(headliner = header_dict[x], article_user = this_user[0])) >= 1:
            pass
        else: 
            Article.objects.create(headliner = (header_dict[x]), hyperlink= corrected_link[x], article_user = this_user[0], stock = this_stock[0])
    user_saved_articles = Article.objects.filter(stock_id = id, article_user = this_user[0], saved = True)
    saved_headlines = []
    stock_name = this_stock[0].stock_name
    for article in user_saved_articles:
        saved_headlines.append(article.headliner)
    context = {
            "current_user" : this_user[0].first_name,
            "header_dict": header_dict,
            "corrected_link": corrected_link,
            "consolidated": consolidated,
            "user_saved_articles": user_saved_articles,
            "saved_headlines": saved_headlines,
            "stock_name": stock_name,
        }
    return render(request, "feed.html", context)

def stats(request):
    if 'user_id' not in request.session:
        return redirect('/')
    this_user = User.objects.filter(id = request.session['user_id'])
    this_stock = Stock.objects.filter(user_id = request.session['user_id'])
    progress_dict = []
    for object in this_stock:
        URL = object.nasdaq_url
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        # progress = list(soup)[1].find_all('div', class_="BNeawe iBp4i AP7Wnd")[0].prettify()
        progress = soup.find_all('div', class_='ln0Gqe')
        # print(progress_first)
        # progress=list(list(soup.children)[1].children)[1].find_all('div', class_='ln0Gqe')
        for number in progress:
            progress_dict.append(number.text)
    context = {
            "current_user" : this_user[0].first_name,
            "progress_dict": progress_dict,
            "this_stock": this_stock,
        }
    return render(request, "nasdaq.html", context)


def logout(request):
    request.session.flush()
    return redirect('/')

#def portfolio , create a dictionary
def profile(request):
    if 'user_id' not in request.session:
        return redirect('/')
    this_user = User.objects.filter(id = request.session['user_id'])
    portfolio = Stock.objects.filter(user=User.objects.get(id = request.session['user_id']))
    saved_articles = Article.objects.filter(article_user_id=this_user[0].id, saved = True)
    context = {
            "user": this_user[0],
            "current_user" : this_user[0].first_name,
            "username" : this_user[0].username,
            "portfolio": portfolio,
            "saved_articles": saved_articles,
        }
    return render(request, "profile.html", context)

def check_stock(request):
    if 'user_id' not in request.session:
        return redirect('/')
    else:
        errors = Stock.objects.stock_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/profile')
        stock_name = request.POST['stock-option']
        if len(Stock.objects.filter(stock_name=stock_name, user_id = request.session['user_id'])) >= 1:
            messages.error(request, "Stock is already in your portfolio.")
            return redirect('/profile')
        #if no issues, add stock to portfolio
        this_user = User.objects.get(id = request.session['user_id'])
        #when we create a stock, let's add functionality to automatically add the correct URL.
        for t in url_tuple:
            if request.POST['stock-option'] == t[0]:
                new_stock = Stock.objects.create(stock_name=request.POST['stock-option'], user=this_user, news_url = t[1], nasdaq_url = t[2]) #added
        portfolio = Stock.objects.filter(user=User.objects.get(id = request.session['user_id']))
        this_user = User.objects.filter(id = request.session['user_id'])
        saved_articles = Article.objects.filter(article_user_id=this_user[0].id, saved = True)
        context = {
            "current_user" : this_user[0].first_name,
            "portfolio": portfolio,
            "saved_articles": saved_articles,
            "username" : this_user[0].username,
        }
        return render(request, "profile.html", context)

def remove_stock(request, id):
    if 'user_id' not in request.session:
        return redirect('/')
    stock_to_remove = Stock.objects.filter(id = id)
    stock_to_remove.delete()
    return redirect('/profile')

def buy_sell(request):
    if 'user_id' not in request.session:
        return redirect('/')
    this_user = User.objects.filter(id = request.session['user_id'])
    context = {
        "current_user" : this_user[0].first_name,
        }
    return render(request, "buy_share.html", context)

def save(request, headliner):
    if 'user_id' not in request.session:
        return redirect('/')
    this_user = User.objects.filter(id = request.session['user_id'])
    this_stock_start = Article.objects.filter(headliner = headliner)
    this_stock = this_stock_start[0].stock_id
    #check if article already saved
    update_article = Article.objects.filter(headliner = headliner, article_user = this_user[0].id)
    new_article = update_article[0]
    
    if len(Article.objects.filter(headliner = headliner, article_user = this_user[0].id, saved = True)) >= 1:
        new_article.saved = False
        new_article.save()
        return redirect(f"/feed/{this_stock}")
    else: 
        new_article.saved = True
        new_article.save()
    return redirect(f"/feed/{this_stock}")

def update(request):
    if 'user_id' not in request.session:
        return redirect('/')
    this_user = User.objects.filter(id = request.session['user_id'])
    current_user = this_user[0]
    current_user.username = request.POST['username']
    current_user.save()
    messages.error(request, "Successfully updated username")
    return redirect('/profile')

def delete(request, id):
    if 'user_id' not in request.session:
        return redirect('/')
    this_user = User.objects.filter(id = request.session['user_id'])
    current_user = this_user[0]
    current_user.delete()
    return redirect('/')

def unsave_profile(request, headliner):
    if 'user_id' not in request.session:
        return redirect('/')
    this_user = User.objects.filter(id = request.session['user_id'])
    this_stock_start = Article.objects.filter(headliner = headliner)
    this_stock = this_stock_start[0].stock_id
    #check if article already saved
    update_article = Article.objects.filter(headliner = headliner, article_user = this_user[0].id)
    new_article = update_article[0]
    if len(Article.objects.filter(headliner = headliner, article_user = this_user[0].id, saved = True)) >= 1:
        new_article.saved = False
        new_article.save()
        return redirect("/profile")
    return redirect("/profile")

def load_save(request, headliner):
    headliner = headliner
    return redirect(f"/save/{headliner}")