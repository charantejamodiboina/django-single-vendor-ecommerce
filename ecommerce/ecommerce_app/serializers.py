from rest_framework import serializers
from .models import*
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'password', 'role')
    
    def create(self, validated_data):
        auth_user = CustomUser.objects.create_user(**validated_data) # type: ignore
        return auth_user

class VerifyAccountSerializer(serializers.Serializer):
    class Meta:
        email = models.EmailField()
        otp = models.CharField(max_length=6)

class SubscriptionSerializer(serializers.Serializer):
    class Meta:
        model = Subscription
        fields = '__all__'
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    last_login = serializers.DateTimeField(default=timezone.now, format='%Y-%m-%d %H:%M:%S %Z')

class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = '__all__'

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
        
class ResetPasswordSerializer(serializers.Serializer):
    class Meta:
        model = CustomUser
        email = serializers.EmailField()
        otp = models.CharField(max_length=6)
        new_password = serializers.CharField(max_length=20, write_only=True)
        confirm_new_password = serializers.CharField(max_length=20, write_only=True)

        def create(self, validated_data):
            auth_user = CustomUser.objects.create_user(**validated_data)
            return auth_user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
    

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = "__all__"

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"
   
    
class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = "__all__"
    

class SubCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategories
        fields = "__all__"

class SubCategoriesViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategories
        fields = "__all__"
    category=CategoriesSerializer()

class VariantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = "__all__"

class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = "__all__"
    
class ProductsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = "__all__"
    subcategories_id=SubCategoriesViewSerializer()
    variant=VariantsSerializer()

class CustProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields =('id', 'name', 'image', 'price')
    

class ProductQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductQuestions
        fields = "__all__"

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAnswer
        fields = "__all__"

class ProductReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReviews
        fields = "__all__"
    
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"

class CartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = "__all__"
    

class CartItemViewSerializer(serializers.ModelSerializer):
    product=CustProductSerializer()
    class Meta:
        model = CartItem
        fields = ('product', 'quantity')
    
class CartViewSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = "__all__"
    def get_items(self, obj):
        cart_items = obj.cartitem_set.all()
        return CartItemViewSerializer(cart_items, many=True).data
class OrderItemsSerializer(serializers.ModelSerializer):
    product=CustProductSerializer()
    class Meta:
        model = OrderItems
        fields = ('product',)
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

class OrderViewSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = "__all__"
    def get_items(self, obj):
        order_items = obj.orderitems_set.all()
        return OrderItemsSerializer(order_items, many=True).data

class StatusSerializer(serializers.ModelSerializer):
    
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled')
    ])
    class Meta:
        model = Order
        fields = ('status', )
class OrderCanceledSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancelOrder
        fields = "__all__"

# class PaymentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Payment
#         fields = "__all__"

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"
class CustomProductField(serializers.RelatedField):
    def to_representation(self, value):
        product_serializer = ProductsSerializer(value)
        return (product_serializer.data)
class CustomUserField(serializers.RelatedField):
    def to_representation(self, value):
        user_serializer = UserListSerializer(value)
        return (user_serializer.data)
class WishlistItemsSerializer(serializers.ModelSerializer):
    product=CustProductSerializer()
    class Meta:

        model = WishlistItem
        fields = ('id', 'product',)
class GetWishlistSerializer(serializers.ModelSerializer):
    items=serializers.SerializerMethodField()
    class Meta:

        model = WishList
        fields = "__all__"
    def get_items(self, obj):
        wishlist_item = obj.wishlistitem_set.all()
        return WishlistItemsSerializer(wishlist_item, many=True).data
class CreateWishlistSerializer(serializers.ModelSerializer):
    class Meta:

        model = WishList
        fields = "__all__"
    user = serializers.PrimaryKeyRelatedField(read_only=True)

class RazorpaySerializer(serializers.ModelSerializer):
    class Meta:
        model=Razorpay
        fields="__all__"

class ChangeOrderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=('address')

class TwilioSerializer(serializers.ModelSerializer):
    class Meta:
        model=Twilio
        fields="__all__"

class Msg91Serializer(serializers.ModelSerializer):
    class Meta:
        model=Msg91
        Fields="__all__"

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Content
        Fields="__all__"

class InstaMOJOSerializer(serializers.ModelSerializer):
    class Meta:
        model=InstaMOJO
        Fields="__all__"

class PayTMSerializer(serializers.ModelSerializer):
    class Meta:
        model=PayTM
        Fields="__all__"