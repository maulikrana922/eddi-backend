"""eddi_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
   
    path('',include('eddi_app.urls')),
    path('rosetta/',include('rosetta.urls')),
    path("i18n/", include("django.conf.urls.i18n")),
    path('openapi/', get_schema_view(
        title="Eddi Api Service",
        description="API developers hpoing to use our service"
    ), name='openapi-schema'),
    path('docs/7e3f7124d67d0b6471842d311388b818/', TemplateView.as_view(
        template_name='documentation.html',
        extra_context={'schema_url':'openapi-schema'}
    ), name ='swagger-ui'),
    path('__debug__/', include('debug_toolbar.urls')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

 

urlpatterns +=staticfiles_urlpatterns()

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),

)
