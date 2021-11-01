from django.contrib import admin

from .models import  Cart,CartProduct, Hotel, Items, Review,Order

# Register your models here.
admin.site.register([Hotel,Items,Review,Cart, CartProduct,Order,])