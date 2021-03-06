from django.shortcuts import render
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
import razorpay
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

# Create your views here.

class RegisterView(APIView):
    def post(self, request):
        serializers = Userserializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response({"error": False})
        return Response({"error": True})

class HotelsView(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication,]
    def get(self, request):
        query = Hotel.objects.all()
        serializer = HotelSerializer(query,many = True)
        return Response(serializer.data)




class ItemsView(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication,]
    def get(self, request):
        query = Items.objects.all()
        serializer = ItemSerializer(query,many = True)
        data= []
        for item in serializer.data:
            review_query = Review.objects.filter(item = item['id'])
            review_serializer = ReviewSerializer(review_query,many = True) 
            item['review'] = review_serializer.data
            data.append(item)
        return Response(serializer.data)

class CartView(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def get(self, request):
        user = request.user
        cart_obj = Cart.objects.filter(user=user).filter(isComplete=False).filter(multipleorder = True)
        data = []
        cart_serializer = CartSerializers(cart_obj, many=True)
        for cart in cart_serializer.data:
            cart_product_obj = CartProduct.objects.filter(cart=cart["id"])
            cart_product_obj_serializer = CartProductSerializers(
                    cart_product_obj, many=True)
            cart['cartproducts'] = cart_product_obj_serializer.data
            data.append(cart)
         
        return Response(data)

class SingleCartView(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def get(self, request):
        user = request.user
        cart_obj = Cart.objects.filter(user=user).filter(isComplete=False).filter(multipleorder = False)
        data = []
        cart_serializer = CartSerializers(cart_obj, many=True)
        for cart in cart_serializer.data:
            cart_product_obj = CartProduct.objects.filter(cart=cart["id"])
            cart_product_obj_serializer = CartProductSerializers(
                    cart_product_obj, many=True)
            cart['cartproducts'] = cart_product_obj_serializer.data
            data.append(cart)
         
        return Response(data)

class CartOrderProceed(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]
    def post(sefl, request):
        cart = Cart.objects.filter(
                    user=request.user).filter(isComplete=False).filter(multipleorder = True).first()
        amount = cart.total*100
        client = razorpay.Client(auth=('rzp_test_fJf3Pkpq69Ienb', 'kK34CoQC3ivwvkDDVVEbS7Da'))
        response_payment = client.order.create(dict(amount=amount,
                                                    currency='INR')
                                               )
        order_id = response_payment['id']
        print(order_id)
        order_status = response_payment['status']
        if order_status == 'created':
            cart.order_id = order_id
            cart.save()
        print(order_id)



class SinglerOrder(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]
    def post(sefl, request):
        product_id = request.data['id']
        product_size=request.data['size']
        product_qty= request.data['qty']
        product_obj = Items.objects.get(id=product_id)
        if product_size == 'full':
            itemprice= product_obj.itemprice
        if product_size == 'half':
            itemprice= product_obj.halfprice
        if product_size == 'quarter':
            itemprice= product_obj.quarterprice
        # print(product_obj, "product_obj")
        print("NEW CART CREATED")
        Cart.objects.create(user=request.user,
                                    total=0, isComplete=False,multipleorder = False)
        new_cart = Cart.objects.filter(
                    user=request.user).filter(isComplete=False).filter(multipleorder = False).first()
        amount = product_qty*itemprice*100
        client = razorpay.Client(auth=('rzp_test_fJf3Pkpq69Ienb', 'kK34CoQC3ivwvkDDVVEbS7Da'))
        response_payment = client.order.create(dict(amount=amount,
                                                    currency='INR')
                                               )
        order_id = response_payment['id']
        print(order_id)
        order_status = response_payment['status']
        if order_status == 'created':
            new_cart.order_id = order_id
            print(order_id)
        cart_product_new = CartProduct.objects.create(
                    cart=new_cart,
                    price=product_qty*itemprice,
                    quantity=product_qty,
                    hotel= product_obj.hotel,
                    size= product_size,
                    subtotal=itemprice*product_qty,
                    hotelname = product_obj.hotel.hotelname,
                    cartitemname = product_obj.itemname,
                    hotellocation = product_obj.hotel.hotelloc,
                    itemid = product_id,
                    cartid = new_cart.id,
                )
        
        cart_product_new.product.add(product_obj)
        new_cart.total += itemprice*product_qty
        new_cart.save()
        
        response_msg = {"error": False, "message": "Your Order is Complit"}
        return Response(response_msg)



class AddToCart(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(sefl, request):
        product_id = request.data['id']
        product_size=request.data['size']
        product_qty= request.data['qty']
        product_obj = Items.objects.get(id=product_id)
        if product_size == 'full':
            itemprice= product_obj.itemprice
        if product_size == 'half':
            itemprice= product_obj.halfprice
        if product_size == 'quarter':
            itemprice= product_obj.quarterprice
        # print(product_obj, "product_obj")
        cart_cart = Cart.objects.filter(
            user=request.user).filter(isComplete=False).filter(multipleorder = True).last()
        cart_product_obj = CartProduct.objects.filter(
            product__id=product_id).first()
        
        try:
            if cart_cart:
                print(cart_cart)
                print("OLD CART")
                this_product_in_cart = cart_cart.cartproduct_set.filter(
                    product=product_obj).filter(size= product_size)
                print(this_product_in_cart)
                if this_product_in_cart.exists():
                    print("ADD PRODUCT QTY OLD CART")
                    cartprod_uct = CartProduct.objects.filter(
                        product=product_obj).filter(isComplete=False).filter(cart__multipleorder = True).filter(size= product_size).first()
                    cartprod_uct.quantity += product_qty
                    cartprod_uct.subtotal += itemprice*product_qty
                    cartprod_uct.save()
                    cart_cart.total += itemprice*product_qty
                    cart_cart.save()
                else:
                    print("NEW CART PRODUCT CREATED--OLD CART")
                    cart_product_new = CartProduct.objects.create(
                        cart=cart_cart,
                        price=itemprice,
                        quantity=product_qty,
                        subtotal=itemprice*product_qty,
                        size= product_size,
                        hotel= product_obj.hotel,
                        hotelname = product_obj.hotel.hotelname,
                        cartitemname = product_obj.itemname,
                        hotellocation = product_obj.hotel.hotelloc,
                        itemid = product_id,
                        cartid = cart_cart.id,

                    )
                    cart_product_new.product.add(product_obj)
                    cart_cart.total += itemprice*product_qty
                    cart_cart.save()
            else:
                print("NEW CART CREATED")
                Cart.objects.create(user=request.user,
                                    total=0, isComplete=False)
                new_cart = Cart.objects.filter(
                    user=request.user).filter(isComplete=False).first()
                cart_product_new = CartProduct.objects.create(
                    cart=new_cart,
                    price=itemprice,
                    quantity=product_qty,
                    hotel= product_obj.hotel,
                    size= product_size,
                    subtotal=itemprice*product_qty,
                    hotelname = product_obj.hotel.hotelname,
                    cartitemname = product_obj.itemname,
                    hotellocation = product_obj.hotel.hotelloc,
                    itemid = product_id,
                    cartid = new_cart.id,
                )
                cart_product_new.product.add(product_obj)
                new_cart.total += itemprice*product_qty
                new_cart.save()
            
            response_mesage = {
                'error': False, 'message': "Product add to card successfully", "productid": product_id}
        except:
            response_mesage = {'error': True,
                               'message': "Product Not add!Somthing is Wromg"}
        return Response(response_mesage)

class DeleteCarProduct(APIView):
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        cart_product_id = request.data['id']
        try:
            cart_product_obj = CartProduct.objects.get(id=cart_product_id)
            cart_cart = Cart.objects.filter(
                user=request.user).filter(isComplete=False).filter(multipleorder = True).last()
            cart_cart.total -= cart_product_obj.subtotal
            cart_product_obj.delete()
            cart_cart.save()
            response_msg = {'error': False}
        except:
            response_msg = {'error': True}
        return Response(response_msg)


class AllOrderView(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def get(self, request):
        try:
            query = Order.objects.filter(cart__user=request.user)
            serializers = OrdersSerializers(query, many=True)
            data = []
            for item in serializers.data:
                print('ooooo')
                print(item['cart']['id'])
                print('ooooo')
                cart_product_obj = CartProduct.objects.filter(cartid=item['cart']['id'])
                cart_product_obj_serializer = CartProductSerializers(
                    cart_product_obj, many=True)
                item['orderitems'] = cart_product_obj_serializer.data
                data.append(item)
        except:
            response_msg = {"error": True, "data": "no data"}
        return Response(data)

class CartOrderCreate(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(self, request):
        try:
            data = request.data
            house = data['house']
            name = data['name']
            street = data['street']
            phone = data['phone']
            town = data['town']
            state = data['state']
            paymentmethod = data['paymentmethod']
            cart_obj = Cart.objects.filter(isComplete = False).filter(multipleorder = True).last()
            if paymentmethod == 'COD':
                cart_obj.isComplete = True
            cart_obj.save()
            print(cart_obj.id)
            print('order')
            Order.objects.create(
                cart=cart_obj,
                paymentmethod=paymentmethod,
                house=house,
                name=name,
                phone=phone,
                town=town,
                street=street,
                state=state,
            )
            # try adding user, orderitems here(inside order)
            
            response_msg = {"error": False, "message": "Your Order is Complit"}
        except:
            response_msg = {"error": True, "message": "Somthing is Wrong !"}
        return Response(response_msg)
class SingleOrderCreate(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(self, request):
        try:
            data = request.data
            house = data['house']
            name = data['name']
            street = data['street']
            phone = data['phone']
            town = data['town']
            state = data['state']
            paymentmethod = data['paymentmethod']
            print('acess')
            cart_obj = Cart.objects.filter(user = request.user).filter(isComplete = False).filter(multipleorder = False).first()
            print('success')
            if paymentmethod == 'COD':
                cart_obj.isComplete = True
            cart_obj.save()
            print(cart_obj.id)
            print('single order')
            Order.objects.create(
                cart=cart_obj,
                paymentmethod=paymentmethod,
                house=house,
                name=name,
                phone=phone,
                town=town,
                street=street,
                state=state,
            )
            print('address')
            # try adding user, orderitems here(inside order)

            
            
            response_msg = {"error": False, "message": "Your Order is processing"}
        except:
            response_msg = {"error": True, "message": "Somthing is Wrong !"}
        return Response(response_msg)


class OrderedItemsView(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def get(self, request):
        user = request.user
        cart_obj = Cart.objects.filter(user=user).filter(isComplete=True)
        data = []
        cart_serializer = CartSerializers(cart_obj, many=True)
        for cart in cart_serializer.data:
            cart_product_obj = CartProduct.objects.filter(cart=cart["id"])
            cart_product_obj_serializer = CartProductSerializers(
                    cart_product_obj, many=True)
            cart['cartproducts'] = cart_product_obj_serializer.data
            data.append(cart)
         
        return Response(data)


class DeleteSingleCart(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(self, request):
        try:
            cart_obj = Cart.objects.filter(user=request.user).filter(multipleorder = False).filter(isComplete = False).all()
            cart_obj.delete()
            response_msg = {'error': False}
        except:
            response_msg = {'error': True}
        return Response(response_msg)


class OrderPay(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(self, request):
        print('first')
        data = request.data
        params_dict = {
        'razorpay_order_id': data['razorpay_order_id'],
        'razorpay_payment_id': data['razorpay_payment_id'],
        'razorpay_signature': data['razorpay_signature']
    }
        print('orderpay')

    # client instance
        client = razorpay.Client(auth=('rzp_test_fJf3Pkpq69Ienb', 'kK34CoQC3ivwvkDDVVEbS7Da'))

        try:
            print('orderpayyyyy')
            status = client.utility.verify_payment_signature(params_dict)
            print(status)
            order = Cart.objects.get(order_id=data['razorpay_order_id'])
            print('cart called')
            order.razorpay_payment_id = data['razorpay_payment_id']
            print(order.razorpay_payment_id)
            order.isComplete = True
            order.paid = True
            order.save()
            print('order success')
            response_msg = {"error": False, "message": "Your Order is Complit"}
        except:
            response_msg = {"error": True, "message": "Something went wrong"}
            
        return Response(response_msg)

class CancelOrder(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(self, request):
        data = request.data
        order_id = data['order_id']
        id = data['id']
        print('11')
        try:
            cart = Cart.objects.get(order_id = order_id)
            print('cart')
            print('order first')
            if cart.isComplete == True and cart.user== request.user:
                print(cart.id)
                print('id')
                print(cart.order_id)
                order = Order.objects.get(id = id)
             
                if order.paymentmethod == 'COD':
                    print('cod first')
                    if order.order_status == 'ORDER COMPLETE' or order.order_status == 'ORDER RECIEVED':
                        print('cancel check')
                        order.order_status = 'CANCELLED'
                        print('cacelled')
                        order.save()
                        response_msg = {"error": False, "message": "Order cancelled"}
                if order.paymentmethod == 'ONLINE':
                    print('online first')
                    if order.order_status == 'ORDER COMPLETE' or order.order_status == 'ORDER RECIEVED':
                        print('cancel check')
                        order.order_status = 'CANCELLED'
                        print('cacelled')
                        cart.order_cancel_status = 'REFUNDING'
                        print('save')
                        order.save()
                        print(cart.order_cancel_status)
                        cart.save()
                        print(cart)
                        print('cart status')
                        response_msg = {"error": False, "message": "Order cancelled"}

        except:
            response_msg = {"error": True, "message": "Cannot Cancel"}
            
        return Response(response_msg)