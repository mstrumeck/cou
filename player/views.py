from random import choice, randrange

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode

from citizen_engine.models import Citizen, Family, Education
from city_engine.main_view_data.board import assign_city_fields_to_board
from city_engine.models import City, Field, StandardLevelResidentialZone
from cou.global_var import ELEMENTARY
from player.forms import CityCreationForm, MapForm
from player.tokens import account_activation_token
from resources.models import Market
from .models import Profile
from map_engine.models import Map, Field
from django import forms
import random


def main_page(request):
    return render(request, "registration/main_page.html")


def signup(request):
    if request.method == "POST":
        user_creation_form = UserCreationForm(request.POST)
        city_creation_form = CityCreationForm(request.POST)
        map_form = MapForm(request.POST)

        if user_creation_form.is_valid() and city_creation_form.is_valid() and map_form.is_valid():
            user_creation_form.save()
            username = user_creation_form.cleaned_data.get("username")
            raw_password = user_creation_form.cleaned_data.get("password1")
            chosen_map = map_form.cleaned_data.get("maps")
            city_name = city_creation_form.cleaned_data.get("name")
            import random
            start_place = random.choice(Field.objects.filter(map=chosen_map, if_start=True))
            user = authenticate(username=username, password=raw_password)
            player = Profile.objects.get(user=user)

            login(request, user)
            new_city = City.objects.create(player=player, name=city_name, map_id=chosen_map)
            assign_city_fields_to_board(start_place, chosen_map, player)

            import names
            for x in range(30):

                sex = choice(Citizen.SEX)[0]
                surname = names.get_last_name()
                f = Family.objects.create(surname=surname, city=new_city)
                c = Citizen.objects.create(
                    city=new_city,
                    age=randrange(18, 24),
                    name=names.get_first_name(sex.lower()),
                    surname=surname,
                    health=10,
                    month_of_birth=randrange(1, 12),
                    sex=sex,
                    family=f,
                    cash=500,
                    edu_title=ELEMENTARY,
                )
                Education.objects.create(citizen=c, name=ELEMENTARY, effectiveness=0.50)

            import random

            s = StandardLevelResidentialZone.objects.create(
                city=new_city,
                if_under_construction=False,
                city_field=random.choice(list(Field.objects.filter(player=player))),
            )
            s.self__init(50)
            s.save()
            new_city.save()

            # player.if_social_enabled = True
            player.save()
            Market.objects.create(profile=player)

            return redirect("/main/")
    else:
        user_creation_form = UserCreationForm()
        city_creation_form = CityCreationForm()
        map_form = MapForm(request.POST)
    return render(
        request,
        "registration/signup.html",
        {
            "user_creation_form": user_creation_form,
            "city_creation_form": city_creation_form,
            "map_form": map_form
        },
    )


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
    return render_to_string(request, "account_activation_email.html")


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_encode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect("home")
    else:
        return render(request, "account_activation_email.html")
