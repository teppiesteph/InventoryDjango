from django.urls import path
from inventory import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Landing page
    path('', views.landing_page, name='landing'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='inventory/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),  # Ensure logout redirects to login page
    path('signup/', views.signup, name='signup'),
    
    # Static pages
    path('about/', views.about_page, name='about'),  # About Us page
    path('contact/', views.contact_page, name='contact'),  # Contact page
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Product management
    path('add_product/', views.add_product, name='add_product'),
    path('remove_product/', views.remove_product, name='remove_product'),
    path('view_products/', views.view_products, name='view_products'),
    path('search/', views.search_products, name='search_products'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path("upload_inventory/", views.upload_inventory, name="upload_inventory"),
    path("undo_last_action/", views.undo_last_action, name="undo_last_action"),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
