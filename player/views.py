from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from player.forms import CityCreationForm
from player.tokens import account_activation_token
from city_engine.models import City, CityField
from city_engine.board import HEX_NUM


def main_page(request):
    return render(request, 'registration/main_page.html')


def signup(request):
    if request.method == 'POST':
        user_creation_form = UserCreationForm(request.POST)
        city_creation_form = CityCreationForm(request.POST)
        if user_creation_form.is_valid() and city_creation_form.is_valid():
            user_creation_form.save()
            username = user_creation_form.cleaned_data.get('username')
            raw_password = user_creation_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            city_name = city_creation_form.cleaned_data.get('name')
            new_city = City.objects.create(user_id=request.user.id, name=city_name)

            for field_id in range(1, int(HEX_NUM)+1):
                CityField.objects.create(city=new_city, field_id=field_id).save()
            new_city.save()
            return redirect('/main_view/')
    else:
        user_creation_form = UserCreationForm()
        city_creation_form = CityCreationForm()
    return render(request, 'registration/signup.html', {'user_creation_form': user_creation_form,
                                                        'city_creation_form': city_creation_form})

# def signup(request):
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = False
#             user.save()
#             current_site = get_current_site(request)
#             subject = 'Aktywacja Twojego konta'
#             message = render_to_string('account_activation_email.html', {
#                 'user':user,
#                 'domain':current_site.domain,
#                 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#                 'token':account_activation_token.make_token(user)
#             })
#             user.email_user(subject, message)
#             return redirect('account_activation_sent')
#     else:
#         form = SignUpForm()
#     return render(request, 'signup.html', {'form': form})


def account_activation_sent(request):
    return render_to_string(request, 'account_activation_email.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_encode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'account_activation_email.html')
