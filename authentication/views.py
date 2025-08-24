from django.shortcuts import render,redirect
from django.contrib import messages
from .models import MasterPassword


def master_login(request):
    # Wenn der User bereits eingelogt ist wird er sofort weitergeleitet, vorerst zu movies später zu profiles
    if request.session.get('master_authenticated'):
        # return redirect('/movies/') # -> Später profiles
        return redirect('profiles:selection')  # Zu Profil-Auswahl statt movies
    
    if request.method == 'POST':
        entered_password = request.POST.get('master_password')
        
        # Abgleich mit Passwort aus der Datenbank
        
        try:
            master_pw = MasterPassword.objects.first()
            if master_pw and master_pw.password == entered_password:
                # Korrekte PW Eingabe -> 'Session setzten'
                request.session['master_authenticated'] = True
                request.session.set_expiry(0) # Die Session sollte beim Schließen des Browsers ablaufen
                # return redirect('/movies/') # Später profiles
                return redirect('profiles:selection')
            else:
                messages.error(request, 'Falsches Passwort!')
        except:
            messages.error(request, 'Fehler beim Login!')
    
        # Login-Seite anzeigen
    return render(request, 'authentication/master_login.html')

#TODO Logout im HTML einbauen
def logout(request):
    """Komplette Session löschen und zu Master-Login"""
    request.session.flush()
    return redirect('authentication:master_login')