from django.urls import path
from api import views


urlpatterns = [
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('transaction/', views.TransactionView.as_view(), name='transaction'),
]
