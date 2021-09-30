"""Poll URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from PollApp import views



urlpatterns = [
     path('home/', views.home, name='home'),
     path('admin/', admin.site.urls),
     path('PollApp/', include('PollApp.urls')),
     path('login/', views.login_user, name='login'),
     path('logout/', views.logout_user, name='logout'),
     path('register/', views.create_user, name='register'),
     path('list/', views.polls_list, name='list'),
     path('list/user/', views.list_by_user, name='list_by_user'),
     path('add/', views.polls_add, name='add'),
     path('edit/<int:poll_id>/', views.polls_edit, name='edit'),
     path('delete/<int:poll_id>/', views.polls_delete, name='delete_poll'),
     path('end/<int:poll_id>/', views.endpoll, name='end_poll'),
     path('edit/<int:poll_id>/choice/add/', views.add_choice, name='add_choice'),
     path('edit/choice/<int:choice_id>/', views.choice_edit, name='choice_edit'),
     path('delete/choice/<int:choice_id>/', views.choice_delete, name='choice_delete'),
     path('<int:poll_id>/', views.poll_detail, name='detail'),
     path('<int:poll_id>/vote/', views.poll_vote, name='vote'),
]
