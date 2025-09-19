from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

# UserProfile Model für Profilbilder
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signal um automatisch UserProfile zu erstellen wenn User erstellt wird
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
    else:
        UserProfile.objects.create(user=instance)

# Filme mit:
#     id
#     title
#     year
#     runtime 
#     jwURL
#     imgURL
#     imdbID
#     jwRating
#     tomatoMeter
#     backdrops [] with jasons
#     offers [] with jasons
#     votes [] with users
    
class Movie(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    title = models.CharField(max_length=255)
    year = models.IntegerField()
    runtime = models.IntegerField()
    jwURL = models.URLField(max_length=200)
    imgURL = models.URLField(max_length=200)
    imdbID = models.CharField(max_length=20, unique=True)
    jwRating = models.FloatField(null=True, blank=True)
    tomatoMeter = models.FloatField(null=True, blank=True)
    backdrops = models.JSONField(default=list, blank=True)
    offers = models.JSONField(default=list, blank=True)
    votes = models.ManyToManyField(User, blank=True, related_name='voted_movies')

    def __str__(self):
        return f"{self.title} ({self.year})"
    
class HallOfFame(models.Model):
    
    # Primary Key Automatisch von Django
    
    # Verknüpfung zum Film
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='hall_of_fame_entries')
    
    # Datum des Eintrags
    date_watched = models.DateField()
    
    # Anwesende Kalte Pizza Genießer
    attendees = models.ManyToManyField(User, related_name='hall_of_fame_attendances')
    
    # Created At Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_watched']  # Neueste zuerst
        verbose_name = "Hall of Fame Entry"
        verbose_name_plural = "Hall of Fame Entries"
    
    def __str__(self):
        return f"{self.movie.title} - {self.date_watched.strftime('%Y-%m-%d')}"
    
    def get_attendee_count(self):
        return self.attendees.count()