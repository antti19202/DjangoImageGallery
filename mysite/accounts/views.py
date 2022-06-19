# accounts/views.py
from django.contrib.auth.forms import UserCreationForm
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from taggit.models import Tag
from django.template.defaultfilters import slugify

from .forms import CreateUserForm, CustomerForm, UploadImage, CreateAlbum
from .models import *



# Rekisteröinti sivu
def registerPage(request):
    # Jos käyttäjä on jo kirjaantunut, hänet ohjataan kotisivulle
    if request.user.is_authenticated:
        return redirect('home')
    
    # Jos käyttäjä ei ole kirjautunut
    else:
        form = CreateUserForm()
        if request.method == 'POST':  # Tarkastetaan että tiedot tulee POST:illa
            form = CreateUserForm(request.POST)
            if form.is_valid():  # Tarkastetaa tiedot
                user = form.save()  # Tiedot tallennetaan
                username = form.cleaned_data.get('username')

                # Luopdaan käyttäjälle profiili
                Customer.objects.create(user=user)
                # kun käyttäjä on luotu, hänet siirretään login sivulle ja näytetään alla oleva teksti
                messages.success(request, 'Account was created for ' + username)

                return redirect('login')  # Käyttäjän ohjaus login sivulle

        context = {'form':form}
        return render(request, 'accounts/register.html', context)


# Sisäänkirjautumis sivu
def loginPage(request):
    # Jos käyttäjä on jo kirjaantunut, hänet ohjataan kotisivulle
    if request.user.is_authenticated:
        return redirect('home')
    
    # Jos käyttäjä ei ole kirjautunut
    else:
        if request.method == 'POST':  # Tarkastetaan että tiedot tulee POST:illa
            username = request.POST.get('username')  # Otetaan käyttäjänimi muuttujaan
            password = request.POST.get('password')  # Otetaan salasana muuttujaan

            # Tarkastetaan että käyttäjätunnus ja salasana täsmäävät
            user = authenticate(request, username=username, password=password)

            # Jos tunnukset täsmäävät, käyttäjä kirjautuu sisään ja ohjataan kotisivulle
            if user is not None:
                login(request, user)
                return redirect('home')
            # Jos tunnukset eivät täsmää, annetaan siitä viesti
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'accounts/login.html', context)

# Kun käyttäjä kirjautuu ulos, hänet ohjataan login sivulle
def logoutUser(request):
    logout(request)
    return redirect('login')


# Jos käyttäjä ei ole kirjautunut sisään, hänet ohjataan login sivulle
@login_required(login_url='login')
def home(request):  # Kotisivu sivu
    if request.method == "GET":
        # Haetaan kaikki kuvat ja näytetään ne uusimmasta vanhimpaan
        photos = Photo.objects.all().order_by('-date_created')[:30]
        context = {'photos': photos}
    return render(request, 'accounts/home.html', context)


# Oman käyttäjän profiili
@login_required(login_url='login')
def userPage(request):
    if request.method == "GET":
        # Haetaan käyttäjän kuvat ja näytetään ne uusimmasta vanhimpaan
        photos = request.user.customer.photo_set.all().order_by('-date_created')
        albums = request.user.customer.album_set.all().order_by('-date_created')
        context = {'photos': photos, 'albums': albums}
    return render(request, 'accounts/user.html', context)


# Albumi sivu
def albumView(request, pk):
    try:
        album = get_object_or_404(Album, id=pk)  # Haetaan kuvaa kuvan id:llä
    except Album.DoesNotExist:
        return redirect ('404')
    context = {'albums': album}
    return render(request, 'accounts/album.html', context)


# Käyttäjän tietojen muuttaminen
@login_required(login_url='login')
def accountSettings(request):

    customer = request.user.customer  # Haetaan käyttäjän tiedot
    form = CustomerForm(instance=customer)  # forms.py tiedostosta haetaan mitä formilla näytetään

    if request.method == 'POST':  # Tarkastetaan että tiedot lähetetään POST muodossa
        # Otetaan käyttäjän muuttamat tiedot muuttujaan, tarkastetaan ja tallennetaan
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()

            return redirect('user-page')  # Käyttäjä ohjataan omaan profiiliinsa

    context = {'form':form}
    return render(request, 'accounts/settings.html', context)


# Kuvien lataaminen
@login_required(login_url='login')
def uploadImage(request):
    user = request.user.customer  # Haetaan käyttäjän nimi

    form = UploadImage(initial={'user': user}, current_user=user)  # Haetaan upload foorumi
    if request.method == 'POST':  # Tarkastetaan että tiedot tulee POST:illa
        form = UploadImage(None, request.POST, request.FILES)
        if form.is_valid():
            # Tallennetaan tiedot siten ettei käyttäjä pysty muuttamaan
            # id:tään f12 kautta toiseksi käyttäjäksi
            reservation = form.save(commit=False)
            reservation.slug = slugify(reservation.title)
            reservation.user = user
            reservation.is_reservation = True
            reservation.save()
            form.save_m2m()
            return redirect('home')  # Sirretään käyttäjä home sivulle

    context = {'form':form}
    return render(request, 'accounts/upload_image.html', context)


# Kuvien poistaminen
@login_required(login_url='login')
def deleteImage(request):
    # Haetaan kaikki käyttäjän kuvat
    photos = request.user.customer.photo_set.all().order_by('-date_created')
    context = {'photos': photos}
    return render(request, 'accounts/delete_image.html', context)


