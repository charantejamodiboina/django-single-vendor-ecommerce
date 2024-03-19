from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import *
# from ecomerce.settings import DATE_TIME_FORMATS
# from ecomerce import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from .managers import CustomUserManager
from django.db.models.fields import CharField
# from .signals import*

class Subscription(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_subscribed = models.BooleanField(default=True)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
    uid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4, verbose_name='Public identifier')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    otp = models.CharField(max_length=6, default=000000)
    role = models.CharField(max_length =100, choices=[
        ('admin', 'Admin'),
        ('store admin', 'Store Admin'),
        ('delivery', 'Delivery'),
        ('customer', 'Customer'),
        ('employe', 'Employee')], default= 'customer')
    is_staff = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.first_name+self.last_name

class ShippingAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    address = models.TextField(max_length=500)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

class UserProfile(models.Model):

    MALE = 1
    FEMALE = 2
    OTHERS = 3

    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHERS, 'Others')
    )
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True)
    gender = models.PositiveSmallIntegerField(choices=GENDER_CHOICES)
    mobile = models.BigIntegerField(unique=True, validators=[
            MaxValueValidator(9999999999),
            MinValueValidator(1000000000)
        ])
    display_pic = models.ImageField(upload_to='uploads/', null=True, blank=True)

class Store(models.Model):
    name=models.CharField(max_length=255)
    description=models.TextField(null=True)
    vat=models.CharField(max_length=255)
    gstin=models.CharField(max_length=255)
    contact_No= models.BigIntegerField(unique=True, validators=[
            MaxValueValidator(9999999999),
            MinValueValidator(1000000000)
        ])
    email_ID =models.EmailField(max_length=250)
    Address = models.TextField(max_length = 500)
    City = models.CharField(max_length=100)
    State = models.CharField(max_length=100)
    ZIP = models.CharField(max_length=100)
    Country_Name = models.CharField(max_length=100)
    Allow_Distance = models.IntegerField()
    Default_City =models.CharField(max_length=100)
    Default_ZIP =models.CharField(max_length=100)
    Delivery_Charge = models.FloatField()
    Tax_Charge = models.FloatField()
    Delivery_Type = models.CharField(max_length=100, choices=[
        ('fixed', 'Fixed'),
        ('km', 'KM')
    ])
    Have_Shop= models.CharField(max_length=100, choices=[
        ('yes', 'Yes'),
        ('no', 'No')
    ])
    Search_Result_Kind =models.CharField(max_length=100, choices=[
        ('km', 'KM'),
        ('miles', 'Miles')
    ])
    Search_Radius = models.IntegerField()
    Currency_Symbol= models.CharField(max_length=100)
    Currency_Side =models.CharField(max_length=100, choices=[
        ('left', 'Left'),
        ('right', 'Right')
    ])
    Currency_Code = models.CharField(max_length=100)
    App_Direction = models.CharField(max_length=100, choices=[
        ('ltr', 'LTR'),
        ('rtl', 'RTL')
    ])
    SMS_Gateway = models.CharField(max_length=100, choices=[
        ('twilio', 'Twilio'),
        ('msg91', 'MSG91'),
        ('firebase', 'Firebase')
    ])
    User_Login= models.CharField(max_length=100, choices=[
        ('email & password', 'Email & Password'),
        ('phone & password', 'Phone & Password'),
        ('phone & OTP', 'Phone & OTP')
    ])
    User_Verify_With= models.CharField(max_length=100, choices=[
        ('email verification', 'Email verification'),
        ('phone verification', 'Phone verification')
    ])
    App_Color = models.CharField(max_length=100)
    App_Status = models.CharField(max_length=100, choices=[
        ('email verification', 'Email verification'),
        ('phone verification', 'Phone verification')
    ])
    Default_Country_Code_without_plus_=models.IntegerField()
    Countries=models.CharField(max_length=100)
    FCM_Token=models.TextField(max_length=1000)
    Logo= models.ImageField(upload_to='uploads/', null=True, blank=True)
    Facebook_URL=models.CharField(max_length=100)
    Instagram_URL= models.CharField(max_length=100)


    def __str__(self):
        return self.name
  
class Categories(models.Model):
    name=models.CharField(max_length=255, unique=True)
    thumbnail=models.ImageField(upload_to='uploads/', null=True, blank=True)
    description=models.TextField(null=True)
    created_at=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name

