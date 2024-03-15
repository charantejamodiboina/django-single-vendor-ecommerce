from django.urls import path, include
from .views import*
from ecommerce_app import views
from django.conf.urls.static import static

from rest_framework import routers
routers = routers.DefaultRouter()

routers.register('cancel/order',views.OrderCancelViewSet , "Cancel Order")
# routers.register('payment',views.PaymentViewSet , "Payment")
routers.register('address',views.AddressViewSet , "Address")
routers.register('inventory',views.InventoryViewSet , "Inventory")
routers.register('profile',views.UserProfileViewSet)


urlpatterns = [
    path('', include(routers.urls)),
    # API's for User
    path('register', UserRegistrationView.as_view(), name='User Registration'),
    path('verify', VerifyOtp.as_view(), name='Email Verification'),
    path('login', UserLoginView.as_view(), name='User login'),
    path('list', UserListView.as_view(), name='Users'),
    path('forgot/password', ForgotPasswordView.as_view(), name='Forgot Password'),
    path('reset/password', ResetPasswordView.as_view(), name='Reset Password'),
    path('delete/<int:pk>/', DeleteAccountView.as_view(), name='delete account'),

    # API's for Banners
    path('banner/create', BannerCreateView.as_view(), name='Create Banner'),
    path('banners', BannersView.as_view(), name='Banner List'),
    path('banner/retrieve/<int:pk>/', BannerRetrieveView.as_view(), name='Banner Retrieve By Id'),
    path('banner/update/<int:pk>/', BannerUpdateView.as_view(), name='Update Banner'),

    # API's for Category
    path('category/create', CategoryCreateView.as_view(), name='Create Category'),
    path('categories', CategoriesView.as_view(), name='Categories List'),
    path('category/<int:pk>/', CategoryRetrieveView.as_view(), name='Category Retrieve By Id'),
    path('category/update/<int:pk>/', CategoryUpdateView.as_view(), name='Update Category'),

    # API's for Subcategory
    path('subcategory/create', SubcategoryCreateView.as_view(), name='Create Subcategory'),
    path('subcategories', SubcategoriesView.as_view(), name='Subcategories List'),
    path('subcategory/<int:pk>/', SubcategoryRetrieveView.as_view(), name='Subcategory Retrieve By Id'),
    path('subcategory/update/<int:pk>/', SubcategoryUpdateView.as_view(), name='Update Subcategory'),

    # API's for Products
    path('product/create', ProductsCreateView.as_view(), name='Create Products'),
    path('products', ProductsView.as_view(), name='Products List'),
    path('product/retrieve/<int:pk>/', ProductsRetrieveView.as_view(), name='Products Retrieve By Id'),
    path('product/update/<int:pk>/', ProductsUpdateView.as_view(), name='Update Products'),

    # Product variant APIs
    path('product/variant', VarientsPost.as_view()),
    path('product/variant/list', Varientslist.as_view()),
    path('product/variant/<int:pk>/', VarientsDetails.as_view()),
    path('variant/update/<int:pk>/', VarientUpdateView.as_view()),

    # API's for product questions
    path('product/que', ProductQuestionsCreate.as_view()),
    path('product/que/list', ProductQuestionslist.as_view()),
    path('product/que/<int:pk>/', ProductQuestionsDetails.as_view()),

    # API's for product answers
    path('product/ans', PostAnswer.as_view()),
    path('product/ans/list', Answerslist.as_view()),
    path('product/ans/<int:pk>/', AnswerDetails.as_view()),

    # API's for product reviews
    path('review', CreateProductReview.as_view()),
    path('review/list', ListProductReview.as_view()),
    path('review/<int:pk>/', RetrieveProductReview.as_view()),
    path('product/review/<int:pk>/', ProductReview.as_view()),
    # API's for count
    path('count', Count.as_view(), name='Count'),
    path('user/count', UserCount.as_view(), name='Count By Role based'),

    # wishlist APIs
    path('wishlist', WishListView.as_view(), name='WishList'),

    # cart APIs
    path('cart/', CartView.as_view()),
    path('cartlist/', CartlistView.as_view()),

    # checkout APIs
    path('checkout/', Checkout.as_view(), name='cart-checkout'),
    path('orders/', OrderView.as_view()),
    path('change/status/<int:pk>/', ChangeStatus.as_view()),
    path("razorpay/callback/", RazorpayCallback.as_view(), name="callback"),

    # all excel bulk upload APIs
    path('category/excel/bulk', CategoryBulkUploadView.as_view()),
    path('subcat/excel/bulk', CategoryBulkUploadView.as_view()),
    path('product/excel/bulk', CategoryBulkUploadView.as_view()),
    
    # all json bulk upload APIs
    path('category/bulk', BulkCategoryCreateView.as_view(), name='Create bulk Category'),
    path('subcategory/bulk', BulkSubcategoryCreateView.as_view(), name='Create bulk Subcategory'),
    path('product/bulk', BulkProductsCreateView.as_view(), name='Create Bulk Products'),
    path('variant/bulk/', CreateBulkVariants.as_view()),
    
    # all bulk delete APIs
    path("subcate/bulk/delete/", BulkSubcategoryDelete.as_view()),
    path("cate/bulk/delete/", BulkCategoryDelete.as_view()),
    path("product/bulk/delete/", BulkProductDelete.as_view()),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)