from django.shortcuts import render, get_object_or_404
from django.core.files.storage import FileSystemStorage
import cv2
import numpy as np
from .models import Product
from .forms import ImageUploadForm
from PIL import Image
import io

def some_similarity_check(img1, img2):
    img1_resized = cv2.resize(img1, (128, 128))
    img2_resized = cv2.resize(img2, (128, 128))

    hist1 = cv2.calcHist([img1_resized], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist2 = cv2.calcHist([img2_resized], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])

    cv2.normalize(hist1, hist1)
    cv2.normalize(hist2, hist2)

    similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

    return similarity

def find_similar_products(reference_image):
    products = Product.objects.all()
    similar_products = []

    for product in products:
        product_image = cv2.imread(product.image.path)  # Adjust path as necessary
        if product_image is not None:
            score = some_similarity_check(reference_image, product_image)
            similar_products.append((product, score))

    # Sort by similarity score in descending order
    similar_products.sort(key=lambda x: x[1], reverse=True)

    return similar_products

def image_search(request):
    if request.method == 'POST':
        uploaded_image = request.FILES['image']
        
        # Convert InMemoryUploadedFile to a format OpenCV can read
        img = Image.open(uploaded_image)
        img_array = np.array(img)
        
        # Convert RGB to BGR (OpenCV uses BGR)
        reference_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        similar_products = find_similar_products(reference_image)

        if similar_products:
            return render(request, 'search/results.html', {'similar_products': similar_products})
        else:
            return render(request, 'search/no_results.html')
    
    return render(request, 'search/upload.html')

def product_list(request):
    products = Product.objects.all()
    return render(request, 'search/product_list.html', {'products': products})

def home(request):
    return render(request, 'search/home.html')
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProductForm
from .models import Category
from django.contrib.auth.decorators import login_required
@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('add_product')  # Redirect to the same page or elsewhere
    else:
        form = ProductForm()

    categories = Category.objects.all()
    return render(request, 'product/add_product.html', {'form': form, 'categories': categories})
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product/product_detail.html', {'product': product})


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegistrationForm, LoginForm

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('product_list')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')



