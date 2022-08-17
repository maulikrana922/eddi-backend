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
import environ

from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

import os

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'root': {
#         'handlers': ['console'],
#         'level': 'WARNING',
#     },
# }

env = environ.Env()
environ.Env.read_env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!!
DEBUG = env.bool('DEBUG', default=True)




ALLOWED_HOSTS = env('ALLOWED_HOSTS').split(",")

CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS').split(",")
CSRF_TRUSTED_ORIGINS= env('CSRF_TRUSTED_ORIGINS').split(",")

# Application definition
INSTALLED_APPS = [
    'django_crontab',
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
    'corsheaders',
    'wkhtmltopdf',
    'rosetta',
    'debug_toolbar',
]


LOCALE_PATHS = [os. path.join(BASE_DIR, 'locale')]

production_models = [
    'eddi_app.HomePageCMSBanner',
    'eddi_app.utl_status',
    'eddi_app.UserType',
    'eddi_app.approval_status',
    # 'eddi_app.UserSignup',
    'eddi_app.CourseCategoryDetails',
    'eddi_app.CourseSubCategoryDetails',
    'eddi_app.CourseDetails',
    # 'eddi_app.TestinomialsDetails',
    'eddi_app.BlogDetails',
    'eddi_app.HomePageCMSPartners',
    'eddi_app.HomePageCMS',
    'eddi_app.AboutUsPageCMS',
    'eddi_app.PrivacyPolicyCMS',
    'eddi_app.TermsConditionCMS',
    'eddi_app.FeeType',
    'eddi_app.ContactUsPageCMS',
    'eddi_app.CourseLevel',
    'eddi_app.CourseType',
    'eddi_app.CourseEnroll',
    'eddi_app.FavouriteCourse',
    'eddi_app.NonBuiltInUserToken',
    'eddi_app.UserProfile',
    'eddi_app.UserPaymentDetail',
    'eddi_app.Header_FooterCMS',
    'eddi_app.EventAd',
    'eddi_app.RecruitmentAd',
    'eddi_app.EventAdPaymentDetail',
    'eddi_app.EventAdEnroll',
    'eddi_app.CourseMaterial',
    'eddi_app.InvoiceData',
    'eddi_app.InvoiceDataEvent',
    'eddi_app.MaterialVideoMaterial',
    'eddi_app.MaterialDocumentMaterial',
    'eddi_app.SupplierOrganizationProfile',
    'eddi_app.SupplierProfile',
    'eddi_app.Notification',
    'eddi_app.TermsConditionCMS_SV',
    'eddi_app.InvoiceData',
    'eddi_app.HomePageCMS_SV',
    'eddi_app.HomePageCMSPartners',
    'eddi_app.HomePageCMSBanner_SV',
    'eddi_app.Header_FooterCMS',
    'eddi_app.Header_FooterCMS_SV',
    'eddi_app.CourseRating',
    'eddi_app.CourseMaterialStatus',
    'eddi_app.ContactUsPageCMS_SV',
    'eddi_app.BlogDetails_SV',
    'eddi_app.AboutUsPageCMS_SV',
    'eddi_app.HomePageCMSPartners_SV',
    'eddi_app.PrivacyPolicyCMS_SV',
    'eddi_app.CourseBatch',
    'eddi_app.BatchSession',
    'eddi_app.SupplierAccountDetail',
    'eddi_app.SupplierPayoutDetail',
    ]
    
local_models = []
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
            "name": _("Home Page"), 
            "url": "/admin/eddi_app/homepagecms/1/change/", 
            "icon": "fas fa-home",
        },
        {
            "name": _("Home Page SV"), 
            "url": "/admin/eddi_app/homepagecms_sv/1/change/", 
            "icon": "fas fa-home",
        },
        {
            "name": _("About Us Page"), 
            "url": "/admin/eddi_app/aboutuspagecms/1/change/", 
            "icon": "fas fa-info",
        },
        {
            "name": _("About Us Page SV"), 
            "url": "/admin/eddi_app/aboutuspagecms_sv/1/change/", 
            "icon": "fas fa-info",
        },
        {
            "name": _("Contact Us Page"), 
            "url": "/admin/eddi_app/contactuspagecms/1/change/", 
            "icon": "fas fa-phone",
        },
        {
            "name": _("Contact Us Page SV"), 
            "url": "/admin/eddi_app/contactuspagecms_sv/1/change/", 
            "icon": "fas fa-phone",
        },
        {
            "name": _("Privacy Policy Page"), 
            "url": "/admin/eddi_app/privacypolicycms/1/change/", 
            "icon": "fas fa-file-contract",
        },
        {
            "name": _("Privacy Policy Page SV"), 
            "url": "/admin/eddi_app/privacypolicycms_sv/1/change/", 
            "icon": "fas fa-file-contract",
        },
        {
            "name": _("Terms & Conditions Page"), 
            "url": "/admin/eddi_app/termsconditioncms/1/change/", 
            "icon": "fas fa-file-signature",
        },
        {
            "name": _("Terms & Conditions Page SV"), 
            "url": "/admin/eddi_app/termsconditioncms_sv/1/change/", 
            "icon": "fas fa-file-signature",
        },
        ],
   
       
    },


    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": None,
    "changeform_format": "collapsible",

    "hide_models": production_models,
    # "hide_models": local_models,
    "order_with_respect_to": ["eddi_app.HomePageCMS", "eddi_app.AboutUsPageCMS"],
    

    # Welcome text on the login screen
    "welcome_sign": "Welcome to Eddi",
     "copyright": "Eddi",
     "custom_js": "main.js"
}
MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
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
INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
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


DATABASES = {
     
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }

    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASS'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('PORT'),
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
    ('sv', _(u'Swedish')),
    ('en', _(u'English')),
]
CMS_TEMPLATES = (
    ('page.html', _('Page')),  # any name should work
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

MEDIA_ROOT  = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

TOKEN_TTL = datetime.timedelta(days=15) #Authentication Token Lifetime

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
WKHTMLTOPDF_CMD = env('WKHTMLTOPDF_CMD')


STRIPE_PUBLIC_KEY='pk_test_51LT5qWF219DjFxE14L3x0UwNEmGNMDfnTl01wQVgS7ORaVSAl66BHGEoRy8ciUs4TA2FMMIAEp6L7HQtwkaUdfvj00MfVoPYJ7'
STRIPE_SECRET_KEY='sk_test_51LT5qWF219DjFxE1R3LS85B4AMsM1ZJLbogPB0Q3vUfluAa8DRbcqzsWjhZJCm52FQi6jxw4h6vq1N3iRKgtTP4s00UZq8ynLz'


STRIPE_WEBHOOK_SECRET = ""

CRONJOBS = [
    # ('*/1 * * * *', 'eddi_app.cron.my_cron_job'),
    # ('*/1 * * * *', 'eddi_app.cron.my_cron_job_event'),
    # ('*/1 * * * *', 'eddi_app.cron.my_cron_job_course'),
    # ('*/1 * * * *', 'eddi_app.cron.my_cron_job_login'),
    ('*/1 * * * *', 'eddi_app.cron.my_cron_job_balance'),
]
