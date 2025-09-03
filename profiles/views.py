from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from movies.models import UserProfile
from django.db import IntegrityError

# Alle Funktionen in der Profiles App erfordern eine Master-Auth
# Kein Plan wie der Shit funktioniert 100% Claude TODO: verstehen
def require_master_auth(view_func):
    """Decorator: Nur mit Master-Authentifizierung zugelassen"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('master_authenticated'):
            return redirect('authentication:master_login')
        return view_func(request, *args, **kwargs)
    return wrapper
# Ist die Session nicht durch das master pw freigegeben wird der nutzer zu pw eingabe umgeleitet


# Gibt alle User zurück bzw rendert die User Selection
@require_master_auth
def profile_selection(request):
    """Zeigt alle verfügbaren Profile zur Auswahl"""
    # Alle User mit UserProfile holen
    users_with_profiles = User.objects.filter(userprofile__isnull=False).select_related('userprofile')
    
    return render(request, 'profiles/profile_selection.html', {
        'users': users_with_profiles
    })

# User wird in der Session gespeichert und der Nutzer wird an die Main Page weitergeleitet
@require_master_auth  
def select_profile(request, user_id):
    """User auswählen und zur Movies-App weiterleiten"""
    user = get_object_or_404(User, id=user_id, userprofile__isnull=False)
    
    # Ausgewählten User in Session speichern
    request.session['current_user_id'] = user.id
    request.session['current_username'] = user.username
    
    # Zu Dashboard weiterleiten (ohne user_id in URL)
    return redirect('movies:user_dashboard')


# Show register Page
@require_master_auth
def show_create_profile(request):
    """Zeigt die Seite zum Erstellen eines neuen Profils an"""
    return render(request, 'profiles/profile_create.html')

@require_master_auth
def create_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        profile_image = request.FILES.get('profile_image')

        if not username:
            messages.error(request, "Benutzername darf nicht leer sein.")
            return render(request, 'profiles/profile_create.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Benutzername existiert bereits.")
            return render(request, 'profiles/profile_create.html')

        try:
            new_user = User.objects.create(username=username)
            # UserProfile wird durch Signal automatisch erstellt!
            if profile_image:
                new_user.userprofile.profile_image = profile_image
                new_user.userprofile.save()
            return redirect('profiles:selection')
        except Exception as e:
            messages.error(request, f"Fehler beim Erstellen des Profils: {str(e)}")
            return render(request, 'profiles/profile_create.html')

    return render(request, 'profiles/profile_create.html')