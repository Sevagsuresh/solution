# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages  # Import messages for error handling
from .forms import CustomRegisterForm
from django.contrib.auth.decorators import user_passes_test
from .models import Post, Comment, Like ,Dislike,OxygenAvailability,SafeAwarePoll, SafeAwareResponse ,NormalPoll, NormalPollResponse,HealthEvent
from .forms import PostForm, CommentForm
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
import random
import string
from io import BytesIO
from django.http import HttpResponse
from django.core.cache import cache
from PIL import Image, ImageDraw, ImageFont
from django.db.models import Count
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

def admin_user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'user_list.html', {'users': users})

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

@user_passes_test(is_admin)
def manage_post(request):
    posts = Post.objects.all().order_by('-created_at')
    comment_form = CommentForm()
    return render(request, 'manage_post.html', {
        'posts': posts,
        'comment_form': comment_form,
    })
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('manage_post')
    else:
        form = PostForm()

    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'create_post.html', {'form': form, 'posts': posts})

@user_passes_test(lambda u: u.is_staff)
def reply_to_comment(request, comment_id):
    if request.method == "POST":
        comment = get_object_or_404(Comment, id=comment_id)
        reply_text = request.POST.get('reply')
        if reply_text:
            comment.reply = reply_text
            comment.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


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

def dislike_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if request.method == "POST":
        # Remove like if already liked
        Like.objects.filter(post=post, user=user).delete()

        dislike, created = Dislike.objects.get_or_create(post=post, user=user)
        if not created:
            dislike.delete()  # Toggle
    return redirect(request.META.get('HTTP_REFERER', '/'))

def delete_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        post.delete()
    return redirect('admin_dashboard')

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Overall counts
    total_likes = Like.objects.filter(post=post).count()
    total_dislikes = Dislike.objects.filter(post=post).count()
    total_comments = Comment.objects.filter(post=post).count()

    # Last 7 days analytics
    last_week = timezone.now() - timedelta(days=7)
    recent_likes = Like.objects.filter(post=post, created_at__gte=last_week).count()
    recent_dislikes = Dislike.objects.filter(post=post, created_at__gte=last_week).count()
    recent_comments = Comment.objects.filter(post=post, created_at__gte=last_week).count()

    # Additional dynamic example values (these could be calculated better in real apps)
    engagement_rate = (total_likes + total_dislikes + total_comments) / 3 if post else 0
    avg_response_time = "1.8h"  # Example static value or calculate from timestamps if needed

    context = {
        'post': post,
        'total_likes': total_likes,
        'total_dislikes': total_dislikes,
        'total_comments': total_comments,
        'recent_likes': recent_likes,
        'recent_dislikes': recent_dislikes,
        'recent_comments': recent_comments,
        'engagement_rate': f"{engagement_rate:.1f}%",
        'avg_response_time': avg_response_time,
    }

    return render(request, 'post_detail.html', context)
def view_oxygen(request):
    data = OxygenAvailability.objects.all().order_by('id')
    return render(request, 'view_oxygen.html', {'data': data})

@user_passes_test(lambda u: u.is_staff)
def manage_oxygen(request):
    data = OxygenAvailability.objects.all().order_by('id')

    if request.method == 'POST':
        for item in data:
            item.availability_percent = request.POST.get(f'avail_{item.id}', item.availability_percent)
            item.capacity_mt = request.POST.get(f'cap_{item.id}', item.capacity_mt)
            item.demand_mt_per_day = request.POST.get(f'demand_{item.id}', item.demand_mt_per_day)
            item.save()
        return redirect('manage_oxygen')

    return render(request, 'manage_oxygen.html', {'data': data})

def poll_list(request):
    polls = NormalPoll.objects.all().order_by('-created_at')
    return render(request, 'polls/list.html', {'polls': polls})

def vote_poll(request, poll_id):
    poll = get_object_or_404(NormalPoll, id=poll_id)

    # Prevent multiple votes from same user
    if NormalPollResponse.objects.filter(poll=poll, user=request.user).exists():
        messages.info(request, "You already voted on this poll.")
        return redirect('normal_poll_results', poll_id=poll.id)

    if request.method == 'POST':
        user_response = request.POST.get('response')
        if user_response not in ['agree', 'disagree']:
            messages.error(request, "Invalid response.")
            return redirect('vote_poll', poll_id=poll.id)

        NormalPollResponse.objects.create(
            poll=poll,
            user=request.user,
            response=user_response
        )
        messages.success(request, "Your response has been recorded.")
        return redirect('normal_poll_results', poll_id=poll.id)

    return render(request, 'polls/vote.html', {'poll': poll})

