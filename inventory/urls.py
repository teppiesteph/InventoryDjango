from django.urls import path
from inventory import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('login/', auth_views.LoginView.as_view(template_name='inventory/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_product/', views.add_product, name='add_product'),
    path('remove_product/', views.remove_product, name='remove_product'),
    path('view_products/', views.view_products, name='view_products'),
    path('search/', views.search_products, name='search_products'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
