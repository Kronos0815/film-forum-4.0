from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from .models import Movie
from django.db.models import Prefetch, Count
import requests
from django.db.models.expressions import RawSQL

# Session-Decorator für Master-Auth und User-Session
def require_user_session(view_func):
    """Decorator: Überprüft Master-Auth und aktive User-Session"""
    def wrapper(request, *args, **kwargs):
        # 1. Master-Passwort prüfen
        if not request.session.get('master_authenticated'):
            return redirect('authentication:master_login')
        
        # 2. User-Session prüfen  
        if not request.session.get('current_user_id'):
            return redirect('profiles:selection')
            
        return view_func(request, *args, **kwargs)
    return wrapper
# Kein Plan wie das eigentlich funktioniert

@require_user_session
def movie_page(request, movie_id):
    requested_movie = get_object_or_404(Movie, id=movie_id)
    users = User.objects.all().order_by('username')
    seen = set()
    flatrate_offers = []
    for offer in requested_movie.offers:
        if offer['type'].startswith('FLATRATE') and offer['name'] not in seen:
            flatrate_offers.append(offer)
            seen.add(offer['name'])
    return render(request, 'movies/movie_page.html', {'movie': requested_movie, 'offers': flatrate_offers, 'users': users})

@require_user_session
def user_dashboard(request):
    """Personalisiertes Dashboard - behält movie_list Logik bei"""
    # Aktuellen User aus Session holen
    current_user_id = request.session.get('current_user_id')
    current_user = get_object_or_404(User, id=current_user_id)
    
    # Ihre bestehende movie_list Logik
    users = User.objects.all().order_by('username')
    movies = (
        Movie.objects
        .annotate(vote_count=Count('votes', distinct=True))
        .filter(vote_count__gt=0)
        .prefetch_related('votes')
        .order_by('-vote_count', 'title')
    )
    return render(request, 'movies/user_dashboard.html', {
        'movies': movies, 
        'users': users,
        'current_user': current_user
    })


# Fallback für bestehende movie_list URLs
def movie_list(request):
    """Leitet zur User-Dashboard weiter"""
    return redirect('movies:user_dashboard')

@require_POST
@require_user_session
def movie_unvote(request, movie_id):
    # User aus Session holen statt request.user
    current_user_id = request.session.get('current_user_id')
    user = get_object_or_404(User, id=current_user_id)
    
    movie = get_object_or_404(Movie, id=movie_id)

    # Remove the user's vote if it exists
    if movie.votes.filter(id=user.id).exists():
        movie.votes.remove(user)

    return redirect('movies:user_dashboard')

@require_POST
@require_user_session
def movie_vote_search(request, movie_id, movie_title):
    # User aus Session holen statt request.user
    current_user_id = request.session.get('current_user_id')
    user = get_object_or_404(User, id=current_user_id)

    # 1. API-Request an JustWatch mit movie_title als Suchbegriff
    api_url = "https://imdb.iamidiotareyoutoo.com/justwatch"
    params = {"q": movie_title, "L": "de_DE"}
    response = requests.get(api_url, params=params)
    data = response.json()

    # 2. Film anhand der ID aus der API-Antwort filtern
    movie_data = None
    for item in data.get("description", []):
        if item.get("id") == movie_id:
            movie_data = item
            break

    if not movie_data:
        # Film nicht gefunden -> zurück zur Liste
        return redirect('movies:user_dashboard')

    # 3. Movie-Objekt in der Datenbank suchen oder anlegen, alle Felder korrekt befüllen
    defaults = {
        "title": movie_data.get("title", ""),
        "year": movie_data.get("year") or 0,
        "runtime": movie_data.get("runtime") or 0,
        "jwURL": movie_data.get("url", ""),
        "imgURL": (movie_data.get("photo_url") or [""])[0],
        "imdbID": movie_data.get("imdbId", ""),
        "jwRating": movie_data.get("jwRating"),
        "tomatoMeter": movie_data.get("tomatoMeter"),
        "offers": movie_data.get("offers", []),
        "backdrops": movie_data.get("backdrops", []),
    }
    movie, created = Movie.objects.get_or_create(
        id=movie_id,
        defaults=defaults
    )

    # 4. Vote hinzufügen, falls noch nicht vorhanden
    if not movie.votes.filter(id=user.id).exists():
        movie.votes.add(user)

    return redirect('movies:user_dashboard')



