from django.urls import path,include
from . import views



appname = "oldbook"

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('addcart/', views.addcart, name='addcart'),
    path('addcartItem/', views.addcartItem, name='addcartItem'),
    
    path('cart_delete/<int:id>', views.cart_delete, name='cart_delete'),

    path('contact/', views.contact, name='contact'),
    path('details/<slug:slug>/', views.details, name='details'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('user_profile/edit_profile/', views.edit_profile, name='edit_profile'),

    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    path('paymentdone/', views.payment_done, name='payment_done'),
    path('payment/', views.payment, name='payment'),
    path('order_success/', views.order_success, name='order_success'),

]
