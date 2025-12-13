from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from .models import Movie
from django.db.models import Prefetch, Count
import requests
from django.db.models.expressions import RawSQL
import datetime
from django.utils import timezone

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
    update_movie_information(request, movie_id)
    users = User.objects.all().order_by('username')
    
    # Aktuelles User-Rating holen
    current_user_id = request.session.get('current_user_id')
    current_user = get_object_or_404(User, id=current_user_id)
    user_rating = current_user.userprofile.movie_ratings.get(str(movie_id), {}).get('rating', None)
    
    seen = set()
    flatrate_offers = []
    for offer in requested_movie.offers:
        if offer['type'].startswith('FLATRATE') and offer['name'] not in seen:
            flatrate_offers.append(offer)
            seen.add(offer['name'])
    
    return render(request, 'movies/movie_page.html', {
        'movie': requested_movie, 
        'offers': flatrate_offers, 
        'users': users,
        'user_rating': user_rating
    })

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
        "timestamp": timezone.now(),
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

@require_POST
@require_user_session
def rate_movie(request, movie_id):
    current_user_id = request.session.get('current_user_id')
    user = get_object_or_404(User, id=current_user_id)
    movie = get_object_or_404(Movie, id=movie_id)
    
    rating = request.POST.get('rating')
    
    if rating:
        try:
            rating_value = float(rating)
            if 0 <= rating_value <= 10:
                user.userprofile.movie_ratings[str(movie_id)] = {
                    'rating': rating_value,
                    'rated_at': timezone.now().isoformat(),
                }
                user.userprofile.save()
        except (ValueError, TypeError):
            pass
    
    return redirect('movies:movie_page', movie_id=movie_id)

@require_user_session
def addMovieEvent(request, movie_id):
    # Einem Film kann über die movie_page ein History-Eintrag hinzugefügt werden, dieser kann in der Hall of Fame eingesehen werden
    movie = get_object_or_404(Movie, id=movie_id)
    
    if request.method == 'POST':
        # Daten aus dem POST-Request extrahieren
        date = request.POST.get('date')
        attendee_ids = request.POST.getlist('attendees')  # Liste der Teilnehmer-IDs
        rating = None
        
        # Validierung
        if date and attendee_ids:
            try:
                
                # User-IDs validieren
                valid_attendee_ids = []
                ratings = []
                for user_id in attendee_ids:
                    try:
                        # Prüfen ob User existiert
                        user = User.objects.get(id=int(user_id))
                        # Ratings in die Liste jeeten
                        user_rating = user.userprofile.movie_ratings.get(str(movie_id), {}).get('rating', None)
                        if user_rating is not None:
                            ratings.append(float(user_rating))
                        
                        valid_attendee_ids.append(int(user_id))
                    except (User.DoesNotExist, ValueError):
                        continue  # Ungültige User-ID überspringen
                    
                
                # Film rating für das Event berechnen -> Jeder User hat ein JSON mit Filmen für die er gevotet hat
                    
                rating_float = round(sum(ratings) / len(ratings),2) if ratings else None
                
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
    
        # The users how watched the movie has to be removed from the movie votes
        for user_id in attendee_ids:
            try:
                user = User.objects.get(id=int(user_id))
                if movie.votes.filter(id=user.id).exists():
                    movie.votes.remove(user)
            except (User.DoesNotExist, ValueError):
                continue  # Ungültige User-ID überspringen
    return redirect('movies:movie_page', movie_id=movie_id)

# update film 
# Diese Methode wird aufgerufen, wenn der Timestamp des Films älter als ein Tag ist -> TODO:In Datenbank anlegen, um die Streaming-Informationen aktuell zu halten
@require_user_session
def update_movie_information(request, movie_id):
    
    movie = get_object_or_404(Movie, id=movie_id)
    
    if movie.timestamp < timezone.now() - datetime.timedelta(days=1):
        # API-Request an JustWatch mit movie_title als Suchbegriff
        api_url = "https://imdb.iamidiotareyoutoo.com/justwatch"
        params = {"q": movie.title, "L": "de_DE"}
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
            return redirect('movies:movie_page', movie_id=movie_id)

        # Update offers und timestamp
        movie.offers = movie_data.get("offers", [])
        movie.timestamp = timezone.now()
        movie.save()
    
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
        return redirect('movies:user_page', id=user.id)  # Redirect zurück zur User Page
    
    # GET request fallback - redirect to user page
    current_user_id = request.session.get('current_user_id')
    user = get_object_or_404(User, id=current_user_id)
    return redirect('movies:user_page', id=user.id)



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
        
        return redirect('movies:user_page', id=user.id)  # Redirect zurück zur User Page
    
    # GET request fallback - redirect to user page
    current_user_id = request.session.get('current_user_id')
    user = get_object_or_404(User, id=current_user_id)
    return redirect('movies:user_page', id=user.id)

