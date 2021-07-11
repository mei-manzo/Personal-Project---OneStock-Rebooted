from django.db import models
import re
import bcrypt
from django.db.models.fields import TextField

class UserManager(models.Manager):
    def basic_validator(self, postData):
        errors = {}
        email = postData['email']
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if len(postData['first-name']) <2:
            errors["first_name"]="First name should be at least 2 characters"
        if len(postData['last-name']) <2:
            errors["last_name"]="Last name should be at least 2 characters"
        if len(postData['username']) <2:
            errors["username"]="Username should be at least 2 characters"
        if not EMAIL_REGEX.match(postData['email']):             
            errors['email'] = ("Invalid email address!")
        if len(postData['password']) < 8:
            errors["password"]="Password must be at least 8 characters"
        if postData['password'] != postData['confirm-password']:
            errors["password"]="Passwords do not match"
        return errors
        
    def login_validator(self, postData):
        errors = {}
        email = postData['email']
        existing_user = User.objects.filter(email=postData['email'])
        if len(postData['email']) == 0:
            errors['email'] = "Must enter an email"
            return errors
        if len(User.objects.filter(email=email)) == 0:
            errors['email'] = "Email is not registered"
            return errors
        if len(postData['password']) < 8:
            errors['password'] = "Must enter a password 8 characters or longer"
        elif bcrypt.checkpw(postData['password'].encode(), existing_user[0].password.encode()) != True:
            errors['password'] = "Email and password do not match"
        return errors
    
class StockManager(models.Manager):
    def stock_validator(self, postData):
        errors = {}
        stocks = ["GOOGL", "BYND", "AMZN"]
        # if (postData['stock-option']) != "GOOGL" and (postData['stock-option']) != "BYND" :
        if (postData['stock-option']) not in stocks:
            errors['stock-option'] = "Must enter a valid stock option."
        return errors

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add = True)
    objects = UserManager()

class Stock(models.Model):
    stock_name = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now= True)
    user = models.ForeignKey(User, related_name = "stocks", on_delete = models.CASCADE)
    news_url = models.TextField()
    nasdaq_url = models.TextField()
    objects = StockManager()

class Article(models.Model):
    saved = models.BooleanField(default=False)
    headliner = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    hyperlink = models.TextField()
    stock = models.ForeignKey(Stock, related_name="articles", on_delete = models.CASCADE, null = True)
    article_user = models.ForeignKey(User, related_name = "user_articles", on_delete = models.CASCADE, null = True)

