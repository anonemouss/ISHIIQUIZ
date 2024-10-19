from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from .forms import UserRegisterForm, LoginForm
from .models import Post, Report
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from .models import UserProfile
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

# Check if user is superuser
def is_superuser(user):
    return user.is_superuser

@login_required
def report_post(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        message = request.POST.get('message')

        post = get_object_or_404(Post, id=post_id)
        report = Report(user=request.user, post=post, message=message)
        report.save()

        messages.success(request, 'Your report has been submitted.')
        return redirect('all_posts')

    return redirect('all_posts')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Create a UserProfile for the new user
            UserProfile.objects.create(user=user, contact_number=form.cleaned_data['contact_number'])
            messages.success(request, 'Account created! Awaiting admin approval.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def home(request):
    return render(request, 'home.html')

@login_required
def create_post(request):
    if Post.objects.filter(user=request.user).exists():
        messages.warning(request, 'You have already posted once and cannot post again.')
        return redirect('home')

    if request.method == 'POST':
        content = request.POST.get('content')
        Post.objects.create(user=request.user, content=content)
        messages.success(request, 'Your post has been created!')
        return redirect('all_posts')

    return render(request, 'create_post.html')

def view_all_posts(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 5)  # 5 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'all_posts.html', {'page_obj': page_obj})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    # Allow login if the user is a superuser
                    if user.is_superuser:
                        login(request, user)
                        messages.success(request, 'Welcome back, Superuser!')
                        return redirect('home')

                    # Check for UserProfile for non-superusers
                    try:
                        user_profile = user.userprofile
                        if user_profile.approved:
                            login(request, user)
                            messages.success(request, 'Welcome back!')
                            return redirect('home')
                        else:
                            messages.error(request, 'Your account is not approved yet.')
                    except UserProfile.DoesNotExist:
                        messages.error(request, 'User profile does not exist.')

                else:
                    messages.error(request, 'Your account is not active.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

@login_required
def view_pending_users(request):
    pending_users = User.objects.filter(is_superuser=False, is_active=True)  # Filter pending users

    paginator = Paginator(pending_users, 5)  # 5 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pending_users.html', {'page_obj': page_obj})


@user_passes_test(is_superuser)
def approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Ensure the user has a UserProfile
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        messages.error(request, f'User {user.username} does not have a profile.')
        return redirect('pending_users')

    user_profile.approved = True  # Assuming the UserProfile has an 'approved' field
    user_profile.save()
    messages.success(request, f'User {user.username} has been approved.')

    return redirect('pending_users')

@user_passes_test(is_superuser)
def view_reports(request):
    reports = Report.objects.all()
    paginator = Paginator(reports, 5)  # 5 reports per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'report_management.html', {'page_obj': page_obj})
