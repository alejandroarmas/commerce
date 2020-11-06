from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core import files
from django.forms import ModelForm
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from io import BytesIO
import requests
import wget

from .models import AuctionListing, Bid, Comment, User 


class CreateListing(ModelForm):

    class Meta:
        model = AuctionListing
        exclude = ('listed_by', )
    # listed_by is filled out in view


class CreateBid(ModelForm):

    class Meta:
        model = Bid
        fields = ['bid_amount']
    # bid_by_whom is filled out in view


class CreateComment(ModelForm):

    class Meta:
        model = Comment
        exclude = ['listing', 
        'commented_by_whom']
    # commented_by_whom is filled out in view


def index(request):

    listings = AuctionListing.objects.all()

    context = {
        "listings": listings
    }

    return render(request, "auctions/index.html", context)

@login_required
def watchlist(request):

    # Call the User model manager called '.objects' to obtain a QuerySet
    # This is equivalent to using SELECT on SQL.
    # Then use the limiting clause get
    user = User.objects.get(username=request.user)
    listings = user.watch_list.all()

    context = {
        "listings": listings
    }

    return render(request, "auctions/index.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url="login")
def createListing(request):
    if request.method == "POST":
        filled_form = CreateListing(request.POST, request.FILES)
        if filled_form.is_valid():
            user = User.objects.get(username=request.user)
            
            new_listing = filled_form.save(commit=False)
            new_listing.listed_by = user

            if not new_listing.image and new_listing.image_url: 
                url = new_listing.image_url
                get_photo_response = requests.get(url)
                url_is_valid = get_photo_response.status_code == requests.codes.ok
                
                if url_is_valid:
                    fp = BytesIO()
                    fp.write(get_photo_response.content)
                    file_name = url.split("/")[-1]  
                    new_listing.image.save(file_name, files.File(fp))
                    new_listing.save()
                    context = {}
                    return HttpResponseRedirect(reverse("index"))
                else:
                    context = {
                        "createlistingform": filled_form,
                        "message": "Url Invalid, please check it again."
                    }    
        else:
            context = {
        "createlistingform": filled_form,
        "message": "Form Invalid, please check it again."
    }    
    else:
        context = {
            "createlistingform": CreateListing(),
            "message": "Create your own listing!"
        }

    return render(request, "auctions/createlisting.html", context)


def listingPage(request, listing_id):
    
    listing = AuctionListing.objects.get(pk=listing_id)
    comment_section = Comment.objects.filter(listing=listing)
    
    comment_form = CreateComment()
    create_bid = CreateBid()

    context = {
        "listing": listing,
        "create_bid": create_bid,
        "comments": comment_section,
        "comment_form": comment_form
    }

    if request.method == "POST":
        filled_comment_form = CreateComment(request.POST)
        filled_bid_form = CreateBid(request.POST)
        user = User.objects.get(username=request.user)

        if filled_comment_form.is_valid():
            new_comment = filled_comment_form.save(commit=False)
            new_comment.commented_by_whom = user
            new_comment.listing = listing
            new_comment.save()

        if filled_bid_form.is_valid():
            new_bid = filled_bid_form.save(commit=False)
            can_update_bid = user is not listing.listed_by and new_bid.bid_amount > listing.current_bid

            if can_update_bid:
                # Create bid 
                
                new_bid.bid_by_whom = user
                new_bid.item = listing
                new_bid.save()
                # Update listing information
                listing.current_bid = new_bid.bid_amount
                listing.highest_bidder = user 
                listing.save()
            else:
                context["create_bid"] = filled_bid_form
        else:
                        context["create_bid"] = filled_bid_form

    return render(request, "auctions/listing.html", context)













