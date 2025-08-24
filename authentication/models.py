from django.db import models

# Das Master-Passwort Modell dient dazu das Master-Passwort in der Datenbank zu speichern und zu verwalten.
# Es enthält ein Passwort-Feld und Zeitstempel für die Erstellung und Aktualisierung.
# Das Passwort wird standardmäßig auf "$film-forum$" gesetzt, kann aber über das Admin-Interface geändert werden.

class MasterPassword(models.Model):
    password = models.CharField(max_length=255, default="$film-forum$")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Master Password"