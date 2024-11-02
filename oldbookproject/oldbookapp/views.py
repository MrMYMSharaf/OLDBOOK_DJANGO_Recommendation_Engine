from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth import authenticate
from django.http import HttpResponse
from oldbookapp.forms import ContactForm
from .models import Books,About,CustomUser,Rating,CartItem,OrderPlaced 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.conf import settings
from .forms import CustomUserCreationForm,ProfileUpdateForm,RatingForm  
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
#Import Some Paypal Stuff
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from django.db.models import Q 
import uuid # unique user id for duplictate orders
from .recommendation import get_recommendations 

import logging
logger = logging.getLogger(__name__)



def index(request):
    books = Books.objects.all()
    total_books = books.count()  # Count total books

    search_query = request.GET.get('search', '')  # Get the search term from query parameters
    
    if search_query:
        # Filter books based on the search query
        books = Books.objects.filter(
            Q(Book_Title__icontains=search_query) |  # Search in book titles
            Q(Description__icontains=search_query)    # Search in descriptions
        )
        
        if books.exists():  # Only fetch recommendations if books are found
            # Fetch book IDs for recommendation purposes
            book_ids = books.values_list('id', flat=True)
            # Get recommendations based on the search query
            recommended_books_ids = get_recommendations(book_ids)  # Assumes get_recommendations returns book IDs
            # Fetch recommended books from the database (limit to 5 recommended books)
            recommended_books = Books.objects.filter(id__in=recommended_books_ids)[:5]
        else:
            recommended_books = []  # No recommendations if no search results
    else:
        books = Books.objects.all()  # Fetch all books if no search term is provided
        recommended_books = []  # No recommendations if there's no search
    
    

    # Set up pagination
    p = Paginator(books, 5)  # Show 5 books per page
    page_number = request.GET.get('page')  # Get page number from the query string
    page_obj = p.get_page(page_number)  # Automatically handles invalid page numbers

    # Pass the paginated object and total book count to the template
    context = {
        'page_obj': page_obj,
        'total_books': total_books,
        'search_query': search_query,  # Pass the search query to the template
        'recommended_books': recommended_books,  # Pass recommended books
    }
    
    return render(request, 'oldbook/index.html', context)

def about(request):
    about_instance = About.objects.first()
    context = {'about': about_instance}
    return render(request, 'oldbook/about.html',context)

@login_required
def addcart(request):
   cart = CartItem.objects.filter(user=request.user)
   total_price = cart.aggregate(total=Sum('book__price'))['total'] or 0.00
   context = { 'cart': cart,
              'total_price': total_price, }
 
   return render(request, 'oldbook/addcart.html',context)

def cart_delete(request,id):
    obj = get_object_or_404(CartItem, id = id,user=request.user)
    obj.delete()
    messages.success(request, 'Item removed from your cart successfully.')
    return redirect("addcart")
    

@login_required
def addcartItem(request):
    if request.method =='POST':
        book_id = request.POST.get('book_id')
        book = get_object_or_404(Books,id=book_id) #Get the book ID from the POST request
        user = request.user
        #Check if the book alredy in the user's cart
        existing_cart_item = CartItem.objects.filter(book=book,user=user).first()

        if existing_cart_item:
            return JsonResponse({'success': False, 'message': 'This book is already in your cart.'})
        else:
            CartItem.objects.create(book=book,user=request.user)
            return JsonResponse({'success': True, 'message': 'Book added to cart successfully!'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('index')
    else:
        form = ContactForm()
    
    return render(request, 'oldbook/contact.html', {'form': form})


# def success(request):
#   return HttpResponse('Success!')

@login_required
def details(request, slug):
    book = get_object_or_404(Books, slug=slug)
    existing_rating = None

    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        user = request.user
        
        # Ensure the rating value is an integer
        try:
            rating_value = int(rating_value)
            if rating_value < 0 or rating_value > 10:
                raise ValueError("Rating must be between 0 and 10.")
        except (ValueError, TypeError):
            # Handle the error (optional)
            return redirect('details', slug=slug)

        # Check if the user already rated the book
        existing_rating, created = Rating.objects.update_or_create(
            book=book,
            user=user,
            defaults={'rating': rating_value}
        )
        return JsonResponse({'success': True})

    # Retrieve the user's existing rating if it exists
    existing_rating = Rating.objects.filter(book=book, user=request.user).first()

    context = {
        'book': book,
        'existing_rating': existing_rating,
    }
    return render(request, 'oldbook/details.html', context)

@login_required
def user_profile(request):
    return render(request, 'oldbook/user_profile.html')


def login_view(request):  # Renamed the function to avoid conflict
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if a user with the provided username exists
        if not CustomUser.objects.filter(username=username).exists():
            # Display an error message if the username does not exist
            messages.error(request, 'Invalid Username')
            return redirect('login')
        
        # Authenticate the user with the provided username and password
        user = authenticate(request,username=username, password=password)
        
        if user is None:
            # Display an error message if authentication fails (invalid password)
            messages.error(request, "Invalid Password")
            return redirect('login')
        else:
            # Log in the user and redirect to the home page upon successful login
            auth_login(request, user)  # Use the renamed function
            return redirect('index')
    
    # Render the login page template (GET request)
    return render(request, 'oldbook/auth/login.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Use Django's built-in login function
            messages.success(request, 'Account created successfully!')
            return redirect('user_profile')  # Redirect to profile or home page after successful signup
    else:
        form = CustomUserCreationForm()

    return render(request, 'oldbook/auth/signup.html', {'form': form})

def logout_view(request):
    auth_logout(request)  # Log out the user
    return redirect('login')

@login_required
def edit_profile(request):
    user = request.user  # Get the currently logged-in user
    if request.method == 'POST':
        logger.debug(f"Request.FILES: {request.FILES}")  # Log the file data
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)  # Bind form with user instance
        if form.is_valid():
            password = request.POST.get('password', None)  # Get new password if provided
            if password:  # If a new password is provided
                user.set_password(password) 
            logger.debug("Form is valid, saving form.") # Set the new password
            form.save()  # Save the updated user data, including the image
            return redirect('user_profile')  # Redirect to the user's profile page
    else:
        form = ProfileUpdateForm(instance=user)  # Create a form instance with current user data

    return render(request, 'oldbook/edit_profile.html', {'form': form})  # 


def payment(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    total_price = cart_items.aggregate(total=Sum('book__price'))['total'] or 0.00
    context = {
            'paypal_client_id': settings.PAYPAL_CLIENT_ID,
            'total_price': total_price,
        }
    return render(request,'oldbook/payment.html',context)

def payment_done(request):
    user = request.user
    paypal_transaction_id = request.GET.get("paypal_payment_id")  # Use the correct name for the payment ID
    print("Received PayPal transaction ID:", paypal_transaction_id)
    cart_items = CartItem.objects.filter(user=user)

    # Check if the payment was made with PayPal
    if paypal_transaction_id:
        # Create order for each cart item
        for cart in cart_items:
            OrderPlaced.objects.create(
                user=user,
                product=cart.book,  # Make sure this references the correct field
                transaction_id=paypal_transaction_id,
            )
        # Clear the cart after placing orders
        cart_items.delete()
        
        # Provide context for the order success page
        
        return render(request, 'oldbook/order_success.html')

    else:
        return HttpResponse("Invalid payment information")
    
def order_success(request):
    return render(request,'oldbook/order_success.html')

