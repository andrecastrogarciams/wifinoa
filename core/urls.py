from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.PortalIndexView.as_view(), name='portal_index'),
    path('colaborador/', views.LoginColaboradorView.as_view(), name='login_colaborador'),
    path('visitante/', views.LoginVisitanteView.as_view(), name='login_visitante'),
    path('sucesso/', views.SuccessView.as_view(), name='success'),
]
