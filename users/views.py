from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from .tokens import TokenGenerator
# Create your views here.

def Home(request):
    return render(request, 'users/home.html')

def Register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        if pass1 == pass2:
            if User.objects.filter(username = username).exists():
                messages.info(request, 'Username already exist!')
                return render(request, 'users/register.html')
            if User.objects.filter( email = email ):
                messages.info(request, 'Email already exists!')
                return render(request, 'users/register')
            else:
                myuser = User.objects.create_user(username, email, pass1)
                myuser.is_active = False
                myuser.save()
                messages.success(request, f'{myuser.username}, your account have be successfully created')
                
                # Welcome message to users mail
                subject = 'Welcome to Login System'
                message = 'HELLO' + myuser.username + 'Welcome as a member of login system /n Kindly click the link below to activate your account'
                email_from = settings.EMAIL_HOST_USER
                to_list = [myuser.email]
                send_mail( subject, message, email_from, to_list, fail_silently = True)
                
                #Confirmation mail
                current_site = get_current_site(request)
                email_subject = 'Confirm your email at login system'
                context = {
                    'name': myuser.username,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
                    'token': TokenGenerator.make_token(myuser)
                }
                message2 = render_to_string('users/confirmation_email.html', context)
                email = EmailMessage(
                    email_subject,
                    message2,
                    settings.EMAIL_HOST_USER,
                    [myuser.email]
                )
                email.fail_silently = True
                email.save()
                return redirect('login')
                
    return render(request, 'users/register.html', )

def UserLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        user = authenticate(request, username = username, password = pass1)

        if user is not None:
            login(request, user)
            return render(request, 'users/home.html')
        else:
            messages.info(request, 'You have entered bad credentials')
            return render(request, 'users/login.html')
    return render(request, 'users/login.html')

def about(request):
    return render(request, 'users/about.html')

def UserLogout(request):
    logout(request)
    messages.info(request, 'You are logged out!')
    return render(request, 'users/home.html')

def Activate(request, uid64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid64))
        myuser = User.objects.get(pk = uid)
    except (ValueError, TypeError, OverflowError, User.DoesNotExist):
        myuser = None
    if myuser is not None and TokenGenerator.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render('users/confirmation_failed.html')