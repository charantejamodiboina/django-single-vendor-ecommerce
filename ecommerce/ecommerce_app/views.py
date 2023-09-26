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
                            'last_login': user.last_login,
                            'user': serializer.data
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
        user = CustomUser.objects.get(email=email)
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
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class CategoriesViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class SubCategoriesViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = SubCategories.objects.all()
    serializer_class = SubCategoriesSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class BrandViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class ProductsViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,filters.OrderingFilter)
    filterset_class = ProductsFilter

class VarientsViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = ProductVariant.objects.all()
    serializer_class = VarientsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,filters.OrderingFilter)
    filterset_class = ProductVariantFilter
    
class ProductMediaViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = ProductMedia.objects.all()
    serializer_class = ProductMediaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class ProductTransactionViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = ProductTransaction.objects.all()
    serializer_class = ProductTransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class ProductDetailsViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = ProductDetails.objects.all()
    serializer_class = ProductDetailsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,filters.OrderingFilter)
    filterset_class = ProductDetailsFilter

class ProductQuestionsViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = ProductQuestions.objects.all()
    serializer_class = ProductQuestionsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,filters.OrderingFilter)
    filterset_class = ProductQuestionsFilter

class AnswerViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = ProductAnswer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class ProductReviewsViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = ProductReviews.objects.all()
    serializer_class = ProductReviewsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,filters.OrderingFilter)
    filterset_class = ProductReviewsFilter

class CartViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class CartItemListView(generics.ListCreateAPIView):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class OrderViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class OrderItemListView(generics.ListCreateAPIView):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class OrderItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class PaymentViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

# Create your views here.