@login_required(login_url='login')
def delete(request, pk):
    image = Photo.objects.get(id=pk)  # Haetaan kuvaa kuvan id:llä
    # Jos käyttäjä yrittää poistaa toisen kuvaa, hänet ohjataan 404
    if (image.user != request.user.customer):
        return redirect ('404')
    else:
        if request.method == "POST":
            image.delete()
            return redirect('delete_image')
    
    context = {'photo':image}
    return render(request, 'accounts/delete.html', context)


# Albumin poistaminen
@login_required(login_url='login')
def deleteAlbum(request):
    # Haetaan kaikki käyttäjän albumit
    albums = request.user.customer.album_set.all().order_by('-date_created')
    context = {'albums': albums}
    return render(request, 'accounts/delete_album.html', context)


@login_required(login_url='login')
def deleteAlbumConfirm(request, pk):
    album = Album.objects.get(id=pk)  # Haetaan albumia id:llä
    # Jos käyttäjä yrittää poistaa toisen albumia, hänet ohjataan 404
    if (album.user != request.user.customer):
        return redirect ('404')
    else:
        if request.method == "POST":
            album.delete()
            return redirect('delete_album')
    
    context = {'album': album}
    return render(request, 'accounts/delete_album_confirm.html', context)


# Kuva-albumin luonti sivu
@login_required(login_url='login')
def createAlbum(request):
    user = request.user.customer  # Haetaan käyttäjän nimi

    form = CreateAlbum(initial={'user': user})  # Haetaan upload foorumi
    if request.method == 'POST':  # Tarkastetaan että tiedot tulee POST:illa
        form = CreateAlbum(request.POST)
        # Tallennetaan tiedot siten ettei käyttäjä pysty muuttamaan
        # id:tään f12 kautta toiseksi käyttäjäksi
        reservation = form.save(commit=False)
        reservation.user = user
        reservation.is_reservation = True
        reservation.save()
        return redirect('home')  # Sirretään käyttäjä home sivulle

    context = {'form':form}
    return render(request, 'accounts/create-album.html', context)



# Käyttäjien löytäminen
def profile(request, username=None):
    if username:  # Jos urliin annetaan validi käyttäjänimi, mennään hänen profiiliin
        utente = Customer.objects.filter(user__username=username)  # Haetaan käyttäjän tiedot
        # Haetaan käyttäjän kuvat
        photo = Photo.objects.filter(user__user__username=username).order_by('-date_created')
        # Haetaan käyttäjän albumit
        albums = Album.objects.filter(user__user__username=username).order_by('-date_created')

    else:
        utente = "utente"
        photo = "photos"
        albums = "albums"

    context = {'users' : utente, 'photos' : photo, 'albums' : albums}
    return render(request, 'accounts/profile.html', context)


# Kuvan sivu
def imageView(request, pk):
    try:
        image = Photo.objects.get(id=pk)  # Haetaan kuvaa kuvan id:llä
    except Photo.DoesNotExist:
        return redirect ('404')
    context = {'photo': image}
    return render(request, 'accounts/image.html', context)

# Pienen thumbnailin sivu
def imageViewSmall(request, pk):
    try:
        image = Photo.objects.get(id=pk)  # Haetaan kuvaa kuvan id:llä
    except Photo.DoesNotExist:
        return redirect (request, 'accounts/404.html')
    context = {'photo': image}
    return render(request, 'accounts/image_small.html', context)

# Suuren thumbnailin sivu
def imageViewLarge(request, pk):
    try:
        image = Photo.objects.get(id=pk)  # Haetaan kuvaa kuvan id:llä
    except Photo.DoesNotExist:
        return redirect (request, 'accounts/404.html')
    context = {'photo': image}
    return render(request, 'accounts/image_large.html', context)

# 404 sivu
def pageNotFound(request, exception=None):
    return render(request, 'accounts/404.html', status=404)


# 500 sivu
def error_500(request):
    return render(request, 'accounts/500.html', status=500)


# Käyttäjän poistaminen
@login_required(login_url='login')
def deleteUser(request, username):
    # Jos käyttäjää ei ole, 404
    user = get_object_or_404(User, username=username)
    try:
        #Jos käyttäjänimi ei ole sama kuin poistettavan käyttäjän, 404
        if (user.username != request.user.username):
            return redirect ('404')
        
        if request.method == "POST":
            password = request.POST.get('password')  # Kysytään salasana
            user_password = authenticate(request, username=user.username, password=password)
            if user_password is not None:  # Jos kaikki on oikein
                user.delete()  # Poistetaan käyttäjä
                messages.success(request, f"{username} was deleted")  # Viesti

                return redirect('login')  # Käyttäjän ohjaus login sivulle

            else:  # Jos salasana ei ole oikea, viesti
                messages.info(request, 'Password is incorrect')

    except:
        return redirect('404')

    context = {'username': user}
    return render(request, 'accounts/delete_user.html', context)


def detail_view(request, slug):
    post = get_object_or_404(Photo, slug=slug)
    context = {'post': post}
    return render(request, 'accounts/detail.html', context)

def tagged(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Photo.objects.filter(tags=tag).order_by('-date_created')
    context = {'tag':tag, 'posts': posts}
    return render(request, 'accounts/detail.html', context)


# Haku
def search(request):
    search_term = ''
    common_tags = Photo.tags.most_common()[:10]

    if 'search' in request.GET:
        search_term = request.GET['search']  # Haetaan hakusana
        return redirect(f"/tag/{search_term}/")  # Ohjataan käyttäjä "/tag/hakusana"

    context = {'common_tags': common_tags}
    return render(request, 'accounts/search.html', context)