@require_user_session
def hall_of_fame(request):
    # Current User aus Session holen
    current_user_id = request.session.get('current_user_id')
    current_user = get_object_or_404(User, id=current_user_id)
    
    users = User.objects.all().order_by('username')
    
    # Filme mit nicht-leerer History holen und nach History-Länge sortieren
    watched_movies = Movie.objects.exclude(history=[]).annotate(
        history_count=RawSQL("json_array_length(history)", [])
    ).order_by('-history_count')
    
    return render(request, 'movies/hall_of_fame_movies.html', {
        'watched_movies': watched_movies,
        'requested_user': current_user,
        'users' : users,
    })
    

@require_user_session
def addMovieEvent(request, movie_id):
    # Einem Film kann über die movie_page ein History-Eintrag hinzugefügt werden, dieser kann in der Hall of Fame eingesehen werden
    movie = get_object_or_404(Movie, id=movie_id)
    
    if request.method == 'POST':
        # Daten aus dem POST-Request extrahieren
        date = request.POST.get('date')
        attendee_ids = request.POST.getlist('attendees')  # Liste der Teilnehmer-IDs
        rating = request.POST.get('rating')
        
        # Validierung
        if date and attendee_ids and rating:
            try:
                rating_float = float(rating)
                if 0 <= rating_float <= 10:
                    # User-IDs validieren
                    valid_attendee_ids = []
                    for user_id in attendee_ids:
                        try:
                            # Prüfen ob User existiert
                            User.objects.get(id=int(user_id))
                            valid_attendee_ids.append(int(user_id))
                        except (User.DoesNotExist, ValueError):
                            continue  # Ungültige User-ID überspringen
                    
                    # History-Eintrag hinzufügen falls gültige Attendees vorhanden
                    if valid_attendee_ids:
                        movie.history.append({
                            'date': date,
                            'attendees': valid_attendee_ids,
                            'rating': rating_float
                        })
                        movie.save()
            except ValueError:
                pass  # Ungültiger Rating-Wert
    
    return redirect('movies:movie_page', movie_id=movie_id)


# Shows the profile page of a specific User
@require_user_session
def user_page(request, id):
    requested_user = get_object_or_404(User, id=id)
    voted_movies = requested_user.voted_movies.all().order_by('title')
    return render(request, 'movies/user_votes.html', {'requested_user': requested_user, 'voted_movies': voted_movies})

# View to change the Profile Picture of the current User
@require_user_session
def changeProfilePicture(request):
    if request.method == 'POST' and 'profile_image' in request.FILES:
        current_user_id = request.session.get('current_user_id')
        user = get_object_or_404(User, id=current_user_id)
        profile = user.userprofile
        profile.profile_image = request.FILES['profile_image']
        profile.save()
        return redirect('profiles:selection')  # TODO: Noch anpassen
    return render(request, 'profiles/change_profile_picture.html')  # Noch anpassen

#<form action="{% url 'profiles:change_profile_picture' %}" method="POST" enctype="multipart/form-data">
#  {% csrf_token %}
#  <label for="profile_image">Profilbild auswählen:</label>
#  <input type="file" id="profile_image" name="profile_image" accept="image/*">
#  <input type="submit" value="Hochladen">
#</form>>

# View to change the User Profile Name
@require_user_session
def changeProfileName(request):
    if request.method == 'POST':
        current_user_id = request.session.get('current_user_id')
        user = get_object_or_404(User, id=current_user_id)
        
        new_username = request.POST.get('username', '').strip()
        
        if new_username:
            user.username = new_username
        
        user.save()
        return redirect('profiles:selection') # TODO: Noch anpassen
    return render(request, 'profiles/change_profile_name.html') # Noch anpassen

