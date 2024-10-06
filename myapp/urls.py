from django.contrib import admin
from django.urls import path, include
from myapp import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login, name='login'),
    path('reg', views.reg, name='reg'),
    path('adminhome', views.adminhome, name='adminhome'),
    path('advocate_home', views.advocate_home, name='advocate_home'),
    path('user_home', views.user_home, name='user_home'),
    path('admclient', views.admclient, name='admclient'),
    path('adCase', views.adCase, name='adCase'),
    path('adAdv', views.adAdv, name='adAdv'),
    path('bookAd', views.bookAd, name='bookAd'),
    path('submit_booking', views.submit_booking, name='submit_booking'),
    path('booking_status', views.booking_status, name='booking_status'),
    path('advocate_schedule/', views.advocate_schedule, name='advocate_schedule'),
    path('update_booking_status/', views.update_booking_status, name='update_booking_status'),

    # Case management URLs
    path('add_case/', views.add_case, name='add_case'),
    path('view_case/<int:case_id>/', views.view_case, name='view_case'),
    path('edit_case/<int:case_id>/', views.edit_case, name='edit_case'),
    path('delete_case/<int:case_id>/', views.delete_case, name='delete_case'),
    path('advocate/<int:advocate_id>/cases/', views.advocate_cases, name='advocate_cases'),
    path('case/<int:case_id>/manage/', views.manage_case, name='manage_case'),
]