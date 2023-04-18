import environ
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env()

SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don"t run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    "debug_toolbar",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tinymce",
    "notes.apps.NotesConfig",
    "accounts.apps.AccountsConfig",
    "django_cleanup.apps.CleanupConfig",
    "captcha",

]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "StudyNotes.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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
WSGI_APPLICATION = "StudyNotes.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("DATABASE_NAME"),
        "USER": env("DATABASE_USER"),
        "PASSWORD": env("DATABASE_PASSWORD"),
        "HOST": env("DATABASE_HOST"),
        "PORT": env("DATABASE_PORT"),
    }
}

# Password validation
AUTH_USER_MODEL = "accounts.CustomUser"
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
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "notes/static",
]
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_FORM = env("EMAIL_FORM")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = True
PASSWORD_RESET_TIMEOUT = 14400  # 4 hours

# Captcha
RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY")
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

# Tinymce
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
# TINYMCE_JS_URL = os.path.join(STATIC_URL, "path/to/tiny_mce/tiny_mce.js")
TINYMCE_DEFAULT_CONFIG = {
    "custom_undo_redo_levels": 100,
    "selector": "textarea",
    "menubar": "file edit view insert format tools table help",
    "plugins": "link image preview codesample contextmenu table code lists fullscreen",
    "toolbar1": "undo redo | backcolor casechange permanentpen formatpainter removeformat formatselect fontselect fontsizeselect",
    "toolbar2": "bold italic underline blockquote | alignleft aligncenter alignright alignjustify "
               "| bullist numlist | outdent indent | table | link image | codesample | preview code | tiny_mce_wiris_formulaEditor tiny_mce_wiris_formulaEditorChemistry",
    "contextmenu": "formats | link image",
    "block_formats": "Paragraph=p; Header 1=h1; Header 2=h2",
    "fontsize_formats": "8pt 10pt 12pt 14pt 16pt 18pt",
    "content_style": "body { font-family: Arial; background: white; color: black; font-size: 12pt}",
    "codesample_languages": [
        {"text": "Python", "value": "python"}, {"text": "HTML/XML", "value": "markup"}, ],
    "image_class_list": [{"title": "Fluid", "value": "img-fluid", "style": {}}],
    "width": "auto",
    "height": "600px",
    "image_caption": True,
    "images_upload_url": "upload_image",
}

if DEBUG:
    import socket
    import mimetypes
    mimetypes.add_type("application/javascript", ".js", True)
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]

                                                                 