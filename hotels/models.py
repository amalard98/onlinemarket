from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Hotel(models.Model):
    hotelname = models.CharField(max_length=150)
    hotelloc = models.CharField(max_length=150)
    hotelphone = models.IntegerField()
    open = models.BooleanField(default=False)
    logo = models.CharField(max_length=600)
    def __str__(self):
        return self.hotelname

class Items(models.Model):
    available = models.BooleanField(default=False)
    hotel = models.ForeignKey(Hotel,models.CASCADE)
    itemname = models.CharField(max_length=150)
    itemprice = models.PositiveIntegerField()
    itemdesc = models.TextField()
    itemphoto = models.CharField(max_length=550)
    itemrating = models.PositiveIntegerField()
    itemtrending = models.BooleanField(default = False)
    quarter = models.BooleanField(default = False)
    quarterprice = models.PositiveIntegerField(blank=True,null=True)
    half = models.BooleanField(default = False)
    date = models.DateField(auto_now_add=True)
    halfprice = models.PositiveIntegerField(blank=True,null=True)
    def __str__(self):
        return f"{self.itemname}"

class Review(models.Model):
    user = models.ForeignKey(User, models.CASCADE,)
    item = models.ForeignKey(Items,models.CASCADE,)
    review = models.CharField(max_length=200)
    def __str__(self):
        return f"User : {self.user.username} review :{self.review}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.PositiveIntegerField()
    isComplete = models.BooleanField(default=False)
    multipleorder =models.BooleanField(default=True)
    order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    paid = models.BooleanField(default=False)
    order_cancel_status = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return f"User={self.user.username}|ISComplete={self.isComplete}"


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ManyToManyField(Items,)
    price = models.PositiveIntegerField()
    size = models.CharField(max_length=8)
    quantity = models.PositiveIntegerField()
    hotel = models.ForeignKey(Hotel,models.CASCADE)
    subtotal = models.PositiveIntegerField()
    hotelname= models.CharField(max_length=150)
    cartitemname = models.CharField(max_length=200)
    hotellocation = models.CharField(max_length=300)
    itemid = models.CharField(max_length=250)
    cartid = models.CharField(max_length=250)
    order_id = models.CharField(max_length=100, blank=True)
    
    
    def __str__(self):
        return f"Cart=={self.cart.id}<==>CartProduct:{self.id}==Qualtity=={self.quantity}"

class Order(models.Model):
    
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    phone = models.CharField(max_length=13)
    street = models.CharField(max_length=200)
    house = models.CharField(max_length=200)
    town = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    orderdate = models.DateField(auto_now_add=True, blank=True)
    orderTime = models.TimeField(auto_now_add=True, blank=True)
    paymentmethod = models.CharField(max_length=6)
    ORDER_CANCEL = 'CANCEL'
    ORDER_COMPLETED = 'ORDER COMPLETE'
    ORDER_RECEIVED = 'ORDER RECIEVED'
    ORDER_PROCESSING = 'PROCESSING'
    ORDER_PICKEDUP = 'PICKEDUP'
    DELIVERED = 'DELIVERED'
    
    ORDER_STATUS = [
        (ORDER_CANCEL, 'CANCEL'),
        (ORDER_COMPLETED, 'ORDER COMPLETE'),
        (ORDER_RECEIVED, 'ORDER RECIEVED'),
        (ORDER_PROCESSING, 'PROCESSING'),
        (ORDER_PICKEDUP, 'PICKEDUP'),
        (DELIVERED, 'DELIVERED'),
    ]
    order_status = models.CharField(
        max_length=14,
        choices=ORDER_STATUS,
        default=ORDER_COMPLETED,
    )