class SubCategories(models.Model):
    category=models.ForeignKey(Categories,on_delete=models.CASCADE)
    name=models.CharField(max_length=255, unique=True)
    thumbnail=models.ImageField(upload_to='uploads/', null=True, blank=True)
    description=models.TextField(null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(default=timezone.now)
    
class ProductVariant(models.Model):
    variant_name = models.CharField(max_length=100, unique=True)


class Products(models.Model):
    subcategories_id=models.ForeignKey(SubCategories,on_delete=models.CASCADE)
    variant=models.ForeignKey(ProductVariant,on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default=" ")
    price = models.FloatField()
    discount_type = models.CharField(max_length=200, choices=[
        ('percentage', 'Percentage'),
        ('amount', 'Amount'),
    ], default='amount')
    discount=models.FloatField(default=0)
    you_save = models.FloatField(default=0)
    final_price = models.FloatField(default=0)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='product_images/', blank=True)
    image2 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    image3 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    image4 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    image5 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    image6 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    video = models.FileField(upload_to='product_video/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    stock = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if self.discount_type == 'percentage':
            self.you_save = (self.price*self.discount)/100     
        elif self.discount_type == 'amount':
            self.you_save = self.discount
        self.final_price = self.price-self.you_save
        super().save(*args, **kwargs)

class ProductQuestions(models.Model):
    product_id=models.ForeignKey(Products,on_delete=models.CASCADE)
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    question=models.CharField(max_length=200, unique=True)
    created_at=models.DateTimeField(auto_now_add=True)

class ProductAnswer(models.Model):
    product_id=models.ForeignKey(Products,on_delete=models.CASCADE)
    question_id = models.ForeignKey(ProductQuestions,on_delete=models.CASCADE)
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    answers=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    

class ProductReviews(models.Model):
    product_id=models.ForeignKey(Products,on_delete=models.CASCADE)
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    review_image1=models.FileField(null=True)
    review_image2=models.FileField(null=True)
    review_image3=models.FileField(null=True)
    review_image4=models.FileField(null=True)
    review_image5=models.FileField(null=True)
    rating=models.FloatField(validators=[
            MaxValueValidator(1),
            MinValueValidator(5)
        ],)
    review=models.TextField(default="")
    created_at=models.DateTimeField(auto_now_add=True)
    
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, null=False, on_delete=models.CASCADE)
    items = models.ManyToManyField(Products, through='CartItem')
    total_price = models.FloatField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    def update_total_price(self):
        # Calculate the total_price based on associated OrderItems
        self.total_price = sum(item.items_price for item in self.cartitem_set.all())
        self.save()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    items_price = models.FloatField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        # Calculate items_price before saving
        self.items_price = self.product.final_price * self.quantity
        super().save(*args, **kwargs)

class Order(models.Model):
    user = models.ForeignKey(CustomUser, null=False, on_delete=models.CASCADE)
    items = models.ManyToManyField(Products, through='OrderItems')
    total_price = models.FloatField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('order placed', 'Order placed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('success', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending', blank=False, null=False)
    provider_order_id = models.CharField(
        _("Order ID"), max_length=40, null=False, blank=False
    )
    payment_id = models.CharField(
        _("Payment ID"), max_length=36, null=False, blank=False
    )
    signature_id = models.CharField(
        _("Signature ID"), max_length=128, null=False, blank=False
    )
    def update_total_price(self):
        # Calculate the total_price based on associated Cart
        self.total_price = self.cart.total_price
        self.save()
class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    items_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
class CancelOrder(models.Model):
    order_id = models.PositiveSmallIntegerField()
    is_cancelled = models.BooleanField(default=True)
    reason = models.CharField(max_length=100, choices=[
        ('Reason1', 'The price of the product has fallen due to sales/discounts.'),
        ('Reason2', 'Cheaper alternative available for lesser price.'),
        ('Reason3', 'Order delivered time is too much'),
        ('Reason4', 'others')
    ])
    others = models.TextField(null=True)

    
class Banner(models.Model):
    title = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='uploads/')
    link = models.CharField(max_length=200, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class WishList(models.Model):
    user = models.ForeignKey(CustomUser, null=False, on_delete=models.CASCADE)
    items = models.ManyToManyField(Products, through='WishlistItem')
    
    

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(WishList, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    
    