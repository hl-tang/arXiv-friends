"""
URL configuration for arXiv_friends project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from arXiv_friends.api import api
from arxiv_search_paper.api import arxiv_search_paper_api
from gpt_simplify.api import gpt_simplify_api
from recommendation.api import recommendation_api
from user_authentication.api import user_authentication_api

api.add_router("", arxiv_search_paper_api)
api.add_router("", gpt_simplify_api)
api.add_router("", recommendation_api)
api.add_router("", user_authentication_api)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", api.urls),
]
