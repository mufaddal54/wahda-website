import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wahda_site.settings")

from wahda_site.wsgi import application

app = application
