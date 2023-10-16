from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import*
from .serializers import*
from .email import*
from django.conf import settings
from django.core.mail import send_mail
import random
from django.http import Http404
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .filters import*
TIME_ZONE ='Asia/Kolkata'
class UserRegistrationView(APIView):
    user=CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny, )
    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        valid = serializers.is_valid(raise_exception = True)
        if valid:
            
            

            serializers.save()
            email_otp(serializers.data['email'])
            
            status_code= status.HTTP_201_CREATED
            response={
                'success': True,
                'status': status_code,
                'message' : 'user successfully created',
                'user': serializers.data
           }
            return Response( response, status=status_code)
    
class VerifyOtp(APIView):
    serializer_class = VerifyAccountSerializer
    permission_classes = (AllowAny,)
    def post(self, request):
        otp = request.data.get('otp')
        email = request.data.get('email')

        if not email or not otp:
            return Response({'error': 'email and otp is required.'}, status=status.HTTP_400_BAD_REQUEST)
        # Get the user and their associated OTP from the database (assuming you have stored it during registration)
        user = CustomUser.objects.get(email=email) 
        if email != user.email:
            return Response({'error': 'Invalid email.'}, status=status.HTTP_400_BAD_REQUEST)
        # Compare the received OTP with the one in the database
        if otp == user.otp:
            user.is_verified = True
            user.save()
            return Response({'message': 'OTP verified successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
            
            
class UserLoginView(TokenObtainPairView):
    serializer_class = UserLoginSerializer
    permission_classes = (AllowAny, )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.all()
        

        if valid:
            email= serializer.validated_data['email']
            password= serializer.validated_data['password']
        
            user = authenticate(email=email, password=password)
            if user is not None:
                if user.is_verified:
                    login(request, user)
                    refresh = RefreshToken.for_user(user)
                    refresh_token = str(refresh)
                    access_token = str(refresh.access_token)

                    update_last_login(None, user)
                    status_code = status.HTTP_200_OK
                    response = {
                            'success': True,
                            'statusCode': status_code,
                            'message': 'User logged in successfully',
                            'access': access_token,
                            'refresh': refresh_token,
                            'user': user.first_name+" "+user.last_name,
                            'role': user.role
                        }

                    return Response(response, status=status_code)
                else:
                        return Response({'error': 'Email not verified'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    
            
    
class UserListView(APIView):
    serializer_class = UserListSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        user = CustomUser.objects.all()
        serializer = self.serializer_class(user, many=True)
        response = {
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Successfully fetched users',
                'users': serializer.data

            }
        return Response(response, status=status.HTTP_200_OK)
    
class ForgotPasswordView(APIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = (AllowAny,)
    def post(self, request):      
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception = True)
        
        if valid:
            email = serializer.validated_data['email']
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)
            def email_otp(email):
                subject = "Otp for Forgot Passwod"
                otp = random.randint(100000, 999999)
                message = f"your otp is {otp}"
                email_from = settings.EMAIL_HOST
                send_mail(subject, message, email_from, [email] )
                CustomUser_obj = CustomUser.objects.get(email=email)
                CustomUser_obj.otp = otp
                CustomUser_obj.save()
            email_otp(serializer.data['email'])
            
            status_code= status.HTTP_202_ACCEPTED
            response={
                'success': True,
                'status': status_code,
                'message' : 'sent otp succesfully',
                'user': serializer.data
           }
            return Response( response, status=status_code)
        

class ResetPasswordView(APIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = (AllowAny,)
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new = request.data.get('new_password')
        confirm = request.data.get('confirm_new_password')
        
        user = CustomUser.objects.all()
        if not email:
            return Response({'error': 'email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not otp:
            return Response({'error': 'OTP is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the user and their associated OTP from the database (assuming you have stored it during registration)
        if new != confirm: 
            return Response({'error': 'New password doesnot match with confirm password.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            user = CustomUser.objects.get(email=email ,otp = otp)
        except CustomUser.DoesNotExist:
                return Response({'error': 'User with this email does not exist. or the OTP you entered is wrong, please check the OTP'}, status=status.HTTP_404_NOT_FOUND)
            
        user.set_password(new)
        user.save()
        update_session_auth_hash(request, user)
        status_code = status.HTTP_200_OK
                

        response = {
                'success': True,
                'statusCode': status_code,
                'message': 'Your password is updated succesfully',
            }
        return Response(response, status_code)
    
class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404
    def delete(self, request, pk):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class AddressViewSet(viewsets.ModelViewSet):
    queryset = ShippingAddress.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    @action(detail=False, methods=['GET'])
    def get_addresses_by_user(self, request):
        user = request.query_params.get('user')
        if user:
            addresses = ShippingAddress.objects.filter(user_id=user)
            serializer = AddressSerializer(addresses, many=True)
            return Response(serializer.data)
        else:
            return Response({'message': 'Please provide a user parameter in the query.'}, status=400)
        
class CreateUserProfile(generics.CreateAPIView):
    """
    create a new user profile.
    """
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    pagination_class = PageNumberPagination

class UpdateUserProfile(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    pagination_class = PageNumberPagination

class InventoryViewSet(viewsets.ModelViewSet):
    
    queryset = Store.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination


#Brand Views
class BannerCreateView(generics.CreateAPIView):  
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [IsAuthenticated ]
    pagination_class = PageNumberPagination

class BannersView(generics.ListAPIView):   
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = (AllowAny, )
    pagination_class = PageNumberPagination
    
class BannerRetrieveView(generics.RetrieveAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = (AllowAny, )
    pagination_class = PageNumberPagination    

class BannerUpdateView(generics.UpdateAPIView):    
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [IsAuthenticated ]
    pagination_class = PageNumberPagination

class BannerDeleteView(generics.DestroyAPIView):   
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [IsAuthenticated ]
    pagination_class = PageNumberPagination

class CategoryCreateView(generics.CreateAPIView):
    
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = [IsAuthenticated ]
    pagination_class = PageNumberPagination

class CategoriesView(generics.ListAPIView):
    
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (AllowAny, )
    pagination_class = PageNumberPagination
    
class CategoryRetrieveView(generics.RetrieveAPIView):
    
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (AllowAny, )
    pagination_class = PageNumberPagination
    

class CategoryUpdateView(generics.UpdateAPIView):
    
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = [IsAuthenticated ]
    pagination_class = PageNumberPagination

class CategoryDeleteView(generics.DestroyAPIView):
    
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = [IsAuthenticated ]
    pagination_class = PageNumberPagination


#Subcategory Views
class SubcategoryCreateView(generics.CreateAPIView):  
    queryset = SubCategories.objects.all()
    serializer_class = SubCategoriesSerializer
    permission_classes = [IsAuthenticated ]
    pagination_class = PageNumberPagination

class SubcategoriesView(generics.ListAPIView):   
    queryset = SubCategories.objects.all()
    serializer_class = SubCategoriesSerializer
    permission_classes = (AllowAny, )
    pagination_class = PageNumberPagination
    
class SubcategoryRetrieveView(generics.RetrieveAPIView):
    queryset = SubCategories.objects.all()
    serializer_class = SubCategoriesSerializer
    permission_classes = (AllowAny, )
    pagination_class = PageNumberPagination    

class SubcategoryUpdateView(generics.UpdateAPIView):    
    queryset = SubCategories.objects.all()
    serializer_class = SubCategoriesSerializer
    permission_classes = [IsAuthenticated ]
    pagination_class = PageNumberPagination

class SubcategoryDeleteView(generics.DestroyAPIView):   
    queryset = SubCategories.objects.all()
    serializer_class = SubCategoriesSerializer
    permission_classes = [IsAuthenticated ]
    pagination_class = PageNumberPagination

#Brand Views
class BrandCreateView(generics.CreateAPIView):  
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated ]
    pagination_class = PageNumberPagination

class BrandView(generics.ListAPIView):   
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = (AllowAny, )
    pagination_class = PageNumberPagination
    
class BrandRetrieveView(generics.RetrieveAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = (AllowAny, )
    pagination_class = PageNumberPagination    

class BrandUpdateView(generics.UpdateAPIView):    
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated ]
    pagination_class = PageNumberPagination

class BrandDeleteView(generics.DestroyAPIView):   
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated ]
    pagination_class = PageNumberPagination

#Products Views
class ProductsCreateView(generics.CreateAPIView):  
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    permission_classes = [IsAuthenticated ]
    pagination_class = PageNumberPagination

class ProductsView(generics.ListAPIView):   
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    permission_classes = (AllowAny, )
    pagination_class = PageNumberPagination
    
class ProductsRetrieveView(generics.RetrieveAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    permission_classes = (AllowAny, )
    pagination_class = PageNumberPagination    

class ProductsUpdateView(generics.UpdateAPIView):    
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    permission_classes = [IsAuthenticated ]
    pagination_class = PageNumberPagination

class ProductsDeleteView(generics.DestroyAPIView):   
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    permission_classes = [IsAuthenticated ]
    pagination_class = PageNumberPagination

class VarientsViewSet(viewsets.ModelViewSet):
    
    queryset = ProductVariant.objects.all()
    serializer_class = VarientsSerializer
    permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,filters.OrderingFilter)
    filterset_class = ProductVariantFilter
    
class ProductMediaViewSet(viewsets.ModelViewSet):
    
    queryset = ProductMedia.objects.all()
    serializer_class = ProductMediaSerializer
    permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination


class ProductQuestionsViewSet(viewsets.ModelViewSet):
    
    queryset = ProductQuestions.objects.all()
    serializer_class = ProductQuestionsSerializer
    permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,filters.OrderingFilter)
    filterset_class = ProductQuestionsFilter

class AnswerViewSet(viewsets.ModelViewSet):
    
    queryset = ProductAnswer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class ProductReviewsViewSet(viewsets.ModelViewSet):
    
    queryset = ProductReviews.objects.all()
    serializer_class = ProductReviewsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,filters.OrderingFilter)
    filterset_class = ProductReviewsFilter

class CartViewSet(viewsets.ModelViewSet):
    
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class CartItemCreateView(generics.CreateAPIView):
    
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination

class CartItemView(generics.ListAPIView):   
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = (AllowAny, )
    pagination_class = PageNumberPagination
    
class CartItemRetrieveView(generics.RetrieveAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = (AllowAny, )
    pagination_class = PageNumberPagination    

class CartItemUpdateView(generics.UpdateAPIView):    
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated ]
    pagination_class = PageNumberPagination

class CartItemDeleteView(generics.DestroyAPIView):   
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated ]
    pagination_class = PageNumberPagination

class OrderViewSet(viewsets.ModelViewSet):
    
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class OrderItemListView(generics.ListCreateAPIView):
    
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class OrderItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class PaymentViewSet(viewsets.ModelViewSet):
    
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class OrderCancelViewSet(viewsets.ModelViewSet):
    queryset = CancelOrder.objects.all()
    serializer_class=OrderCanceledSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class WishlistView(generics.ListAPIView):
    queryset = Wishlist.objects.all()
    serializer_class=GetWishlistSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class WishlistCreateView(generics.CreateAPIView):
    queryset = Wishlist.objects.all()
    serializer_class=CreateWishlistSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class WishlistCreateView(generics.RetrieveDestroyAPIView):
    queryset = Wishlist.objects.all()
    serializer_class=CreateWishlistSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
# Create your views here.

class Count(APIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        counts = {
            'Categories': Categories.objects.count(),
            'Sub Categories': SubCategories.objects.count(),
            'Brands':Brand.objects.count(),
            'Products':Products.objects.count(),
            'Users':CustomUser.objects.count(),

            
            # Add more counts for other models as needed
        }
        return Response(counts)

class UserCount(APIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        counts = {}
        for role, _ in CustomUser.ROLE_CHOICES:
            count = CustomUser.objects.filter(role=role).count()
            counts[role] = count
        return Response(counts)

