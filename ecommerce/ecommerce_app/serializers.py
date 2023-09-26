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
        auth_user = CustomUser.objects.create_user(**validated_data)
        return auth_user

class VerifyAccountSerializer(serializers.Serializer):
    class Meta:
        
        
        email = models.EmailField()
        otp = models.CharField(max_length=6)

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
    display_pic = serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = "__all__"
    def get_display_pic(self, obj):
        # Define image URLs based on gender
        if obj.gender == 1:
            return 'default_male_profile.jpg'
        elif obj.gender == 2:
            return 'default_female_profile.jpg'
        else:
            return 'default.jpg'

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = "__all__"

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = "__all__"
    profile = serializers.ImageField(
            default=settings.MEDIA_URL + 'default_image.jpg',
            required=False  # Make the field optional
        )
    
class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = "__all__"
    thumbnail = serializers.ImageField(
            default=settings.MEDIA_URL + 'default_image.jpg',
            required=False  # Make the field optional
        )

class SubCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategories
        fields = "__all__"
    thumbnail = serializers.ImageField(
            default=settings.MEDIA_URL + 'default_image.jpg',
            required=False  # Make the field optional
        )

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"
    brand_image = serializers.ImageField(
            default=settings.MEDIA_URL + 'default_image.jpg',
            required=False  # Make the field optional
        )
    
class VarientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = "__all__"

class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = "__all__"
    image = serializers.ImageField(
            default=settings.MEDIA_URL + 'default_image.jpg',
            required=False  # Make the field optional
        )
    # def to_representation(self, instance):
    #     rep = super(ProductsSerializer, self).to_representation(instance)
    #     rep['subcategories_id'] = {instance.subcategories_id.id, instance.subcategories_id.title, instance.subcategories_id.description}
    #     rep['brand'] = instance.brand.brand_name
    #     rep['variant'] = instance.variant.variant_name
    #     return rep
    
class ProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        fields = "__all__"

class ProductTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTransaction
        fields = "__all__"

class ProductDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDetails
        fields = "__all__"

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

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"