
from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('authors/', views.author_list, name='author_list'),  
    path('categories/', views.category_list, name='category_list'), 
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('author/<int:author_id>/', views.author_detail, name='author_detail'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    
    path('add-to-cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('track-order/', views.track_order, name='track_order'),
]

