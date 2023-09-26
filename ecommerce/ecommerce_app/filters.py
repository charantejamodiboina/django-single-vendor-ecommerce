import django_filters
from .models import*

class ProductsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    brand = django_filters.CharFilter(lookup_expr='exact')
    subcategories_id = django_filters.NumberFilter(lookup_expr='exact')  
    class Meta:
        model = Products
        fields = ['name', 'price', 'brand', 'subcategories_id']

class ProductVariantFilter(django_filters.FilterSet):
    variant_name = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = ProductVariant
        fields = ['variant_name']

class ProductDetailsFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = ProductDetails
        fields = ['title']

class ProductQuestionsFilter(django_filters.FilterSet):
    question = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ProductQuestions
        fields = ['question']

class ProductReviewsFilter(django_filters.FilterSet):
    rating = django_filters.NumberFilter(lookup_expr='exact')
    class Meta:
        model = ProductReviews
        fields = ['rating']