from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from .managers import CustomUserManager
from django.db.models.fields import CharField
import random

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
    modified_date = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.first_name+self.last_name

class ShippingAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    address = models.TextField(max_length=500)
    name = models.CharField(max_length=100)
    mobile = models.BigIntegerField(unique=True, validators=[
            MaxValueValidator(9999999999),
            MinValueValidator(1000000000)
        ])
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True)
    sex = models.CharField(max_length =100, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('others', 'Others')])
    mobile = models.BigIntegerField(unique=True, validators=[
            MaxValueValidator(9999999999),
            MinValueValidator(1000000000)
        ])
    display_pic = models.ImageField(upload_to='uploads/', null=True, blank=True)
    # permission_classes = [IsAuthenticated]

class Store(models.Model):
    name=models.CharField(max_length=255)
    description=models.TextField(null=True)
    vat=models.CharField(max_length=255)
    gstin=models.CharField(max_length=255)
    contact_no= models.BigIntegerField(unique=True, validators=[
            MaxValueValidator(9999999999),
            MinValueValidator(1000000000)
        ])
    email =models.EmailField(max_length=250)
    address = models.TextField(max_length = 500)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    ZIP = models.CharField(max_length=100)
    country_name = models.CharField(max_length=100)
    allow_radius = models.IntegerField()
    delivery_charge = models.FloatField()
    tax_charge = models.FloatField()
    delivery_type = models.CharField(max_length=100, choices=[
        ('fixed', 'Fixed'),
        ('km', 'KM')
    ])
    search_result_kind =models.CharField(max_length=100, choices=[
        ('km', 'KM'),
        ('miles', 'Miles')
    ])
    currency_symbol= models.CharField(max_length=100)
    currency_side =models.CharField(max_length=100, choices=[
        ('left', 'Left'),
        ('right', 'Right')
    ])
    currency_code = models.CharField(max_length=100)
    app_direction = models.CharField(max_length=100, choices=[
        ('ltr', 'LTR'),
        ('rtl', 'RTL')
    ])
    SMS_gateway = models.CharField(max_length=100, choices=[
        ('twilio', 'Twilio'),
        ('msg91', 'MSG91'),
        ('firebase', 'Firebase')
    ])
    user_login= models.CharField(max_length=100, choices=[
        ('email & password', 'Email & Password'),
        ('phone & password', 'Phone & Password'),
        ('phone & OTP', 'Phone & OTP')
    ])
    user_verify_with= models.CharField(max_length=100, choices=[
        ('email verification', 'Email verification'),
        ('phone verification', 'Phone verification')
    ])
    app_color = models.CharField(max_length=100)
    app_status = models.CharField(max_length=100, choices=[
        ('active', 'Active'),
        ('deactive', 'Deactive')
    ])
    default_country_code_without_plus=models.IntegerField()
    FCM_token=models.TextField(max_length=1000)
    logo= models.ImageField(upload_to='uploads/', null=True, blank=True)
    facebook_URL=models.CharField(max_length=100)
    instagram_URL= models.CharField(max_length=100)
    twitter= models.CharField(max_length=100, null=True)
    returns_accepted=models.BooleanField(default=False)
    app_store=models.CharField(max_length=100, null=True)
    play_store=models.CharField(max_length=100, null=True)



    @classmethod
    def get_instance(cls):
        # This method retrieves the instance of the Store model.
        # If no instance exists, it creates one with default values.
        instance, created = cls.objects.get_or_create(pk=1)
        if created:
            instance.save()
        return instance

    def save(self, *args, **kwargs):
        # Override the save method to ensure only one instance exists.
        self.pk = 1
        super().save(*args, **kwargs)

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
    modified_at=models.DateTimeField(auto_now=True)
    
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
    ])
    discount=models.FloatField()
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
    stock = models.SmallIntegerField()

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
    product_id=models.ForeignKey(Products,on_delete=models.CASCADE, related_name='product_reviews')
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    review_image1=models.FileField(null=True)
    review_image2=models.FileField(null=True)
    review_image3=models.FileField(null=True)
    review_image4=models.FileField(null=True)
    review_image5=models.FileField(null=True)
    rating=models.FloatField(validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
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
    order_id = models.CharField(max_length=20, unique=True, null=True)
    user = models.ForeignKey(CustomUser, null=False, on_delete=models.CASCADE)
    items = models.ManyToManyField(Products, through='OrderItems')
    price = models.FloatField()
    gst = models.FloatField()
    delivery_charge = models.FloatField()
    total_price = models.FloatField()
    address = models.ForeignKey(ShippingAddress, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('order placed', 'Order placed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled')
    ], default='order placed')
    created_at = models.DateTimeField(auto_now_add=True)
    def generate_order_id(self):
        self.order_id = 'ODID'+str(random.randint(1000000000, 9999999999))
        self.save()
    def address_options(self):
        return self.user.shippingaddress_set.all()  # Query all addresses for the user
    
    @property
    def selected_address(self):
        return self.address

    @selected_address.setter
    def selected_address(self, address_id):
        self.address = ShippingAddress.objects.get(id=address_id)
    # def update_price(self):
    #     # Calculate the total_price based on associated Cart
    #     self.price = self.cart.total_price
    #     self.save()
    # def update_gst_and_delivery_charge(self):
    #     store = Store.get_instance()
    #     self.gst = store.tax_charge
    #     self.delivery_charge = store.delivery_charge
    # def update_total_price(self):
    #     self.total_price = self.gst or 0+self.delivery_charge or 0+self.price
    #     self.save()

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

