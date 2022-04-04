"""
Django settings for eddi_backend project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
#!/usr/local/bin/python

from pathlib import Path
import os
from django.conf.global_settings import LANGUAGES as DJANGO_LANGUAGES
import datetime


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '56bly)en(6j7r2!f5z_g-uo&rjclo9@irwvx1thds5xe*d2n$h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True




ALLOWED_HOSTS = ['https://eddi-backend.testyourapp.online','127.0.0.1'] 

CORS_ALLOWED_ORIGINS = [
    'https://eddi-backend.testyourapp.online',
]
CSRF_TRUSTED_ORIGINS=['https://eddi-backend.testyourapp.online'] 

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'eddi_app',
    'ckeditor',
    'rest_framework',
    'rest_framework_swagger',
    'corsheaders'
]
# LOCALE_PATHS = [os. path.join(BASE_DIR, 'locale')]
JAZZMIN_SETTINGS = {
    "language_chooser": True,
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Eddi Admin",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Eddi",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "Eddi",

    # Logo to use for your site, must be present in static files, used for brand on top left
    # "site_logo": "books/img/logo.png",

    # CSS classes that are applied to the logo above
    "site_logo_classes": "img-circle",
     

"custom_links": {
        "eddi_app": [{
            "name": "Home Page", 
            "url": "/admin/eddi_app/homepagecms/1/change/", 
            "icon": "fas fa-home",
        },
        {
            "name": "About Us Page", 
            "url": "/admin/eddi_app/aboutuspagecms/1/change/", 
            "icon": "fas fa-info",
        },
        {
            "name": "Contact Us Page", 
            "url": "/admin/eddi_app/contactuspagecms/1/change/", 
            "icon": "fas fa-phone",
        },
        {
            "name": "Privacy Policy Page", 
            "url": "/admin/eddi_app/privacypolicycms/1/change/", 
            "icon": "fas fa-file-contract",
        },
        {
            "name": "Terms & Conditions Page", 
            "url": "/admin/eddi_app/termsconditioncms/1/change/", 
            "icon": "fas fa-file-signature",
        },
        ],
   
       
    },


    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": None,
    "changeform_format": "collapsible",
    "hide_models": [
    # 'eddi_app.HomePageCMSBanner',
    # 'eddi_app.utl_status',
    # 'eddi_app.UserType',
    # 'eddi_app.approval_status',
    # 'eddi_app.UserSignup',
    # 'eddi_app.CourseCategoryDetails',
    # 'eddi_app.CourseSubCategoryDetails',
    # 'eddi_app.CourseDetails',
    # 'eddi_app.TestinomialsDetails',
    # 'eddi_app.BlogDetails',
    # 'eddi_app.HomePageCMSPartners',
    # 'eddi_app.HomePageCMS',
    # 'eddi_app.AboutUsPageCMS',
    # 'eddi_app.PrivacyPolicyCMS',
    # 'eddi_app.TermsConditionCMS',
    # 'eddi_app.FeeType',
    # 'eddi_app.ContactUsPageCMS',
    # 'eddi_app.CourseLevel',
    # 'eddi_app.CourseType',



    

    


    ],
     "order_with_respect_to": ["eddi_app.HomePageCMS", "eddi_app.AboutUsPageCMS"],
    

    # Welcome text on the login screen
    "welcome_sign": "Welcome to Eddi",
     "copyright": "Eddi",
     "custom_js": "main.js"
}
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', #added here
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
REST_AUTH_TOKEN_MODEL = "eddi_app.models.NonBuiltInUserToken"
REST_AUTH_TOKEN_CREATOR = "eddi_app.utils.custom_create_token"
ROOT_URLCONF = 'eddi_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                
                'django.template.context_processors.debug',

                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'eddi_backend.wsgi.application'
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
       
        "eddi_app.authentication.ExpiringTokenAuthentication", # <-- with this line 
        "rest_framework.authentication.SessionAuthentication",
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'eddi_app.permissions.IsValid', )
 # ...
}
CKEDITOR_CONFIGS = {
    'default': {
        
        
        'width': '100%',
        'toolbarCanCollapse': False,
    },
}

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'Eddi_db',
        'USER': 'Eddi_db',
        'PASSWORD': 'W0rxQxlWsKuCekrg',
        'HOST': 'eddi-backend.testyourapp.online',
        'PORT': '3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
LANGUAGES = [
    ('sv', ('Swedish')),
    ('en', ('English')),
]
CMS_TEMPLATES = (
    ('page.html', 'Page'),  # any name should work
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

MEDIA_ROOT  = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

TOKEN_TTL = datetime.timedelta(days=15) #Authentication Token Lifetime

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'testing.skillism@gmail.com'
EMAIL_HOST_PASSWORD = 'Latitude@123' 



STRIPE_PUBLIC_KEY = 'pk_test_51KhDqeEjvkdtZsC4cUmvapGjtOYTru6hGp8EOK1KBdZkp7pQfBYMY4XAhkJ0WY2OAjIhpYXtXI2ia9slbSlnvPuy00XyRs254B'
STRIPE_SECRET_KEY = 'sk_test_51KhDqeEjvkdtZsC4aOLUytltjWx0sYj5rZpkcphI6jbxtUHw7Lq5HxGxpRfX8aSO1jj2rNVyH74eTWVeeWZk01DX007SRf9wfX'
STRIPE_WEBHOOK_SECRET = ""