# Setup Guide für den Ubuntu Server (noch nicht getestet)

## Vorbereitungen

1. System updaten

```bash
sudo apt update
sudo apt upgrade -y
```

2. Benötigte Pakete instalisieren ;)

```bash
sudo apt install -y python3-pip python3-dev python3-venv nginx curl
```

3. Firewall konfigurieren?

```bash
sudo ufw allow 'OpenSSH'
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

4. Django Project in den gewünschten Ordner clonen

## Python-Umgebung einrichten

1. Im Ordner Film-Forum-4.0 eine Virtuelle Umgebung einrichten

```bash
python3 -m venv .venv

source myenv/bin/activate

pip install -r requirements.txt
pip install gunicorn
```

## Project konfigurieren

1. .env Datei mit folgenden Informationen anlegen (auf Ebene der manage.py file)

```
# .env

SECRET_KEY='django-insecure-nrh=superGeheimerKey'

DEBUG=False
```

Oder Manuel anpassen (nicht empfohlen!)

```python
DEBUG = False

ALLOWED_HOSTS = ['Domain', 'ip-Adresse'] # Anpassen!

# Statische Dateien
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# Medien-Dateien (falls benötigt)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
```

2. Statische Dateien Sammeln

```bash
python manage.py collectstatic
```

3. Datenbank migrieren

```bash
python manage.py migrate
```

4. Einen Superuser einrichten

```bash
python manage.py createsuperuser
```

## Gunicorn konfigurieren

1. Socket Datei für Gunicorn erstellen 

```bash
sudo nano /etc/systemd/system/gunicorn.socket
```

Inhalt:

```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

2. Service Datei für Gunicorn erstellen

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Inhalte:

```ini
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=username # Benutzername angeben
Group=www-data
WorkingDirectory= # Pfad zu Projekt ohne "" Bsp.: /home/username/meinprojekt
ExecStart=/home/username/meinprojekt/myenv/bin/gunicorn \ # Hier ensprechend den Pfad anpassen
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          meinprojekt.wsgi:application # meinproject durch Projectnamen ersetzen

[Install]
WantedBy=multi-user.target
```

3. Gunicorn Service starten

```bash
# Socket starten und aktivieren
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket

# Service starten
sudo systemctl start gunicorn.service
sudo systemctl enable gunicorn.service
```

Status überprüfen:

```bash
# Prüfe ob der Service läuft
sudo systemctl status gunicorn

# Prüfe ob der Socket läuft
sudo systemctl status gunicorn.socket

# Falls Fehler: Logs anzeigen
sudo journalctl -u gunicorn --since "5 minutes ago"
sudo journalctl -u gunicorn -f  # Live-Logs
```

## Nginx konfigurieren

1. Config erstellen:

```bash
sudo nano /etc/nginx/sites-available/meinproject # Projectname anpassen
```

Inhalt:

```nginx
server {
    listen 80;
    server_name deine-domain.de server_ip_adresse; # An entsprechenden Server anpassen

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/username/meinprojekt; # Pfad zu Project
    }
    
    location /media/ {
        root /home/username/meinprojekt; # Pfad zu Project
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

2. Konfiguration aktivieren

```bash
sudo ln -s /etc/nginx/sites-available/meinprojekt /etc/nginx/sites-enabled/
```

Testen:

```bash
sudo nginx -t
```

Neustarten:

```bash
sudo systemctl restart nginx
```

## Berechtigungen

1. Verzeichnisse

```bash
# Projektverzeichnis
sudo chown -R username:www-data /home/username/meinprojekt  # Pfad anpassen

# Berechtigungen setzen
sudo chmod -R 755 /home/username/meinprojekt  # Pfad anpassen

# Media
sudo chmod -R 775 /home/username/meinprojekt/media  # Pfad anpassen falls media existiert
```

2. Datenbank

```bash
# Finde den genauen Namen deiner Datenbank-Datei
# (steht in settings.py unter DATABASES -> NAME)
ls -la /home/username/meinprojekt/  # Pfad anpassen

# Berechtigungen für die Datenbank-Datei setzen
sudo chmod 664 /home/username/meinprojekt/db.sqlite3  # HIER: Dateiname und Pfad anpassen
sudo chown www-data:www-data /home/username/meinprojekt/db.sqlite3  # Anpassen
```

# Laut Deepseek: Nach Änderungen immer daran denken:

1. Bei Django-Änderungen:

```bash
source myenv/bin/activate  # Virtuelle Umgebung aktivieren
python manage.py collectstatic
python manage.py migrate
deactivate  # Virtuelle Umgebung verlassen
```

2. Bei Service-Änderungen:

```bash
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```
3. Bei Nginx-Änderungen:

```bash
sudo nginx -t  # Immer zuerst testen!
sudo systemctl reload nginx
```