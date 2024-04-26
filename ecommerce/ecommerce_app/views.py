from django.shortcuts import render
from rest_framework_bulk import BulkCreateAPIView
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import*
import requests
from django.db import transaction, DatabaseError
from django.core.exceptions import ObjectDoesNotExist
from .serializers import*
from django.db.models import Avg
from django.conf import settings
from .email import*
# from django.conf import settings
from django.core.mail import send_mail
from rest_framework.decorators import api_view, authentication_classes, permission_classes
import random
from django.http import Http404
from rest_framework import viewsets
from django.contrib.auth import authenticate, login
from rest_framework import generics
from rest_framework.decorators import action
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination
from .filters import*
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
# from fcm_django.models import FCMDevice
from django.views.decorators.csrf import csrf_exempt
import razorpay
from rest_framework.parsers import MultiPartParser
import pandas as pd
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Sum
TIME_ZONE ='Asia/Kolkata'
from datetime import datetime, timedelta

# Registration APIView
class UserRegistrationView(APIView):
    user=CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny, )
    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        valid = serializers.is_valid(raise_exception = True)
        if valid:
            user=serializers.save()
            cart = Cart.objects.create(user=user)
            wishlist = WishList.objects.create(user=user)
            email_otp(serializers.data['email'])
            
            status_code= status.HTTP_201_CREATED
            response={
                'success': True,
                'status': status_code,
                'message' : 'user successfully created',
                'user': serializers.data
           }
            return Response( response, status=status_code)

# Email OTP verification API view
class VerifyOtp(APIView):
    serializer_class = VerifyAccountSerializer
    permission_classes = (AllowAny,)
    def post(self, request):
        otp = request.data.get('otp')
        email = request.data.get('email')
        if not email or not otp:
            return Response({'error': 'email and otp is required.'}, status=status.HTTP_400_BAD_REQUEST)
        # Get the user and their associated OTP from the database (assuming you have stored it during registration)
        try:
            user = CustomUser.objects.get(email=email) 
        except CustomUser.DoesNotExist:
            raise Http404
        if otp != user.otp:
            return Response({'error': 'Invalid otp'}, status=status.HTTP_400_BAD_REQUEST)
        # Compare the received OTP with the one in the database
        
        user.is_verified = True
        user.save()
        return Response({'message': 'OTP verified successfully.'}, status=status.HTTP_200_OK)
            
# Login API view
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
    
# Registered user list API view
class UserListView(APIView):
    serializer_class = UserListSerializer
    permission_classes = (AllowAny,)
    def get(self, request):
        try:
            role = request.query_params.get('role', None)

            if role:
                # Filter users based on role
                users = CustomUser.objects.filter(role=role)
            else:
                # If no role is specified, retrieve all users
                users = CustomUser.objects.all()

            serializer = self.serializer_class(users, many=True)

            response = {
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Successfully fetched users',
                'users': serializer.data
            }

            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the exception for debugging purposes
            print(f"Exception in UserListView: {e}")
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#OTP sent API view for forgot password 
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
            # here this code sent the random OTP to registered email and save that OTP in db
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
        
# Reset password API view
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
    
# Change password 
class ChangePasswordView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    def get_object(self):
        return self.request.user
    def post(self, request, format=None):
        user=self.get_object()
        old = request.data.get('old_password')
        new = request.data.get('new_password')
        #it checks the old password is entered or not
        if not old:
            return Response({'detail': 'old_password is required.'}, status=status.HTTP_400_BAD_REQUEST)
        #it checks the old password with your entered old password
        if not user.check_password(old):
            print(user.check_password)
            return Response({'detail':'The old password you entered is incorrect.'}, status=status.HTTP_401_UNAUTHORIZED)
        #it checks the new password is entered or not
        if not new:
            return Response({'detail': 'new_password is required.'}, status=status.HTTP_400_BAD_REQUEST)
        # it check if new password and old password are same
        if new==old:
            return Response({'detail':"Sorry, your new password can't be the same as your old one. Choose a different password."}, status=status.HTTP_400_BAD_REQUEST)
        serializer=self.serializer_class(user, data=request.data)
        if serializer.is_valid():
            user.set_password(new)
            user.save()
            print(user)
            update_session_auth_hash(request, user)
            status_code = status.HTTP_200_OK
            return Response({'detail': 'Your password is updated succesfully'}, status_code)
        
