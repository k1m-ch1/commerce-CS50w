from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *

def require_login(func):
    def ret_func(*args, **kwargs):
        if args[0].user.is_authenticated:
            return func(*args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('login'))
    return ret_func
            
def index(request):
    all_listing = ActiveListing.objects.all()
    return render(request, "auctions/index.html", 
                  {"listings":all_listing})


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
    
def category(request, category):
    if category == "selection":
        selected_catagories = Category.objects.all()
        return render(request, 'auctions/category.html', {"categories":selected_catagories})
    else:
        category_object = Category.objects.get(name=category)
        selected_listings = ActiveListing.objects.filter(category=category_object)
        return render(request, 'auctions/index.html', {
            "classification":category.capitalize(),
            "listings":selected_listings})

@require_login
def listing(request, listing_id):
    message = str()
    listing_model = ActiveListing.objects.get(pk=listing_id)
    if request.method == "POST":
        bid_amount = request.POST.get("bid-amount", "")
        endbid = request.POST.get("endbid", False)
        add_to_wish_list_check_box = request.POST.get("add-to-wish-list", "off")
        if add_to_wish_list_check_box == "on":
            listing_model.watchers.add(User.objects.get(username=request.user))
        elif add_to_wish_list_check_box == "off":
            listing_model.watchers.remove(User.objects.get(username=request.user))
        if not bid_amount == "":
            bid_amount = float(bid_amount)
            if bid_amount <= listing_model.current_price:
                message = f"The price entered you entered is equal or lower than the current price. \
                    You must enter a price higher than {listing_model.current_price} if you wish to enter the bidding."
            else:
                listing_model.current_price = bid_amount
                listing_model.highest_bidder = request.user
                listing_model.save()
        if endbid:
            if listing_model.highest_bidder == None:
                message = "No one bid on this piece, cannot end the bid yet."
            else:
                listing_model.is_active = False
                listing_model.save()
    print(listing_model.watchers.filter(username=request.user))
    return render(request, 'auctions/listing.html', {
        "message":message,
        "listing":listing_model,
        "is_watching": not len(listing_model.watchers.filter(username=request.user)) == 0,
        "comments": listing_model.comments.all()
    })

@require_login
def create_listing(request):
    if request.method == "POST":
        new_listing_obj = ActiveListing.objects.create(name=request.POST["name"],
                                        owner = User.objects.get(username=request.user),
                                        description=request.POST["description"],
                                        photo=ActiveListing.objects.get(pk=1).photo,
                                        is_active = True,
                                        current_price = float(request.POST["default-price"]),
                                        category = Category.objects.get(pk=int(request.POST["category"])),
                                        )
        new_listing_obj.save()
        return HttpResponseRedirect(reverse('index'))
    return render(request, 'auctions/create_listing.html', {
        "categories":Category.objects.all()
    })

@require_login
def watchlist(request):
    user_listings = User.objects.get(username=request.user).on_watch.all()
    return render(request, 'auctions/index.html', {
        "listings":user_listings,
        "classification":f"{request.user}'s Watchlist"}) 

@require_login
def add_comment(request, listing_id):
    if request.method == "POST":
        new_comment = Comment(owner=request.user, content=request.POST["comment"], listing=ActiveListing.objects.get(pk=listing_id))
        new_comment.save()
        
    return HttpResponseRedirect(reverse('listing', args=(listing_id, )))
 
 