from django.urls import path
from .views import *
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
path('login/', obtain_auth_token),
path('register/', RegisterView.as_view()),
 path('hotels/',HotelsView.as_view()),  
 path('item/',ItemsView.as_view()),
 path('cart/',CartView.as_view()),
 path('singleview/',SingleCartView.as_view()),
 path('addtocart/', AddToCart.as_view()),
 path('delatecartprooduct/', DeleteCarProduct.as_view()),
 path('order/', AllOrderView.as_view()),
 path('ordernow/', CartOrderCreate.as_view()),
 path('ordereditems/', OrderedItemsView.as_view()),
 path('singleorder/',SinglerOrder.as_view()),
 path('singleordernow/',SingleOrderCreate.as_view()),
 path('deletecart/', DeleteSingleCart.as_view()),
 path('singleorderpay/', OrderPay.as_view()),
 path('cancelorder/',CancelOrder.as_view()),
 path('cartorderproceed/', CartOrderProceed.as_view()),
]