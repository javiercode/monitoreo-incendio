# CONFIGURACIÓN GDAL PARA WINDOWS - VERSIÓN CORREGIDA
import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# CONFIGURACIÓN GDAL PARA WINDOWS
if os.name == "nt":  # Windows
    # Buscar GDAL en rutas comunes de conda
    conda_env_path = os.path.dirname(sys.executable)
    
    # Rutas posibles para GDAL.dll
    possible_paths = [
        os.path.join(conda_env_path, "Library", "bin", "gdal.dll"),
        os.path.join(conda_env_path, "..", "Library", "bin", "gdal.dll"),
        r"C:\OSGeo4W\bin\gdal.dll",
        r"C:\Program Files\GDAL\gdal.dll",
    ]
    
    gdal_found = False
    for gdal_path in possible_paths:
        if os.path.exists(gdal_path):
            GDAL_LIBRARY_PATH = gdal_path
            # Buscar geos_c.dll
            geos_path = gdal_path.replace("gdal.dll", "geos_c.dll")
            if os.path.exists(geos_path):
                GEOS_LIBRARY_PATH = geos_path
            else:
                GEOS_LIBRARY_PATH = None
            
            print(f"✅ GDAL encontrado en: {gdal_path}")
            gdal_found = True
            break
    
    if not gdal_found:
        print("⚠️ GDAL no encontrado. Continuando sin configuración GIS completa...")
        GDAL_LIBRARY_PATH = None
        GEOS_LIBRARY_PATH = None
else:
    # Para Linux (no es tu caso)
    GDAL_LIBRARY_PATH = "/usr/lib/libgdal.so"
    GEOS_LIBRARY_PATH = "/usr/lib/libgeos_c.so"

# Quick-start development settings
SECRET_KEY = "django-insecure-clave-secreta-para-desarrollo-bolivia-2024"
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "*"]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",  # IMPORTANTE: GIS support
    "leaflet",  # Maps
    "corsheaders",
    "monitoreo",  # Tu aplicación principal
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "incendios_bolivia.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "incendios_bolivia.wsgi.application"

# Database
# Usar spatialite si GDAL funciona, sino SQLite normal
if GDAL_LIBRARY_PATH and GEOS_LIBRARY_PATH:
    DATABASES = {
        "default": {
            "ENGINE": "django.contrib.gis.db.backends.spatialite",
            "NAME": BASE_DIR / "spatialite.db",
        }
    }
    print("✅ Usando Spatialite para base de datos geoespacial")
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    print("⚠️ Usando SQLite normal (sin soporte GIS completo)")

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "es-es"
TIME_ZONE = "America/La_Paz"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Leaflet config
LEAFLET_CONFIG = {
    "DEFAULT_CENTER": (-16.5, -64.5),
    "DEFAULT_ZOOM": 6,
    "MIN_ZOOM": 3,
    "MAX_ZOOM": 18,
    "RESET_VIEW": False,
    "TILES": [("OpenStreetMap", "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", 
               {"attribution": "&copy; OpenStreetMap contributors"})],
}

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# Logging para desarrollo
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}