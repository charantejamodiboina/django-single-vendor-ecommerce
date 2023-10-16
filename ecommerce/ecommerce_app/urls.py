from django.urls import path, include
from .views import*
from ecommerce_app import views
from rest_framework import routers
routers = routers.DefaultRouter()
routers.register('variant', views.VarientsViewSet, "Product Varients")
routers.register('product/media', views.ProductMediaViewSet, "Product Media")
routers.register('questions', views.ProductQuestionsViewSet, "Product Questions")
routers.register('reviews', views.ProductReviewsViewSet, "Product Reviews")
routers.register('answers', views.AnswerViewSet, "answers for product questions")
routers.register('cart', views.CartViewSet, "Cart")
routers.register('order',views.OrderViewSet , "Order")
routers.register('cancel/order',views.OrderCancelViewSet , "Cancel Order")
routers.register('payment',views.PaymentViewSet , "Payment")
routers.register('address',views.AddressViewSet , "Address")
routers.register('inventory',views.InventoryViewSet , "Inventory")


urlpatterns = [
    path('', include(routers.urls)),

    # Api's for User
    path('register', UserRegistrationView.as_view(), name='User Registration'),
    path('verify', VerifyOtp.as_view(), name='Email Verification'),
    path('login', UserLoginView.as_view(), name='User login'),
    path('list', UserListView.as_view(), name='Users'),
    path('forgot/password', ForgotPasswordView.as_view(), name='Forgot Password'),
    path('reset/password', ResetPasswordView.as_view(), name='Reset Password'),
    path('delete/<int:pk>/', DeleteAccountView.as_view(), name='delete account'),

    # Api's for User Profile
    path('profile', CreateUserProfile.as_view(), name='profile create'),
    path('profile/<int:pk>/', UpdateUserProfile.as_view(), name='profile update'),

    # Api's for Banners
    path('banner/create', BannerCreateView.as_view(), name='Create Banner'),
    path('banners', BannersView.as_view(), name='Banner List'),
    path('banner/retrieve/<int:pk>/', BannerRetrieveView.as_view(), name='Banner Retrieve By Id'),
    path('banner/update/<int:pk>/', BannerUpdateView.as_view(), name='Update Banner'),
    path('banner/delete/<int:pk>/', BannerDeleteView.as_view(), name='Delete Banner'),

    # Api's for Category
    path('category/create', CategoryCreateView.as_view(), name='Create Category'),
    path('categories', CategoriesView.as_view(), name='Categories List'),
    path('category/retrieve/<int:pk>/', CategoryRetrieveView.as_view(), name='Category Retrieve By Id'),
    path('category/update/<int:pk>/', CategoryUpdateView.as_view(), name='Update Category'),
    path('category/delete/<int:pk>/', CategoryDeleteView.as_view(), name='Delete Category'),

    # Api's for Subcategory
    path('subcategory/create', SubcategoryCreateView.as_view(), name='Create Subcategory'),
    path('subcategories', SubcategoriesView.as_view(), name='Subcategories List'),
    path('subcategory/retrieve/<int:pk>/', SubcategoryRetrieveView.as_view(), name='Subcategory Retrieve By Id'),
    path('subcategory/update/<int:pk>/', SubcategoryUpdateView.as_view(), name='Update Subcategory'),
    path('subcategory/delete/<int:pk>/', SubcategoryDeleteView.as_view(), name='Delete Subcategory'),

    # Api's for Brand
    path('brand/create', BrandCreateView.as_view(), name='Create Brand'),
    path('brands', BrandView.as_view(), name='Brand List'),
    path('brand/retrieve/<int:pk>/', BrandRetrieveView.as_view(), name='Brand Retrieve By Id'),
    path('brand/update/<int:pk>/', BrandUpdateView.as_view(), name='Update Brand'),
    path('brand/delete/<int:pk>/', BrandDeleteView.as_view(), name='Delete Brand'),

    # Api's for vProducts
    path('product/create', ProductsCreateView.as_view(), name='Create Products'),
    path('products', ProductsView.as_view(), name='Products List'),
    path('product/retrieve/<int:pk>/', ProductsRetrieveView.as_view(), name='Products Retrieve By Id'),
    path('product/update/<int:pk>/', ProductsUpdateView.as_view(), name='Update Products'),
    path('product/delete/<int:pk>/', ProductsDeleteView.as_view(), name='Delete Products'),

    # Api's for CartItem
    path('cart/item/create', CartItemCreateView.as_view(), name='Create CartItem'),
    path('cart/items', CartItemView.as_view(), name='CartItems List'),
    path('cart/item/retrieve/<int:pk>/', CartItemRetrieveView.as_view(), name='CartItem Retrieve By Id'),
    path('cart/item/update/<int:pk>/', CartItemUpdateView.as_view(), name='Update CartItem'),
    path('cart/item/delete/<int:pk>/', CartItemDeleteView.as_view(), name='Delete CartItem'),

    # Api's for OrderItem
    path('orderitems', OrderItemListView.as_view(), name='order items'),
    path('orderitems/<int:pk>/', OrderItemDetailView.as_view(), name='order items update'),

    # Api's for count
    path('count', Count.as_view(), name='Count'),
    path('user/count', UserCount.as_view(), name='Count By Role based'),

    path('wishlist', WishlistView.as_view(), name='WishList'),
    path('wishlist/create/', WishlistCreateView.as_view(), name='Creating wishlist'),
    path('wishlist/<int:pk>/', WishlistCreateView.as_view(), name='Creating wishlist'),
]