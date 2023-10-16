from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import *
# from ecomerce.settings import DATE_TIME_FORMATS
# from ecomerce import settings
from django.utils import timezone
import uuid
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from .managers import CustomUserManager
# from .signals import*
class CustomUser(AbstractBaseUser, PermissionsMixin):
        # These fields tie to the roles!
    ADMIN = 1
    DELIVERY = 2
    EMPLOYEE = 3
    CUSTOMER = 4

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (DELIVERY, 'Delivery'),
        (CUSTOMER, 'Customer'),
        (EMPLOYEE, 'Employee')
    )

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
    uid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4, verbose_name='Public identifier')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    otp = models.CharField(max_length=6, default=000000)
    role = models.PositiveIntegerField(choices=ROLE_CHOICES)
    is_staff = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_by = models.EmailField()
    modified_by = models.EmailField()

    
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
    profile=models.ImageField(upload_to='uploads/', null=True, blank=True)
    description=models.TextField(null=True)
    mobile = models.BigIntegerField(unique=True, validators=[
            MaxValueValidator(9999999999),
            MinValueValidator(1000000000)
        ])
    email=models.EmailField(max_length=250)
    vat=models.CharField(max_length=255)
    gstin=models.CharField(max_length=255)


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
    varient_quantity = models.PositiveIntegerField(default=0)

class ProductMedia(models.Model):
    media_content=models.FileField(upload_to='uploads/')


class Products(models.Model):
    subcategories_id=models.ForeignKey(SubCategories,on_delete=models.CASCADE)
    variant=models.ForeignKey(ProductVariant,on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default=" ")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_type = models.CharField(max_length=200, choices=[
        ('percentage', 'Percentage'),
        ('amount', 'Amount'),
    ], default='amount')
    discount=models.DecimalField(max_digits=10, decimal_places=2, null = True)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='uploads/', null=True, blank=True)
    product_media= models.ManyToManyField(ProductMedia, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    stock = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.name


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
    review_image=models.FileField()
    rating=models.FloatField(validators=[
            MaxValueValidator(5.0),
            MinValueValidator(0.5)
        ],)
    review=models.TextField(default="")
    created_at=models.DateTimeField(auto_now_add=True)
    
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    items = models.ManyToManyField(Products, through='CartItem')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    products = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class OrderItem(models.Model):
    products = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order_items = models.ManyToManyField(OrderItem)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

class CancelOrder(models.Model):
    order_id = models.PositiveSmallIntegerField()
    is_cancelled = models.BooleanField(default=True)
    reason = models.CharField(max_length=100, choices=[
        (1, 'The price of the product has fallen due to sales/discounts.'),
        (2, 'Cheaper alternative available for lesser price.'),
        (3, 'Order delivered time is too much'),
        (4, 'others')
    ])
    others = models.TextField(null=True)

class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=[
        ('cod', 'Cash On Delivery'),
        ('digital payment', 'Digital Payment'),
    ])
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    Transaction_id = models.CharField(max_length=30, unique=True, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Payment for Order {self.order} - {self.user.first_name} - {self.amount}"
from .signals import*

class Banner(models.Model):
    title = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='banners/')
    link = models.CharField(max_length=200, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='wishlist')