def create_poll(request):
    if request.method == 'POST':
        SafeAwarePoll.objects.create(
            title=request.POST['title'],
            question=request.POST['question']
        )
        return redirect('create_poll')
    polls = SafeAwarePoll.objects.all().order_by('-created_at')
    return render(request, 'polls/create_poll.html', {'polls': polls})

def delete_poll(request, poll_id):
    SafeAwarePoll.objects.get(id=poll_id).delete()
    return redirect('create_poll')

def edit_poll(request, poll_id):
    poll = SafeAwarePoll.objects.get(id=poll_id)
    if request.method == 'POST':
        poll.title = request.POST['title']
        poll.question = request.POST['question']
        poll.save()
        return redirect('create_poll')
    return render(request, 'admin/edit_poll.html', {'poll': poll})

def poll_detail(request, poll_id):
    poll = SafeAwarePoll.objects.get(id=poll_id)
    if request.method == 'POST':
        district = request.POST['district']
        place = request.POST['place']
        is_safe = request.POST['is_safe'] == 'yes'
        SafeAwareResponse.objects.create(poll=poll, district=district, place=place, is_safe=is_safe)
        return redirect('poll_thankyou')

    return render(request, 'poll_detail.html', {'poll': poll})

def pandemic_poll_list(request):
    polls = SafeAwarePoll.objects.all().order_by('-created_at')
    return render(request, 'polls/pandemic_poll_list.html', {'polls': polls})


# Let user vote on a specific poll
def pandemic_poll_vote(request, poll_id):
    poll = get_object_or_404(SafeAwarePoll, id=poll_id)

    if request.method == 'POST':
        is_safe = request.POST.get('is_safe')  # 'yes' or 'no'
        district = request.POST.get('district')
        place = request.POST.get('place')

        if is_safe not in ['yes', 'no']:
            messages.error(request, "Please select a valid response.")
            return redirect('pandemic_poll_vote', poll_id=poll.id)

        SafeAwareResponse.objects.create(
            poll=poll,
            is_safe=is_safe == 'yes',
            district=district,
            place=place
        )
        return redirect('pandemic_poll_thankyou')

    return render(request, 'polls/pandemic_poll_vote.html', {'poll': poll})


# Thank-you page
def pandemic_poll_thankyou(request):
    return render(request, 'polls/pandemic_poll_thankyou.html')

def user_normal_poll_list(request):
    polls = NormalPoll.objects.all()
    return render(request, 'polls/list.html', {'polls': polls})


def normal_poll_vote(request, poll_id):
    poll = get_object_or_404(NormalPoll, id=poll_id)
    has_responded = NormalPollResponse.objects.filter(user=request.user, poll=poll).exists()

    if request.method == 'POST' and not has_responded:
        answer = request.POST.get('response')
        if answer in ['agree', 'disagree']:
            NormalPollResponse.objects.create(user=request.user, poll=poll, response=answer)
            messages.success(request, 'Thank you for your response.')
            return redirect('normal_poll_results', poll_id=poll_id)

    return render(request, 'polls/vote.html', {
        'poll': poll,
        'has_responded': has_responded
    })

def normal_poll_results(request, poll_id):
    poll = get_object_or_404(NormalPoll, id=poll_id)
    agree_count = poll.responses.filter(response='agree').count()
    disagree_count = poll.responses.filter(response='disagree').count()
    total = agree_count + disagree_count
    return render(request, 'polls/results.html', {
        'poll': poll,
        'agree': agree_count,
        'disagree': disagree_count,
        'total': total
    })




def normal_poll_list(request):
    polls = NormalPoll.objects.all().order_by('-created_at')
    return render(request, 'polls/normal_poll_list.html', {'polls': polls})