class Payment(models.Model):
    order=models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_title= models.CharField(max_length=50)
    payment_response= models.TextField(max_length=3000)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('success', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending', blank=False, null=False)
    
class Razorpay(models.Model):
    currency_code = models.CharField(max_length=100, default="INR")
    RAZORPAY_KEY = models.CharField(max_length=1000)
    RAZORPAY_SECRET = models.CharField(max_length=1000)
    @classmethod
    def get_instance(cls):
        # This method retrieves the instance of the Store model.
        # If no instance exists, it creates one with default values.
        instance, created = cls.objects.get_or_create(pk=1)
        if created:
            instance.save()
        return instance

    def save(self, *args, **kwargs):
        # Override the save method to ensure only one instance exists.
        self.pk = 1
        super().save(*args, **kwargs)


class Banner(models.Model):
    title = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='uploads/')
    link = models.CharField(max_length=200, null=True)
    is_active = models.BooleanField(default=True)
    product=models.ForeignKey(Products, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class WishList(models.Model):
    user = models.ForeignKey(CustomUser, null=False, on_delete=models.CASCADE)
    items = models.ManyToManyField(Products, through='WishlistItem')

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(WishList, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    
class Twilio(models.Model):
    twilio_SID = models.CharField(max_length=500)
    twilio_auth_token = models.CharField(max_length=500)
    twilio_from_number = models.CharField(max_length=500)
    @classmethod
    def get_instance(cls):
        # This method retrieves the instance of the Store model.
        # If no instance exists, it creates one with default values.
        instance, created = cls.objects.get_or_create(pk=1)
        if created:
            instance.save()
        return instance

    def save(self, *args, **kwargs):
        # Override the save method to ensure only one instance exists.
        self.pk = 1
        super().save(*args, **kwargs)

class Msg91(models.Model):
    msg91_auth_key=models.CharField(max_length=500)
    msg91_sender_id=models.CharField(max_length=500)
    @classmethod
    def get_instance(cls):
        # This method retrieves the instance of the Store model.
        # If no instance exists, it creates one with default values.
        instance, created = cls.objects.get_or_create(pk=1)
        if created:
            instance.save()
        return instance

    def save(self, *args, **kwargs):
        # Override the save method to ensure only one instance exists.
        self.pk = 1
        super().save(*args, **kwargs)

class Stripe(models.Model):
    currency_code=models.CharField(max_length=500)
    stripe_key=models.CharField(max_length=500)
    stripe_secret=models.CharField(max_length=500)
    @classmethod
    def get_instance(cls):
        # This method retrieves the instance of the Store model.
        # If no instance exists, it creates one with default values.
        instance, created = cls.objects.get_or_create(pk=1)
        if created:
            instance.save()
        return instance

    def save(self, *args, **kwargs):
        # Override the save method to ensure only one instance exists.
        self.pk = 1
        super().save(*args, **kwargs)

class Paypal(models.Model):
    currency_code=models.CharField(max_length=500)
    paypal_client_key=models.CharField(max_length=500)
    paypal_client_secret=models.CharField(max_length=500)
    @classmethod
    def get_instance(cls):
        # This method retrieves the instance of the Store model.
        # If no instance exists, it creates one with default values.
        instance, created = cls.objects.get_or_create(pk=1)
        if created:
            instance.save()
        return instance

    def save(self, *args, **kwargs):
        # Override the save method to ensure only one instance exists.
        self.pk = 1
        super().save(*args, **kwargs)

class PayTM(models.Model):
    currency_code=models.CharField(max_length=500)
    paytm_environment=models.CharField(max_length=500)
    paytm_merchant_key=models.CharField(max_length=500)
    paytm_merchant_MID=models.CharField(max_length=500)
    paytm_merchant_website=models.CharField(max_length=500)
    @classmethod
    def get_instance(cls):
        # This method retrieves the instance of the Store model.
        # If no instance exists, it creates one with default values.
        instance, created = cls.objects.get_or_create(pk=1)
        if created:
            instance.save()
        return instance

    def save(self, *args, **kwargs):
        # Override the save method to ensure only one instance exists.
        self.pk = 1
        super().save(*args, **kwargs)

class InstaMOJO(models.Model):
    currency_code=models.CharField(max_length=500)
    instamojo_environment=models.CharField(max_length=500)
    instamojo_key=models.CharField(max_length=500)
    instamojo_token=models.CharField(max_length=500)
    @classmethod
    def get_instance(cls):
        # This method retrieves the instance of the Store model.
        # If no instance exists, it creates one with default values.
        instance, created = cls.objects.get_or_create(pk=1)
        if created:
            instance.save()
        return instance

    def save(self, *args, **kwargs):
        # Override the save method to ensure only one instance exists.
        self.pk = 1
        super().save(*args, **kwargs)

class PayStack(models.Model):
    currency_code=models.CharField(max_length=500)
    paystack_sk=models.CharField(max_length=500)
    paystack_pk=models.CharField(max_length=500)
    @classmethod
    def get_instance(cls):
        # This method retrieves the instance of the Store model.
        # If no instance exists, it creates one with default values.
        instance, created = cls.objects.get_or_create(pk=1)
        if created:
            instance.save()
        return instance

    def save(self, *args, **kwargs):
        # Override the save method to ensure only one instance exists.
        self.pk = 1
        super().save(*args, **kwargs)

class Flutterwave(models.Model):
    currency_code=models.CharField(max_length=500)
    flutterwave_key=models.CharField(max_length=500)
    flutterwave_secret_key=models.CharField(max_length=500)
    @classmethod
    def get_instance(cls):
        # This method retrieves the instance of the Store model.
        # If no instance exists, it creates one with default values.
        instance, created = cls.objects.get_or_create(pk=1)
        if created:
            instance.save()
        return instance

    def save(self, *args, **kwargs):
        # Override the save method to ensure only one instance exists.
        self.pk = 1
        super().save(*args, **kwargs)

class Content(models.Model):
    free_delivery=models.TextField(max_length=1000)  
    safe_payment=models.TextField(max_length=1000)
    secure_payment=models.TextField(max_length=1000)  
    Back_Guarantee=models.TextField(max_length=1000)
    @classmethod
    def get_instance(cls):
        # This method retrieves the instance of the Store model.
        # If no instance exists, it creates one with default values.
        instance, created = cls.objects.get_or_create(pk=1)
        if created:
            instance.save()
        return instance

    def save(self, *args, **kwargs):
        # Override the save method to ensure only one instance exists.
        self.pk = 1
        super().save(*args, **kwargs)

class Page(models.Model):
    page_name=models.CharField(max_length=500)
    page_image=models.FileField(upload_to='uploads/', null=True, blank=True)
    Page_content=models.TextField(max_length=10000)

class DeliveryProfile(models.Model):
    deliveryman_image=models.ImageField(upload_to='uploads/', null=True, blank=True)
    vehicle=models.CharField(max_length=245)
    identity_type=models.CharField(max_length=245)
    identity_image=models.ImageField(upload_to='uploads/', null=True, blank=True)
    identity_number=models.CharField(max_length=245)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True)

class Delivery(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'delivery'}, related_name='deliveries')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, limit_choices_to={'status': 'order placed'}, related_name='deliveries')
    assigned_datetime = models.DateTimeField(auto_now_add=True)
    delivered_datetime = models.DateTimeField(auto_now=True)
    is_delivered = models.BooleanField(default=False)

    def __str__(self):
        return f"Deliveryman: {self.user.first_name} {self.user.last_name}"