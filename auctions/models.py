from django.contrib.auth.models import AbstractUser
from django.db import models
import time 


class User(AbstractUser):
    # Comment out the foreign key to introspect with django to 
    #   deal with pythonm not providing forward declarations
    watch_list = models.ManyToManyField("AuctionListing", blank=True, related_name="watchedBy")


class AuctionListing(models.Model):

    CATEGORY_CHOICES = [
        ('Fashion', (
                ('wc', "Women's Clothing"),
                ('mc', "Men's Clothing"),
            )
        ),
        ('Books, Movies & Music', (
                ('book', 'Books'),
                ('dvd', 'DVDs & Movies'),
                ('Music', 'Music')
            )
        ),
        ('Electronics', (
                ('phone', 'Cell Phones, Smart Watches, & Accessories'),
                ('pc', 'Computers, Tablets & Network Hardware'),
                ('tv', 'TV, Video & Home Audio Electronics'),
            )
        ),
        ('Collectibles & Art', (
                ('collec', 'Collectibles'),
                ('sport', 'Sports Memorabilia, Fan Shop & Sports Cards'),
                ('art', 'Art'),
        )
        ),
        ('Home & Garden', (
                ('furnit', 'Furniture'),
                ('decor', 'Home Decor'),
            )
        ),
        ('Sporting Goods', (
                ('vhs', 'VHS Tape'),
                ('dvd', 'DVD'),
            )
        ),
        ('Toys & Hobbies', (
                ('vhs', 'VHS Tape'),
                ('dvd', 'DVD'),
            )
        ),
        ('Business & Industrial', (
                ('vhs', 'VHS Tape'),
                ('dvd', 'DVD'),
            )
        ),
        ('Health & Beauty', (
                ('vhs', 'VHS Tape'),
                ('dvd', 'DVD'),
            )
        ),
        ('Others', 'Others')
    ]

    listing_title = models.CharField(max_length=64)
    
    description = models.TextField(max_length=400)
    category = models.CharField(
        max_length=6,
        choices=CATEGORY_CHOICES
    )
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Forbids the deletion of the highest bid
    highest_bidder = models.ForeignKey("User", null=True, on_delete=models.PROTECT)
    date_posted = models.TimeField(auto_now=True)
    image = models.ImageField(blank=True, upload_to="images")
    image_url = models.URLField(blank=True)
    # When the referenced object (User) is deleted, also delete the
    #   objects (Auction Listings) that have references to it.
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="listings")

    def __str__(self):
        return f"{self.listing_title} ({self.category})."


class Bid(models.Model):
    item = models.ForeignKey(AuctionListing, null=True, on_delete=models.CASCADE, related_name="bids")
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bid_by_whom = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="user_bids")
    bid_time = models.TimeField(auto_now=True)

    def __str__(self):
        return f"{self.bid_amount}$ bid for item '{self.item}' at {self.bid_time}"


class Comment(models.Model):
    listing = models.ForeignKey(AuctionListing, null=True, on_delete=models.CASCADE, related_name="listing_comments")
    comment = models.TextField(max_length=250, null=True)
    commented_by_whom = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="user_comments")
    date_posted = models.TimeField(auto_now=True)

    def __str__(self):
        return f"{self.commented_by_whom} commented on '{self.listing}'."