def create_normal_poll(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        if question:
            NormalPoll.objects.create(question=question)
            messages.success(request, 'Poll created successfully.')
            return redirect('normal_poll_list')
    return render(request, 'polls/create_normal_poll.html')



def edit_normal_poll(request, poll_id):
    poll = get_object_or_404(NormalPoll, id=poll_id)
    if request.method == 'POST':
        poll.question = request.POST.get('question')
        poll.save()
        messages.success(request, 'Poll updated successfully.')
        return redirect('normal_poll_list')
    return render(request, 'polls/edit_normal_poll.html', {'poll': poll})



def delete_normal_poll(request, poll_id):
    poll = get_object_or_404(NormalPoll, id=poll_id)
    poll.delete()
    messages.success(request, 'Poll deleted successfully.')
    return redirect('normal_poll_list')



def normal_poll_detail(request, poll_id):
    poll = get_object_or_404(NormalPoll, id=poll_id)
    responses = NormalPollResponse.objects.filter(poll=poll)
    total_votes = responses.count()
    agree_count = responses.filter(response='agree').count()
    disagree_count = responses.filter(response='disagree').count()

    agree_percent = (agree_count / total_votes * 100) if total_votes > 0 else 0
    disagree_percent = (disagree_count / total_votes * 100) if total_votes > 0 else 0

    context = {
        'poll': poll,
        'total_votes': total_votes,
        'agree_count': agree_count,
        'disagree_count': disagree_count,
        'agree_percent': round(agree_percent, 2),
        'disagree_percent': round(disagree_percent, 2),
    }
    return render(request, 'polls/normal_poll_detail.html', context)

# ----------------------
# USER VOTE VIEW
# ----------------------

def vote_normal_poll(request, poll_id):
    poll = get_object_or_404(NormalPoll, id=poll_id)

    user_ip = get_client_ip(request)
    has_voted = NormalPollResponse.objects.filter(poll=poll, user_ip=user_ip).exists()

    if request.method == 'POST' and not has_voted:
        answer = request.POST.get('response')
        if answer in ['agree', 'disagree']:
            NormalPollResponse.objects.create(
                poll=poll,
                user_ip=user_ip,
                response=answer
            )
            messages.success(request, 'Your response has been recorded.')
            return redirect('vote_normal_poll', poll_id=poll.id)

    responses = NormalPollResponse.objects.filter(poll=poll)
    agree_count = responses.filter(response='agree').count()
    disagree_count = responses.filter(response='disagree').count()
    total_votes = responses.count()

    agree_percent = (agree_count / total_votes * 100) if total_votes > 0 else 0
    disagree_percent = (disagree_count / total_votes * 100) if total_votes > 0 else 0

    context = {
        'poll': poll,
        'has_voted': has_voted,
        'agree_count': agree_count,
        'disagree_count': disagree_count,
        'agree_percent': round(agree_percent, 2),
        'disagree_percent': round(disagree_percent, 2),
    }
    return render(request, 'polls/vote_normal_poll.html', context)


def event_list(request):
    events = HealthEvent.objects.order_by('-start_time')
    return render(request, 'events/event_list.html', {'events': events})


def event_like(request, event_id):
    event = get_object_or_404(HealthEvent, id=event_id)
    EventFeedback.objects.update_or_create(user=request.user, event=event, defaults={'response': 'like'})
    return redirect('event_list')


def event_dislike(request, event_id):
    event = get_object_or_404(HealthEvent, id=event_id)
    EventFeedback.objects.update_or_create(user=request.user, event=event, defaults={'response': 'dislike'})
    return redirect('event_list')


def create_event(request):
    if request.method == 'POST':
        # Handle form input manually or use a form
        HealthEvent.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            start_time=request.POST['start_time'],
            end_time=request.POST['end_time'],
            place=request.POST['place'],
            panchayath=request.POST['panchayath'],
            district=request.POST['district'],
        )
        return redirect('event_list')
    return render(request, 'events/create_event.html')


def edit_event(request, event_id):
    event = get_object_or_404(HealthEvent, id=event_id)

    if request.method == 'POST':
        event.title = request.POST['title']
        event.description = request.POST['description']
        event.start_time = request.POST['start_time']
        event.end_time = request.POST['end_time']
        event.place = request.POST['place']
        event.panchayath = request.POST['panchayath']
        event.district = request.POST['district']
        event.save()
        return redirect('event_list')

    return render(request, 'events/edit_event.html', {'event': event})



def delete_event(request, event_id):
    event = get_object_or_404(HealthEvent, id=event_id)

    if request.method == 'POST':
        event.delete()
        return redirect('event_list')

    return render(request, 'events/delete_event.html', {'event': event})




# ----------------------
# Helper function
# ----------------------

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def poll_report(request):
    data = SafeAwareResponse.objects.values('district', 'place', 'is_safe').annotate(count=Count('id'))
    unsafe_places = [entry for entry in data if not entry['is_safe'] and entry['count'] > 0]
    return render(request, 'admin/poll_report.html', {'unsafe_places': unsafe_places})

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