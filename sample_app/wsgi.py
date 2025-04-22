import os
from django.core.wsgi import get_wsgi_application

# Set the default settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sample_app.settings.production')

# Apply WhiteNoise for static files
application = get_wsgi_application()

# Add WhiteNoise (make sure to install whitenoise in requirements.txt)
try:
    from whitenoise import WhiteNoise
    application = WhiteNoise(application, root=os.getenv('STATIC_ROOT'))
except ImportError:
    pass
