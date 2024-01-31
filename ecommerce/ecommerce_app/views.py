from django.shortcuts import render
from django.db.models import Q
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
from .filters import*
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

# from fcm_django.models import FCMDevice
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
            
            
class UserLoginView(ObtainAuthToken):
    permission_classes = (AllowAny, )
    user=CustomUser.objects.all()
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        print(user)
        if user.is_verified:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            
            response_data = {
                'success': True,
                'statusCode': status.HTTP_200_OK,
                'message': 'User logged in successfully',
                'user': user.first_name + " " + user.last_name,
                'role': user.role,
                'user_id': user.id,
                'access': token.key,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Email not verified'}, status=status.HTTP_400_BAD_REQUEST)    
    
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
        if not new:
            return Response({'error': 'new_password is required.'}, status=status.HTTP_400_BAD_REQUEST)
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
    authentication_classes = [TokenAuthentication]
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
    authentication_classes = [TokenAuthentication]
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
#Banner Views
class BannerCreateView(generics.CreateAPIView):  
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class BannersView(generics.ListAPIView):   
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = (AllowAny, )

    
class BannerRetrieveView(generics.RetrieveAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = (AllowAny, )

class BannerUpdateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Banner.objects.get(pk=pk)
        except Banner.DoesNotExist:
            raise Http404
    def put(self, request, pk, format=None):
        banner = self.get_object(pk)
        serializer = BannerSerializer(banner, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk, format=None):
        banner = self.get_object(pk)
        banner.delete()
        return Response({'message': f'banner is deleted.'}, status=status.HTTP_204_NO_CONTENT)

# Categories code
class CategoryCreateView(generics.CreateAPIView):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class CategoriesView(generics.ListAPIView):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (AllowAny, )
    
class CategoryRetrieveView(generics.RetrieveAPIView): 
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (AllowAny, )

class CategoryUpdateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Categories.objects.get(pk=pk)
        except Categories.DoesNotExist:
            raise Http404
    def put(self, request, pk, format=None):
        category = self.get_object(pk)
        serializer = CategoriesSerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk, format=None):
        category = self.get_object(pk)
        category.delete()
        return Response({'message': f'category is deleted.'}, status=status.HTTP_204_NO_CONTENT)

#Subcategory Views
class SubcategoryCreateView(generics.CreateAPIView):  
    queryset = SubCategories.objects.all()
    serializer_class = SubCategoriesSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class SubcategoriesView(generics.ListAPIView):   
    # queryset = SubCategories.objects.all()
    serializer_class = SubCategoriesViewSerializer
    permission_classes = (AllowAny, )
    def get_queryset(self):
        queryset = SubCategories.objects.all()
        category_name = self.request.query_params.get('category_name', None)
        name_contains = self.request.query_params.get('name', None)
        if category_name:
            queryset=queryset.filter(category__name__icontains=category_name)
        if name_contains:
            if name_contains.strip():
                queryset = queryset.filter(name__icontains=name_contains)
        return queryset
    
class SubcategoryRetrieveView(generics.RetrieveAPIView):
    queryset = SubCategories.objects.all()
    serializer_class = SubCategoriesViewSerializer
    permission_classes = (AllowAny, ) 

class SubcategoryUpdateView(APIView):    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return SubCategories.objects.get(pk=pk)
        except SubCategories.DoesNotExist:
            raise Http404
    def put(self, request, pk, format=None):
        subcategory = self.get_object(pk)
        serializer = SubCategoriesSerializer(subcategory, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk, format=None):
        subcategory = self.get_object(pk)
        subcategory.delete()
        return Response({'message': 'subcategory is deleted.'}, status=status.HTTP_204_NO_CONTENT)

#Products Views
class ProductsCreateView(generics.CreateAPIView):  
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class ProductsView(generics.ListAPIView):   
    serializer_class = ProductsViewSerializer
    permission_classes = (AllowAny, )
    def get_queryset(self):
        queryset = Products.objects.all()
        subcategory = self.request.query_params.get('subcategory', None)
        variant = self.request.query_params.get('variant', None)
        name = self.request.query_params.get('name', None)
        
        if subcategory:
            queryset=queryset.filter(subcategories_id__name__icontains=subcategory)
        if variant:
            queryset=queryset.filter(variant__variant_name__icontains=variant)
        if name:
            queryset=queryset.filter(name__icontains=name)
        return queryset
    def get_queryset(self):
        queryset = Products.objects.all()
        max_price = self.request.query_params.get('max_price', None)
        min_price = self.request.query_params.get('min_price', None)
        if min_price and max_price:
            queryset=queryset.filter(price__gte=min_price, price__lte=max_price)
        elif min_price:
            queryset=queryset.filter(price__gte=min_price)
        elif max_price:
            queryset=queryset.filter(price__lte=max_price)
        return queryset

class ProductsRetrieveView(generics.RetrieveAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductsViewSerializer
    permission_classes = (AllowAny, )
    
class ProductsUpdateView(APIView):    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Products.objects.get(pk=pk)
        except Products.DoesNotExist:
            raise Http404
    def put(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductsSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk, format=None):
        product = self.get_object(pk)
        product.delete()
        return Response({'message': 'Product is deleted.'}, status=status.HTTP_204_NO_CONTENT)

# Product variants views
class VarientsPost(generics.CreateAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = VariantsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class Varientslist(generics.ListAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = VariantsSerializer
    permission_classes = (AllowAny, ) 

class VarientsDetails(generics.RetrieveAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = VariantsSerializer
    permission_classes = (AllowAny, )

class VarientUpdateView(APIView):    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return ProductVariant.objects.get(pk=pk)
        except ProductVariant.DoesNotExist:
            raise Http404
    def put(self, request, pk, format=None):
        product_variant = self.get_object(pk)
        serializer = VariantsSerializer(product_variant, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk, format=None):
        product_variant = self.get_object(pk)
        product_variant.delete()
        return Response({'message': 'Product Variant is deleted.'}, status=status.HTTP_204_NO_CONTENT)

# Product Questions view
class ProductQuestionsCreate(generics.CreateAPIView):
    queryset = ProductQuestions.objects.all()
    serializer_class = ProductQuestionsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class ProductQuestionslist(generics.ListAPIView):
    queryset = ProductQuestions.objects.all()
    serializer_class = ProductQuestionsSerializer
    permission_classes = (AllowAny,)

class ProductQuestionsDetails(generics.RetrieveAPIView):
    queryset = ProductQuestions.objects.all()
    serializer_class = ProductQuestionsSerializer
    permission_classes = (AllowAny,)

# product answer view
class PostAnswer(generics.CreateAPIView):   
    queryset = ProductAnswer.objects.all()
    serializer_class = AnswerSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class Answerslist(generics.ListAPIView):
    queryset = ProductAnswer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = (AllowAny, )


class AnswerDetails(generics.RetrieveAPIView):
    queryset = ProductAnswer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = (AllowAny, )

# Product review
class CreateProductReview(generics.CreateAPIView):   
    queryset = ProductReviews.objects.all()
    serializer_class = ProductReviewsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class ListProductReview(generics.ListAPIView):
    queryset = ProductReviews.objects.all()
    serializer_class = ProductReviewsSerializer
    permission_classes = (AllowAny, )

class RetrieveProductReview(generics.RetrieveAPIView):
    queryset = ProductReviews.objects.all()
    serializer_class = ProductReviewsSerializer
    permission_classes = (AllowAny, )

# Cart item  views
class CartItemCreateView(generics.CreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = (AllowAny,)

class CartItemView(generics.ListAPIView):   
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = (AllowAny, )
    
class CartItemRetrieveView(generics.RetrieveAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = (AllowAny, )
    
class CartItemUpdateView(APIView):    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return CartItem.objects.get(pk=pk)
        except CartItem.DoesNotExist:
            raise Http404
    def put(self, request, pk, format=None):
        cart_item = self.get_object(pk)
        serializer = CartItemSerializer(cart_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk, format=None):
        cart_item = self.get_object(pk)
        cart_item.delete()
        return Response({'message': 'CartItem is deleted.'}, status=status.HTTP_204_NO_CONTENT)

# order item views
class OrderItemListView(generics.ListCreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class OrderItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class WishlistView(generics.ListAPIView):
    queryset = Wishlist.objects.all()
    serializer_class=GetWishlistSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class WishlistCreateView(generics.CreateAPIView):
    queryset = Wishlist.objects.all()
    serializer_class=CreateWishlistSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class WishlistUpdateView(generics.RetrieveDestroyAPIView):
    queryset = Wishlist.objects.all()
    serializer_class=CreateWishlistSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class Count(APIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        counts = {
            'Categories': Categories.objects.count(),
            'Sub Categories': SubCategories.objects.count(),
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

# class PushNotificationView(APIView):
#     permission_classes = (AllowAny,)
#     def post(self, request):
#         serializer = PushNotificationSerializer(data=request.data)
#         if serializer.is_valid():
#             registration_ids = serializer.validated_data['registration_ids']
#             data = serializer.validated_data['data']
            
#             # Send the push notification to the specified devices
#             devices = FCMDevice.objects.filter(registration_id__in=registration_ids)
#             message = "Your push notificat0ion message"
#             devices.send_message(message)
            
            
#             return Response({"message": "Push notifications sent successfully"}, status=status.HTTP_200_OK)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # cart views
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class OrderCancelViewSet(viewsets.ModelViewSet):
    queryset = CancelOrder.objects.all()
    serializer_class=OrderCanceledSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class UserProfileViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer        
class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = InventorySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]