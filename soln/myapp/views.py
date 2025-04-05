# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages  # Import messages for error handling
from .forms import CustomRegisterForm
from django.contrib.auth.decorators import user_passes_test
from .models import Post, Comment, Like  # Import all needed models
from .forms import PostForm, CommentForm
from django.shortcuts import get_object_or_404
import random
import string
from io import BytesIO
from django.http import HttpResponse
from django.core.cache import cache
from PIL import Image, ImageDraw, ImageFont
from django.contrib import messages

def register(request):
    if request.method == "POST":
        # CAPTCHA verification
        user_captcha = request.POST.get('captcha', '').lower()
        session_captcha = request.session.get('captcha_text', '').lower()
        
        if user_captcha != session_captcha:
            messages.error(request, "Invalid CAPTCHA verification")
            return redirect('register')
        
        # Clear CAPTCHA after verification
        if 'captcha_text' in request.session:
            del request.session['captcha_text']

        # Process registration form
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            # If form is invalid, show errors
            messages.error(request, "Please correct the errors below")
    else:
        form = CustomRegisterForm()

    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == "POST":
        # CAPTCHA verification
        user_captcha = request.POST.get('captcha', '').lower()
        session_captcha = request.session.get('captcha_text', '').lower()
        
        if user_captcha != session_captcha:
            messages.error(request, "Invalid CAPTCHA verification")
            return redirect('login')
        
        # Clear CAPTCHA after verification
        if 'captcha_text' in request.session:
            del request.session['captcha_text']

        # Process login
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')

# Keep the rest of your views as they were
# ... [other view functions] ...

def generate_captcha(request):
    # Generate random 6-character text (letters + numbers)
    text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    request.session['captcha_text'] = text.lower()
    
    # Create image
    img = Image.new('RGB', (180, 60), color=(23, 25, 35))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except:
        font = ImageFont.load_default()
    
    # Draw text with random distortion
    x = 10
    for char in text:
        y = random.randint(5, 15)
        angle = random.randint(-10, 10)
        char_img = Image.new('RGBA', (30, 40))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((0, 0), char, font=font, fill=(255, 255, 255))
        char_img = char_img.rotate(angle, expand=1)
        img.paste(char_img, (x, y), char_img)
        x += 30
    
    # Add noise
    for _ in range(200):
        xy = (random.randrange(180), random.randrange(60))
        draw.point(xy, fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    
    # Save to buffer
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type='image/png')

def home(request):
    posts = Post.objects.all().order_by('-created_at')
    comment_form = CommentForm()
    return render(request, 'home.html', {
        'posts': posts,
        'comment_form': comment_form,
    })
 # Render the home.html template

def login_view(request):
    if request.method == 'POST':
        # Add captcha validation
        user_input = request.POST.get('captcha', '').lower()
        captcha_text = request.session.get('captcha_text', '').lower()
        
        if user_input != captcha_text:
            messages.error(request, "Invalid CAPTCHA")
            return redirect('login')
        
        # Clear used CAPTCHA
        if 'captcha_text' in request.session:
            del request.session['captcha_text']

# def user_login(request):
#     if request.method == "POST":
#         username = request.POST.get('username')  # Use .get() for safety
#         password = request.POST.get('password')  # Use .get() for safety
#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             login(request, user)
#             return redirect('home')  # Redirect to home page after login
#         else:
#             messages.error(request, "Invalid username or password.")  # Display error message

#     return render(request, 'login.html')
        
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to home page after logout

def is_admin(user):
    return user.is_authenticated and user.is_staff  # Check if the user is authenticated and has staff privileges

@user_passes_test(is_admin)
def admin_dashboard(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('admin_dashboard')
    else:
        form = PostForm()

    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'admin.html', {'form': form, 'posts': posts})

def add_comment(request, post_id):
    if request.method == 'POST' and request.user.is_authenticated:
        post = get_object_or_404(Post, id=post_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
    return redirect('home')

def like_post(request, post_id):
    if request.method == 'POST' and request.user.is_authenticated:
        post = get_object_or_404(Post, id=post_id)
        Like.objects.get_or_create(post=post, user=request.user)
    return redirect('home')

def delete_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        post.delete()
    return redirect('admin_dashboard')

def generate_captcha(request):
    # Generate random 6-character text (letters + numbers)
    text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    request.session['captcha_text'] = text.lower()  # Store in session
    
    # Create image
    img = Image.new('RGB', (180, 60), color=(23, 25, 35))
    draw = ImageDraw.Draw(img)
    
    try:
        # Use a font file (place in your project root)
        font = ImageFont.truetype("arial.ttf", 28)
    except:
        font = ImageFont.load_default()
    
    # Draw text with random distortion
    x = 10
    for char in text:
        y = random.randint(5, 15)
        angle = random.randint(-10, 10)
        char_img = Image.new('RGBA', (30, 40))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((0, 0), char, font=font, fill=(255, 255, 255))
        char_img = char_img.rotate(angle, expand=1)
        img.paste(char_img, (x, y), char_img)
        x += 30
    
    # Add noise
    for _ in range(200):
        xy = (random.randrange(180), random.randrange(60))
        draw.point(xy, fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    
    # Save to buffer
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type='image/png')