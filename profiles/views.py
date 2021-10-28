from django.shortcuts import render,  redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import Http404
from django.template.loader import render_to_string
from .forms import UserSignupForm, LoginForm, ProfileForm, UserForm, ChangeUserPasswordForm, ResetPasswordForm, CheckCodeForm, ChangePasswordResetForm
from .models import Profile, ResetPassword
import datetime


class ChangeUserPasswordView(PasswordChangeView):
    form_class = ChangeUserPasswordForm


def get_user_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@ login_required
def settings_view(request):
    if request.user.id is None:
        return redirect('posts')
    return render(request, 'layout/settings.html')
    
def login_view(request):
    if request.user.id is not None:
        return redirect('posts')

    form = LoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            email_or_username = form.cleaned_data.get('email_or_username')
            user = User.objects.filter(Q(username=email_or_username)
                                       | Q(email=email_or_username)).first()
            password = form.cleaned_data['password']
            
            if user != None and user.check_password(password):
                user = authenticate(username=user.username, password=password)
                login(request, user)
                user.profile.ip = get_user_ip(request)
                user.profile.save()
                if request.GET.get('next'):
                    return redirect(request.GET.get('next'))
                return redirect('posts')
            else:
                form = LoginForm()
    return render(request, 'profiles/login.html', {'form': form})

def signup(request):
    if request.user.id is not None:
        return redirect('posts')

    form = UserSignupForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            user = Profile.objects.get(user__username=username)
            user.ip = get_user_ip(request)
            user.first_ip = get_user_ip(request)
            user.save()
            login(request, user.user)
            messages.success(
                request, f'   لقد تم انشاء حسابك بنجاح, {username}  مرحباٌ')
            return redirect('update_info_profile')
    return render(request, 'profiles/signup.html', {'form': form})

def reset_password(request):
    if request.user.id is not None:
        return redirect('posts')
    form = ResetPasswordForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            email_or_username = form.cleaned_data.get('email_or_username')
            user = User.objects.get(Q(username=email_or_username)
                                    | Q(email=email_or_username))

            if user == None or not(user.is_active):
                messages.warning(request, 'هذا المستخدم غير موجود !!!')
                form = ResetPasswordForm()
            else:
                obj = ResetPassword.objects.get_or_create(
                    email=user.email, username=user.username)
                obj[0].new_code
                obj[0].save()
                template = render_to_string(
                    'email/code_confirm.html', {
                        'code': obj[0].code,
                        'url': request.build_absolute_uri(f'/profile/confirm_code_reset/{obj[0].id}/')
                    })
                email = EmailMessage('Code Confirm', template,
                                     'jackbill687@gmail.com', [user.email, ])
                email.content_subtype = 'html'
                email.fail_silently=False
                email.send()
                return redirect('sended_reset_code')
    return render(request, 'profiles/reset_password.html', {'form': form})

def confirm_code_reset(request, id=None):
    if request.user.id is not None:
        return redirect('posts')
    obj = get_object_or_404(ResetPassword, id=id)
    now = datetime.datetime.now()
    if abs(now.hour - obj.created.hour) > 1 and (abs(now.day - obj.created.day) >= 0 or (now.month - obj.created.month) >= 0 or (now.year - obj.created.year) >= 0):
        obj.delete()
        raise Http404('')
    if request.user.id != None:
        raise Http404('')
    form = CheckCodeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            code = form.cleaned_data.get('code')
            if int(obj.code) == code:
                obj.checked = True
                obj.save()
                code = '{:_x}'.format(code)
                return redirect('change_password_reset', code=code)
            else:
                messages.warning(request, 'رقم التأكيد خاطأ')
                form = CheckCodeForm()
    return render(request, 'profiles/confirm_code_reset.html', {'form': form})

def change_password_reset(request, code=None):
    if request.user.id is not None:
        return redirect('posts')
    code = int(code, 16)
    obj = get_object_or_404(ResetPassword, code=code)
    user = User.objects.get(Q(username=obj.username)
                            & Q(email=obj.email))
    now = datetime.datetime.now()
    if (now.hour - obj.created.hour) > 1 and ((now.day - obj.created.day) >= 0 or (now.month - obj.created.month) >= 0 or (now.year - obj.created.year) >= 0):
        obj.delete()
        raise Http404('')
    if not(obj.checked) or request.user.id != None:
        raise Http404('')
    form = ChangePasswordResetForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            if obj.checked:
                password = form.cleaned_data.get('password2')
                user.set_password(password)
                obj.delete()
                user.save()
                return redirect('login')

    return render(request, 'profiles/change_password_reset.html', {'form': form})

@ login_required
def update_info_user(request):
    if request.user.id is None:
        return redirect('login')
    form = UserForm(request.POST or None, instance=request.user)
    if request.method == "POST":
        if form.is_valid():
            messages.success(request, 'تم تعديل حسابك بنجاح')
            form.save()
            return redirect('profile', id=request.user.profile.id)
    return render(request, 'profiles/update_user.html', {'form': form})

@ login_required
def update_info_profile(request):
    if request.user.id is None:
        return redirect('login')
    form = ProfileForm(instance=request.user.profile)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES,
                           instance=request.user.profile)
        if form.is_valid():
            messages.success(request, 'تم تعديل حسابك بنجاح')
            form.save()
            form = ProfileForm(request.FILES)
            return redirect('profile', id=request.user.profile.id)
    return render(request, 'profiles/update_profile.html', {'form': form})

def profile_view(request, id=None):
    if id is None:
        user = request.user
    else:
        user = get_object_or_404(User, profile__id=id)
    profile = user.profile
    posts = user.creater.filter(
        Q(status='PUB') & Q(active=True)).order_by('-created')
    return render(request, 'profiles/profile.html', {'user': user,
                                                     'profile': profile,
                                                     'posts': posts,
                                                     })

@ login_required
def saved_posts(request):
    if request.user.id is None:
        return redirect('posts')
    user = request.user
    return render(request, 'profiles/saved.html', {'posts': user.saved.all().order_by('-created')})

@ login_required
def draft_profile_posts(request, id=None):
    if id is None:
        user = request.user
    else:
        user = get_object_or_404(
            User, Q(profile__id=id) & Q(username=request.user.username))
    posts = user.creater.filter(
        Q(status='DRA') & Q(active=True)).order_by('-created')
    return render(request, 'articles/posts.html', {
        'posts': posts,
        'status': 'DRA',
    })


