from django.db import models

# Wir brauchen kein eigenes Model, da wir movies.UserProfile verwenden
# UserProgile erweitert das bestehende DjangoModel um ein einzelnes Profilbild pro User
from movies.models import UserProfile