from django.urls import path, include
from .views import*
from ecommerce_app import views
from rest_framework import routers
routers = routers.DefaultRouter()
routers.register('categories', views.CategoriesViewSet, "Categories")
routers.register('subcategories', views.SubCategoriesViewSet, "Sub-categories")
routers.register('brand', views.BrandViewSet, "brand")
routers.register('products', views.ProductsViewSet, "Products")
routers.register('variant', views.VarientsViewSet, "Product Varients")
routers.register('product/media', views.ProductMediaViewSet, "Product Media")
routers.register('product/details', views.ProductDetailsViewSet, "Product Details")
routers.register('questions', views.ProductQuestionsViewSet, "Product Questions")
routers.register('reviews', views.ProductReviewsViewSet, "Product Reviews")
routers.register('transactions', views.ProductTransactionViewSet, "Product Transactions")
routers.register('answers', views.AnswerViewSet, "answers for product questions")
routers.register('cart', views.CartViewSet, "Cart")
routers.register('order',views.OrderViewSet , "Order")
routers.register('payment',views.PaymentViewSet , "Payment")
routers.register('address',views.AddressViewSet , "Address")
routers.register('inventory',views.InventoryViewSet , "Inventory")

urlpatterns = [
    path('', include(routers.urls)),
    path('register', UserRegistrationView.as_view(), name='User Registration'),
    path('verify', VerifyOtp.as_view(), name='Email Verification'),
    path('login', UserLoginView.as_view(), name='User login'),
    path('list', UserListView.as_view(), name='Users'),
    path('forgot/password', ForgotPasswordView.as_view(), name='Forgot Password'),
    path('reset/password', ResetPasswordView.as_view(), name='Reset Password'),
    path('delete/<int:pk>/', DeleteAccountView.as_view(), name='delete account'),
    path('profile', CreateUserProfile.as_view(), name='profile create'),
    path('profile/<int:pk>/', UpdateUserProfile.as_view(), name='profile update'),
    path('cartitems', CartItemListView.as_view(), name='profile update'),
    path('cartitems/<int:pk>/', CartItemDetailView.as_view(), name='profile update'),
    path('orderitems', OrderItemListView.as_view(), name='profile update'),
    path('orderitems/<int:pk>/', OrderItemDetailView.as_view(), name='profile update'),
]