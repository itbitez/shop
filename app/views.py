from django.shortcuts import render, get_object_or_404, redirect
from .models import Order, OrderItem, Product, Category, Brand, Color
from .forms import UserProfileForm
from .models import UserProfile
from django.core.paginator import Paginator
from django.db.models import F
from django.db.models import Count
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from cart.cart import Cart

def cart_view(request):
    return render(request, 'cart.html')

def quickview(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return JsonResponse({
        'name': product.name,
        'price': str(product.price),
        'description': product.description,
        'sku': product.sku,
        'rating': product.rating if hasattr(product, 'rating') else 0,  # Assuming a rating field
        'reviews_count': product.reviews.count(),
        'categories': [{'name': category.name} for category in product.categories.all()],
        'tags': [{'name': tag.name} for tag in product.tags.all()],
        'image': product.image.url,  # Only the featured image
    })

def index(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    latest_products = []
    
    for category in categories:
        product = Product.objects.filter(categories=category).order_by('-created_at').first()  # Get the latest product for each category
        if product:
            latest_products.append(product)
    
    return render(request, 'index.html', {'latest_products': latest_products, 'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'product_detail.html', {'product': product})

def shop(request):
    categories = Category.objects.annotate(product_count=Count('products'))
    brands = Brand.objects.all()
    colors = Color.objects.all()

    # Get the selected filters from the URL
    category_id = request.GET.get('category')
    selected_brand = request.GET.get('brand')
    selected_color = request.GET.get('color')
    sort = request.GET.get('sort')

    # Start with all products
    products = Product.objects.all()

    # Apply category filter
    if category_id and category_id != 'None':
        try:
            category_id = int(category_id)
            products = products.filter(categories__id=category_id)
        except ValueError:
            category_id = None

    # Apply brand filter
    if selected_brand and selected_brand != 'None':
        products = products.filter(brands__name=selected_brand)

    # Apply color filter
    if selected_color and selected_color != 'None':
        try:
            selected_color = int(selected_color)
            products = products.filter(colors__id=selected_color)
        except ValueError:
            selected_color = None

    # Apply sorting
    if sort == 'name_asc':
        products = products.order_by('name')
    elif sort == 'name_desc':
        products = products.order_by('-name')
    elif sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'oldest':
        products = products.order_by('created_at')

    # Paginate the products, showing 3 products per page
    paginator = Paginator(products, 3)  # Show 3 products per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    total_products = products.count()  # Count the filtered products

    # Render the shop template with all context
    return render(request, 'shop.html', {
        'page_obj': page_obj,
        'categories': categories,
        'brands': brands,
        'colors': colors,
        'selected_brand': selected_brand,
        'selected_color': selected_color,
        'category_id': category_id,
        'sort': sort,
        'total_products': total_products
    })



def auth(request):
    # Redirect logged-in users
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('index')  # Redirect to home or another appropriate page

    if request.method == 'POST':
        if 'login' in request.POST:  # Login form submitted
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Successfully logged in!")
                return redirect('index')  # Redirect to home page
            else:
                messages.error(request, "Invalid username or password.")
        
        elif 'register' in request.POST:  # Signup form submitted
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return redirect('login')

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                user.save()
                messages.success(request, "Account created successfully! You can now log in.")
                return redirect('login')

    return render(request, 'login.html')

def my_account(request):
    if not request.user.is_authenticated:
        return redirect('login') 
    
    orders = Order.objects.filter(user=request.user).order_by('-date')
    return render(request, 'account.html', {'orders': orders})

def custom_logout(request):
    logout(request)
    return redirect('index')


# Cart Views
@login_required(login_url="/login/")
def cart_add(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    
    # Get the previous URL from request headers
    referer = request.META.get('HTTP_REFERER')
    
    # If referer exists, redirect to it, otherwise stay on the same page
    if referer:
        return redirect(referer)
    return redirect("cart_detail")



@login_required(login_url="/login/")
def item_clear(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.remove(product)
    return redirect("cart_detail")


@login_required(login_url="/login/")
def item_increment(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("cart_detail")


@login_required(login_url="/login/")
def item_decrement(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.decrement(product=product)
    return redirect("cart_detail")


@login_required(login_url="/login/")
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")


@login_required(login_url="/login/")
def cart_detail(request):
    return render(request, 'cart/cart.html')


def checkout_page(request):
    return render(request, 'cart/checkout.html')

@login_required(login_url="/login/")
def place_order(request):
    if request.method == 'POST':
        # Get user and cart information
        user = request.user
        cart = request.session.get('cart', {})

        # Check if the cart is not empty
        if not cart:
            messages.error(request, "Your cart is empty. Please add items to your cart before placing an order.")
            return redirect('checkout')

        # Get billing and shipping information from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        country = request.POST.get('country')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postcode = request.POST.get('zip')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        additional_info = request.POST.get('additional')

        # Ensure none of the required fields are empty
        if not all([first_name, last_name, country, address, city, state, postcode, phone, email]):
            messages.error(request, "Please fill out all required fields.")
            return redirect('checkout')

        # Calculate total amount
        total_amount = 0
        for key, value in cart.items():
            total_amount += float(value['price']) * int(value['quantity'])

        # Create Order object
        order = Order(
            user=user,
            firstname=first_name,
            lastname=last_name,
            country=country,
            address=address,
            state=state,
            postcode=postcode,
            phone=phone,
            email=email,
            additional_info=additional_info,
            amount=str(total_amount),
        )
        order.save()

        # Create OrderItem objects
        for key, value in cart.items():
            product_name = value['name']
            product_quantity = value['quantity']
            product_price = value['price']
            product_image = value['image']

            order_item = OrderItem(
                order=order,
                product=product_name,
                quantity=product_quantity,
                price=product_price,
                total=float(product_price) * int(product_quantity),
                image=product_image
            )
            order_item.save()

        # Clear the cart
        request.session['cart'] = {}

        # Display success message
        messages.success(request, "Your order has been placed successfully!")

        # Redirect to the Thank You page
        return redirect('thank-you')

    # If not POST request, redirect to checkout page
    return redirect('checkout')

# Thank you page view
def thanks(request):
    return render(request, 'cart/thanks.html')


def account_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=user_profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('account')  # Redirect back to the account page
    else:
        profile_form = UserProfileForm(instance=user_profile)

    context = {
        'profile_form': profile_form,
    }
    return render(request, 'account.html', context)