#User account delete API view 
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

# Plan Subscription Views
class PlanSubscription(generics.ListCreateAPIView):
    permission_classes=(AllowAny, )
    queryset=Subscription.objects.all()
    serializer_class=SubscriptionSerializer

class PlanSubscriptioRetrieveDelete(generics.RetrieveDestroyAPIView):
    permission_classes=(AllowAny, )
    queryset=Subscription.objects.all()
    serializer_class=SubscriptionSerializer

class PlanSubscriptionUpdate(APIView):
    permission_classes=(AllowAny)
    def get_object(self, pk):
        try:
            return Subscription.objects.get(pk=pk)
        except Subscription.DoesNotExist:
            raise Http404
    def patch(self, request, pk, format=None):
        subscription=self.get_object(pk)
        serializer=SubscriptionSerializer(subscription, data=request.data, partial=True)
        if serializer.is_valid:
            serializer.save()
            return Response({'detail':'Subscription updated successfully'}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
# Address API view
class AddressByUserId(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        try:
            addresses=ShippingAddress.objects.filter(user=pk)
            serializer=AddressSerializer(addresses, many=True)
            return Response(serializer.data)
        except ShippingAddress.DoesNotExist:
            return Response({'detail':'Shipping addresses doesnt exist'}, status=status.HTTP_404_NOT_FOUND)
class AddressView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        all_address=ShippingAddress.objects.all()
        serializer=AddressSerializer(all_address, many=True)
        return Response(serializer.data)
    def post(self, request, format=None):
        serializer=AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddressById(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return ShippingAddress.objects.get(pk=pk)
        except ShippingAddress.DoesNotExist:
            raise Http404
    def get(self, request, pk, format=None):
        address=self.get_object(pk)
        serializer=AddressSerializer(address)
        return Response(serializer.data)
    def patch(self, request, pk, format=None):
        address=self.get_object(pk)
        serializer=AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'Shipping address updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk, format=None):
        address=self.get_object(pk)
        address.delete()
        return Response({'detail':'Shipping address deleted successfully'})

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
    def patch(self, request, pk, format=None):
        banner = self.get_object(pk)
        serializer = BannerSerializer(banner, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk, format=None):
        banner = self.get_object(pk)
        banner.delete()
        return Response({'message': f'banner is deleted.'}, status=status.HTTP_204_NO_CONTENT)

# Categories API Views 
# create, retrieve, update, delete, bulk upload(JSON & Excel), bulk delete
class CategoryCreateView(generics.CreateAPIView):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class BulkCategoryCreateView(BulkCreateAPIView):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class CategoryBulkUploadView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    def post(self, request, *args, **kwargs):
        file = request.data.get('file')

        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file, engine='openpyxl')

            # Validate the structure of the DataFrame if needed

            data_to_create = df.to_dict(orient='records')

            serializer = CategoriesSerializer(data=data_to_create, many=True)
            serializer.is_valid(raise_exception=True)

            self.perform_bulk_create(serializer)

            return Response({'message': 'Data uploaded successfully'}, status=status.HTTP_201_CREATED)

        except pd.errors.EmptyDataError:
            return Response({'error': 'Empty file provided'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    def perform_bulk_create(self, serializer):
        Categories.objects.bulk_create([Categories(**item) for item in serializer.validated_data])

class BulkCategoryDelete(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        category_ids = request.data.get('category_ids', [])
        if not category_ids:
            return Response({'detail': 'category_ids are not provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            categories=Categories.objects.filter(id__in=category_ids)
            categories.delete()
            return Response({'detail':'provided categories are deleted'}, status=status.HTTP_200_OK)
        except Categories.DoesNotExist:
            return Response({'detail':'one or more category_ids are not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    def patch(self, request, pk, format=None):
        category = self.get_object(pk)
        serializer = CategoriesSerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk, format=None):
        category = self.get_object(pk)
        category.delete()
        return Response({'message': f'category is deleted.'}, status=status.HTTP_204_NO_CONTENT)

#Subcategory Views
# create, retrieve, update, delete, bulk upload(JSON & Excel), bulk delete
class SubcategoryCreateView(generics.CreateAPIView):  
    queryset = SubCategories.objects.all()
    serializer_class = SubCategoriesSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class BulkSubcategoryCreateView(BulkCreateAPIView):  
    queryset = SubCategories.objects.all()
    serializer_class = SubCategoriesSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class SubcategoryBulkUploadView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    def post(self, request, *args, **kwargs):
        file = request.data.get('file')

        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file, engine='openpyxl')

            # Validate the structure of the DataFrame if needed

            data_to_create = df.to_dict(orient='records')

            serializer = SubCategoriesSerializer(data=data_to_create, many=True)
            serializer.is_valid(raise_exception=True)

            self.perform_bulk_create(serializer)

            return Response({'message': 'Data uploaded successfully'}, status=status.HTTP_201_CREATED)

        except pd.errors.EmptyDataError:
            return Response({'error': 'Empty file provided'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    def perform_bulk_create(self, serializer):
        SubCategories.objects.bulk_create([SubCategories(**item) for item in serializer.validated_data])

class BulkSubcategoryDelete(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        subcategory_ids = request.data.get('subcategory_ids', [])

        if not subcategory_ids:
            return Response({'detail':'subcategory ids are not provided'}, status=status.HTTP_400_BAD_REQUEST )
        try:
            subcategories = SubCategories.objects.filter(id__in=subcategory_ids)
            subcategories.delete()
            return Response({'details': 'Provided subcategory ids are deleted Successfully'}, status=status.HTTP_200_OK)
        except SubCategories.DoesNotExist:
            return Response({'detail':'one or more provided subcategory ids is not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SubcategoriesView(generics.ListAPIView):   
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
    def patch(self, request, pk, format=None):
        subcategory = self.get_object(pk)
        serializer = SubCategoriesSerializer(subcategory, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk, format=None):
        subcategory = self.get_object(pk)
        subcategory.delete()
        return Response({'message': 'subcategory is deleted.'}, status=status.HTTP_204_NO_CONTENT)

#Products Views
# create, retrieve, update, delete, bulk upload(JSON & Excel), bulk delete
class BulkProductsCreateView(BulkCreateAPIView):  
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class ProductBulkUploadView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    def post(self, request, *args, **kwargs):
        file = request.data.get('file')

        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file, engine='openpyxl')

            # Validate the structure of the DataFrame if needed

            data_to_create = df.to_dict(orient='records')

            serializer = ProductsSerializer(data=data_to_create, many=True)
            serializer.is_valid(raise_exception=True)

            self.perform_bulk_create(serializer)

            return Response({'message': 'Data uploaded successfully'}, status=status.HTTP_201_CREATED)

        except pd.errors.EmptyDataError:
            return Response({'error': 'Empty file provided'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    def perform_bulk_create(self, serializer):
        Products.objects.bulk_create([Products(**item) for item in serializer.validated_data])

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
        product = self.request.query_params.get('product', None)
        subcategory = self.request.query_params.get('subcategory', None)
        category = self.request.query_params.get('category', None)
        variant = self.request.query_params.get('variant', None)
        name = self.request.query_params.get('name', None)
        max_price = self.request.query_params.get('max_price', None)
        min_price = self.request.query_params.get('min_price', None)
        new_arrival = self.request.query_params.get('new_arrival', None)
        if subcategory:
            queryset=queryset.filter(subcategories_id__name__icontains=subcategory)
        if category:
            queryset=queryset.filter(subcategories_id__category__name__icontains=category)
        if variant:
            queryset=queryset.filter(variant__variant_name__icontains=variant)
        if name:
            queryset=queryset.filter(name__icontains=name)        
        if new_arrival:
            cutoff=timezone.now()-timedelta(days=int(new_arrival))
            queryset=queryset.filter(created_at__gte=cutoff)
        
        if min_price and max_price:
            queryset=queryset.filter(price__gte=min_price, price__lte=max_price)
        elif min_price:
            queryset=queryset.filter(price__gte=min_price)
        elif max_price:
            queryset=queryset.filter(price__lte=max_price)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        for product_data in serializer.data:
            product_id = product_data['id']
            reviews = ProductReviews.objects.filter(product_id=product_id)
            avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
            product_data['average_rating'] = avg_rating

        return Response(serializer.data)

# class ProductAgregatedData(APIView):
#     permission_classes = (AllowAny, )
#     def get(self, request):
#         host=settings.ALLOWED_HOSTS[0]
#         base_url = f'http://{host}:8000'
#         response1=requests.get(f'{base_url}/products?new_arrival=7')
#         response2=requests.get(f'{base_url}/product/discount')
#         new_arrivals=response1.json()
#         big_discount=response2.json()
#         agregated_data={
#             'New_Arrivals':new_arrivals,
#             'Big_Discounts':big_discount
#         }
#         return Response(agregated_data)
    
class BigDiscount(generics.ListAPIView):   
    serializer_class = ProductsViewSerializer
    permission_classes = (AllowAny, )
    def get_queryset(self):
        queryset=Products.objects.all()
        big_discount = queryset.filter(discount_type='percentage', discount__gte=40, discount__lte=100)

        # Concatenate the two querysets
        return big_discount
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        for product_data in serializer.data:
            product_id = product_data['id']
            reviews = ProductReviews.objects.filter(product_id=product_id)
            avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
            product_data['average_rating'] = avg_rating
        return Response(serializer.data)

class ProductRetrieve(generics.RetrieveAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductsViewSerializer
    permission_classes=(AllowAny ,)
        
class ProductsUpdateView(APIView):    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Products.objects.get(pk=pk)
        except Products.DoesNotExist:
            raise Http404
    def patch(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductsSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk, format=None):
        product = self.get_object(pk)
        product.delete()
        return Response({'message': 'Product is deleted.'}, status=status.HTTP_204_NO_CONTENT)

class BulkProductDelete(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **Kwargs):
        product_ids = request.data.get('product_ids', [])
        if not product_ids:
            return Response({'detail':'product_ids are not provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            products=Products.objects.filter(id__in=product_ids)
            products.delete()
            return Response({'detail':'provided products are deleted'}, status=status.HTTP_200_OK)
        except Products.DoesNotExist:
            return Response({'detail':'one or more provided product_ids are not found'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

# Product variants views
class VarientsPost(generics.CreateAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = VariantsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class CreateBulkVariants(BulkCreateAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = VariantsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class VarientBulkUploadView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    def post(self, request, *args, **kwargs):
        file = request.data.get('file')

        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file, engine='openpyxl')

            # Validate the structure of the DataFrame if needed

            data_to_create = df.to_dict(orient='records')

            serializer = VariantsSerializer(data=data_to_create, many=True)
            serializer.is_valid(raise_exception=True)

            self.perform_bulk_create(serializer)

            return Response({'message': 'Data uploaded successfully'}, status=status.HTTP_201_CREATED)

        except pd.errors.EmptyDataError:
            return Response({'error': 'Empty file provided'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    def perform_bulk_create(self, serializer):
        ProductVariant.objects.bulk_create([ProductVariant(**item) for item in serializer.validated_data])

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
    def patch(self, request, pk, format=None):
        product_variant = self.get_object(pk)
        serializer = VariantsSerializer(product_variant, data=request.data, partial=True)
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
class ProductQuestionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return ProductQuestions.objects.filter(product_id=pk)
        except ProductQuestions.DoesNotExist:
            raise Http404
    def get(self, request, pk, format=None):
        product=self.get_object(pk)
        serializer = ProductQuestionsSerializer(product, many=True)
        return Response(serializer.data)
        
class ProductQuestionsDetails(generics.RetrieveAPIView):
    queryset = ProductQuestions.objects.all()
    serializer_class = ProductQuestionsSerializer
    permission_classes = (AllowAny,)

# product answer view
class ProductAnswersView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return ProductAnswer.objects.filter(question_id=pk)
        except ProductAnswer.DoesNotExist:
            raise Http404
    def get(self, request, pk, format=None):
        answer=self.get_object(pk)
        serializer=AnswerSerializer(answer, many=True)
        return Response(serializer.data)
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

class ProductReview(APIView):
    permission_classes = (AllowAny ,)
    def get_object(self, pk):
        try:
            return ProductReviews.objects.filter(product_id=pk)
        except ProductReviews.DoesNotExist:
            raise Http404
    def get(self, request, pk, format=None):
        try:
            product = self.get_object(pk)
            # review = ProductReviews.objects.filter( product_id=product)
            serializer = ProductReviewsSerializer(product, many=True) 
            average_rating = product.aggregate(average_rating=Avg('rating'))['average_rating'] or 0

            rating_count = product.count()

            response_data = {
                'reviews': serializer.data,
                'average_rating': average_rating,
                'rating_count': rating_count
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Cart item  views
class CartItemView(generics.ListAPIView):
    serializer_class = CartItemSerializer
    permission_classes = (AllowAny, )
    def get_queryset(self):
        queryset = CartItem.objects.all()
        cart=self.request.query_params.get('cart', None)
        if cart:
            queryset=queryset.filter(cart_id=cart)
        return queryset

class CartlistView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # get cart
    def get(self, request, *args, **kwargs):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        serializer = CartViewSerializer(cart)  # Replace with your serializer
        return Response(serializer.data)
    
class CartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # get cart
    def get(self, request, *args, **kwargs):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        serializer = CartSerializer(cart)  # Replace with your serializer
        return Response(serializer.data)
    # add product in cart
    def post(self, request, *args, **kwargs):
        user = request.user
        print(user)
        cart = get_object_or_404(Cart, user=user)
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)
        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        # Check if the product is already in the cart, update quantity if so
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()      
        # Update the cart's total price
        cart.update_total_price()
        serializer = CartSerializer(cart)  # Replace with your serializer
        return Response(serializer.data)
    # update cart items quantity
    def put(self, request, *args, **kwargs):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))
        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        # Remove the product quantity from the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity =max(1, cart_item.quantity - quantity)
            cart_item.save()
        # Update the cart's total price
        cart.update_total_price()
        serializer = CartSerializer(cart)  # Replace with your serializer
        return Response(serializer.data)
    # delete cart items by product id
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        product_id = request.data.get('product')
        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        # Get the cart items before deleting them
        cart_items = CartItem.objects.filter(cart=cart, product=product)
        # Save the quantity of each cart item before deleting
        quantities = [cart_item.quantity for cart_item in cart_items]
        # Remove the product from the cart
        cart_items.delete()
        # Update the cart's total price
        cart.update_total_price()
        serializer = CartSerializer(cart)  # Replace with your serializer
        return Response(serializer.data)


class Checkout(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def post(self, request, *args, **kwargs):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        product_id = request.data.get('product')
        # Ensure the cart is not empty
        if cart.items.count() == 0:
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)
        #check the address is added or not
        address = user.shippingaddress_set.first()
        if not address:
            return Response({'detail':'Please add shipping address before checkout order'}, status=status.HTTP_400_BAD_REQUEST)
        # Create an order
        
        order = Order.objects.create(user=user, total_price=cart.total_price, address=address)
        order.generate_order_id()
        # Transfer items from the cart to the order
        for item in cart.cartitem_set.all():
            
            OrderItems.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                items_price=item.items_price
            )
            product=item.product
            if product.stock < item.quantity:
                return Response({'detail': f'Not enough stock for {item.product.name}.'}, status=status.HTTP_400_BAD_REQUEST)
        # Update the product stock
            product.stock -= item.quantity
            product.save()
        # Optionally, you may want to clear the cart after checkout
        cart.items.clear()
        # Additional logic for payment, shipping, etc., can be added here
        order.save()
        # Construct the response data
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get(self, request, *args, **kwargs):
        user = request.user
        order = Order.objects.filter( user=user)
        serializer = OrderViewSerializer(order, many=True)  # Replace with your serializer
        return Response(serializer.data)

class ChangeStatus(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class =OrderSerializer
    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404
    def patch(self, request, pk, format=None):
        order = self.get_object(pk)
        serializer = StatusSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

class ChangeOrderAddress(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404

    def patch(self, request, pk, format=None):
        order = self.get_object(pk)
        user = request.user
        print("User:", user.id)
        
        # Retrieve the user's addresses
        user_addresses = user.shippingaddress_set.all()
        print("User Addresses:", user_addresses)

        # Ensure the selected address belongs to the user
        address_id = request.data.get('address')
        print("Address ID:", address_id)
        
        try:
            address_id = int(address_id)
        except ValueError:
            return Response({'detail': 'Invalid address ID format.'}, status=status.HTTP_400_BAD_REQUEST)

        if address_id not in user_addresses.values_list('id', flat=True):
            print("Invalid Address ID or Unauthorized")
            return Response({'detail': 'Invalid address ID or unauthorized to change this address.'}, status=status.HTTP_400_BAD_REQUEST)
                # Update the order's address
        order.address_id = address_id
        order.save()

        # Return updated order data
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data)
    
class Count(APIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        counts = {
            'Categories': Categories.objects.count(),
            'Sub Categories': SubCategories.objects.count(),
            'Products':Products.objects.count(),
            'Users':CustomUser.objects.count(),
            'OrderItems':OrderItems.objects.count(),
            'Order':Order.objects.count(),
            # Add more counts for other models as needed
        }
        role_choices = CustomUser._meta.get_field('role').choices
        for role, _ in role_choices:
            count = CustomUser.objects.filter(role=role).count()
            counts[role] = count
        return Response(counts)

class UserCount(APIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        counts = {}
        for role, _ in CustomUser.role:
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

class OrderCancelViewSet(viewsets.ModelViewSet):
    queryset = CancelOrder.objects.all()
    serializer_class=OrderCanceledSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class ProfileList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, format=None):
        queryset = UserProfile.objects.all()
        serializer= UserProfileListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)   
    
class ProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    def post(self, request, *args, **kwargs):
        serializer=UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
                return Response({'detail':'your profile is created successfully'}, status=status.HTTP_200_OK)
            except DatabaseError:
                return Response({'detail':'your profile has been already created'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get_object(self):
        try:
            return self.request.user.userprofile
        except ObjectDoesNotExist:
            raise Http404
    def get(self, request, format=None):
        userprofile = self.get_object()
        serializer = UserProfileSerializer(userprofile)
        return Response(serializer.data)
    def patch(self, request, format=None):
        userprofile = self.get_object()
        serializer = UserProfileSerializer(userprofile, partial=True, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':' succesfully updated'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class DeliveryProfileList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, format=None):
        queryset = DeliveryProfile.objects.all()
        serializer= DeliveryProfileSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)   

class DeliverymanProfile(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset=DeliveryProfile.objects.all()
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    def post(self, request, *args, **kwargs):
        serializer=DeliveryProfileSerializer(data=request.data)
        if serializer.is_valid():
            user=request.user
            if user.role=='delivery':
                try:
                    self.perform_create(serializer)
                    return Response({'detail':'your profile is created successfully'}, status=status.HTTP_200_OK)
                except DatabaseError:
                    return Response({'detail':'your profile has been already created'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({'detail':'You have no access to create a profile'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_object(self):
        try:
            return self.request.user.deliveryprofile
        except ObjectDoesNotExist:
            raise Http404
    def get(self, request, format=None):
        profile=self.get_object()
        serializer=DeliveryProfileSerializer(profile)
        return Response(serializer.data)
    def patch(self, request, format=None):
        profile=self.get_object()
        serializer=DeliveryProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()     
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class StoreView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self):
        store = Store.get_instance()
        if not store:
            raise Http404("store credentials do not exist")
        return store
    def get(self, request, *args, **kwargs):
        store = self.get_object()
        serializer = InventorySerializer(store)
        return Response(serializer.data)
    def post(self, request, *args, **kwargs):
        store_exist=Store.objects.first()
        if store_exist:
            return Response({'detail': 'Store already exist, you cant create a new one'})
        serializer=InventorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'Store created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def patch(self, request, *args, **kwargs):
        store = self.get_object()
        serializer = InventorySerializer(store, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'store credentials updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WishListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        wishlist = get_object_or_404(WishList, user=user)
        serializer = GetWishlistSerializer(wishlist)  # Replace with your serializer
        return Response(serializer.data)
    def post(self, request, *args, **kwargs):
        user = request.user
        print(user)
        wishlist = get_object_or_404(WishList, user=user)
        serializer = CreateWishlistSerializer(wishlist)
        product_id = request.data.get('product')
        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        if WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
            WishlistItem.objects.filter(wishlist=wishlist, product=product).delete()
            return Response({'detail':f'you removed {product.name} from your wishlist'})
        else:
            WishlistItem.objects.create(wishlist=wishlist, product=product)
            serializer = CreateWishlistSerializer(wishlist)  # Replace with your serializer
            return Response({'detail':f'you added {product.name} in your wishlist'})
    
class RazorpayView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self):
        razorpay_instance = Razorpay.get_instance()
        if not razorpay_instance:
            raise Http404("Razorpay credentials do not exist")
        return razorpay_instance

    def get(self, request, *args, **kwargs):
        razorpay_instance = self.get_object()
        serializer = RazorpaySerializer(razorpay_instance)
        return Response(serializer.data)
    def post(self, request, *args, **kwargs):
        razorpay_exists =Razorpay.objects.first()
        if razorpay_exists:
            return Response({'detail':'razorpay credentials already exists'})
        serializer= RazorpaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'Razorpay credential created Succesfully'})
        return Response(status=status.HTTP_400_BAD_REQUEST) 
    def patch(self, request, *args, **kwargs):
        razorpay_instance = self.get_object()
        serializer = RazorpaySerializer(razorpay_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Razorpay credentials updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TwilioView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self):
        Twilio_instance = Twilio.get_instance()
        if not Twilio_instance:
            raise Http404("Twilio credentials do not exist")
        return Twilio_instance
    def get(self, request, *args, **kwargs):
        Twilio_instance = self.get_object()
        serializer = TwilioSerializer(Twilio_instance)
        return Response(serializer.data)
    def post(self, request, *args, **kwargs):
        Twilio_exists =Twilio.objects.first()
        if Twilio_exists:
            return Response({'detail':'Twilio credentials already exists'})
        serializer= TwilioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'Twilio credential created Succesfully'})
        return Response(status=status.HTTP_400_BAD_REQUEST) 
    def patch(self, request, *args, **kwargs):
        Twilio_instance = self.get_object()
        serializer = TwilioSerializer(Twilio_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Twilio credentials updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Msg91View(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self):
        Msg91_instance = Msg91.get_instance()
        if not Msg91_instance:
            raise Http404("Msg91 credentials do not exist")
        return Msg91_instance

    def get(self, request, *args, **kwargs):
        Msg91_instance = self.get_object()
        serializer = Msg91Serializer(Msg91_instance)
        return Response(serializer.data)
    def post(self, request, *args, **kwargs):
        Msg91_exists =Msg91.objects.first()
        if Msg91_exists:
            return Response({'detail':'Msg91 credentials already exists'})
        serializer= Msg91Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'Msg91 credential created Succesfully'})
        return Response(status=status.HTTP_400_BAD_REQUEST) 
    def patch(self, request, *args, **kwargs):
        Msg91_instance = self.get_object()
        serializer = Msg91Serializer(Msg91_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Msg91 credentials updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PayTMView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self):
        PayTM_instance = PayTM.get_instance()
        if not PayTM_instance:
            raise Http404("PayTM credentials do not exist")
        return PayTM_instance

    def get(self, request, *args, **kwargs):
        PayTM_instance = self.get_object()
        serializer = PayTMSerializer(PayTM_instance)
        return Response(serializer.data)
    def post(self, request, *args, **kwargs):
        PayTM_exists =PayTM.objects.first()
        if PayTM_exists:
            return Response({'detail':'PayTM credentials already exists'})
        serializer= PayTMSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'PayTM credential created Succesfully'})
        return Response(status=status.HTTP_400_BAD_REQUEST) 
    def patch(self, request, *args, **kwargs):
        PayTM_instance = self.get_object()
        serializer = PayTMSerializer(PayTM_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'PayTM credentials updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class InstaMOJOView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self):
        InstaMOJO_instance = InstaMOJO.get_instance()
        if not InstaMOJO_instance:
            raise Http404("InstaMOJO credentials do not exist")
        return InstaMOJO_instance

    def get(self, request, *args, **kwargs):
        InstaMOJO_instance = self.get_object()
        serializer = InstaMOJOSerializer(InstaMOJO_instance)
        return Response(serializer.data)
    def post(self, request, *args, **kwargs):
        InstaMOJO_exists =InstaMOJO.objects.first()
        if InstaMOJO_exists:
            return Response({'detail':'InstaMOJO credentials already exists'})
        serializer= InstaMOJOSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'InstaMOJO credential created Succesfully'})
        return Response(status=status.HTTP_400_BAD_REQUEST) 
    def patch(self, request, *args, **kwargs):
        InstaMOJO_instance = self.get_object()
        serializer = InstaMOJOSerializer(InstaMOJO_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'InstaMOJO credentials updated '})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ContentView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self):
        Content_instance = Content.get_instance()
        if not Content_instance:
            raise Http404("Content credentials do not exist")
        return Content_instance

    def get(self, request, *args, **kwargs):
        Content_instance = self.get_object()
        serializer = ContentSerializer(Content_instance)
        return Response(serializer.data)
    def post(self, request, *args, **kwargs):
        Content_exists =Content.objects.first()
        if Content_exists:
            return Response({'detail':'Content credentials already exists'})
        serializer= ContentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'Content credential created Succesfully'})
        return Response(status=status.HTTP_400_BAD_REQUEST) 
    def patch(self, request, *args, **kwargs):
        Content_instance = self.get_object()
        serializer = ContentSerializer(Content_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Content credentials updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PageView(APIView):
    authentication_classes = [TokenAuthentication]
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        elif self.request.method in 'POST':
            return [IsAuthenticated()]
    def get(self, request, format=None):
        queryset=Page.objects.all()
        serializer=PageSerializer(queryset, many=True)
        return Response(serializer.data)
    def post(self, request, format=None):
        serializer=PageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PageDetail(APIView):
    authentication_classes = [TokenAuthentication]
    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        elif self.request.method in ['PATCH', 'DELETE']:
            return [IsAuthenticated()]
    def get_object(self, pk):
        try:
            return Page.object.get(pk=pk)
        except Page.DoesNotExist:
            raise Http404
    def get(self, request, pk, format=None):
        page=self.get_object(pk)
        serializer=PageSerializer(page)
        return Response(serializer.data)
    def patch(self, request, pk, format=None):
        page=self.get_object(pk)
        serializer=PageSerializer(page, request=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail':'updted successfully'}, serializer.data)
        return Response(serializer.errors)
    def delete(self, request, pk, format=None):
        page=self.get_object(pk)
        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)