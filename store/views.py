from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.db.models import Q
from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from decimal import Decimal
from django.utils import timezone
from rest_framework import status

class GlobalSearchView(APIView):
    def get(self, request):
        q = request.query_params.get('q', '')
        if len(q) < 2:
            return Response({"products": [], "categories": []})
            
        products = Product.objects.filter(
            Q(title__icontains=q) | Q(sku__icontains=q) | Q(category__name__icontains=q)
        ).distinct()[:10]
        categories = Category.objects.filter(name__icontains=q)[:5]
        
        return Response({
            "products": ProductSerializer(products, many=True, context={'request': request}).data,
            "categories": CategorySerializer(categories, many=True, context={'request': request}).data
        })

class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

class HomeFixedDataView(APIView):
    """View providing data for New Arrivals and Best Sellers"""
    def get(self, request):
        return Response({
            "new_arrivals": ProductSerializer(Product.objects.filter(is_new_arrival=True), many=True, context={'request': request}).data,
            "best_sellers": ProductSerializer(Product.objects.filter(is_best_seller=True), many=True, context={'request': request}).data,
        })

# store/views.py
class SiteConfigView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        config = SiteConfig.objects.first()
        if not config:
            # Create a default if it doesn't exist yet
            config = SiteConfig.objects.create()
        
        serializer = SiteConfigSerializer(config)
        return Response(serializer.data)
    
class WatchBuyListView(APIView):
    def get(self, request):
        # Fetches WatchAndBuy model objects which contain the video and product link
        items = WatchAndBuy.objects.filter(is_active=True)
        data = []
        for item in items:
            data.append({
                "id": item.id,
                "video_url": item.video.url,
                "product_slug": item.product.slug,
                "name": item.product.title,
                "price": item.product.price,
                "category": item.product.category.name
            })
        return Response(data)
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all().prefetch_related('images', 'variants')
        
        # 1. Get all possible query parameters
        category_slug = self.request.query_params.get('category')
        is_best_seller = self.request.query_params.get('is_best_seller')
        is_new_arrival = self.request.query_params.get('is_new_arrival')
        is_lehenga = self.request.query_params.get('is_featured_lehenga')
        is_saree = self.request.query_params.get('is_saree_collection')
        is_kids = self.request.query_params.get('is_kids_collection')
        is_watch_buy = self.request.query_params.get('is_watch_and_buy')

        # 2. Priority Filtering: Check if we are looking for a "Ticked" Collection first
        if is_lehenga == 'true':
            return queryset.filter(is_featured_lehenga=True).order_by('-id')
        
        if is_saree == 'true':
            return queryset.filter(is_saree_collection=True).order_by('-id')
            
        if is_kids == 'true':
            return queryset.filter(is_kids_collection=True).order_by('-id')
        elif is_watch_buy == 'true':
            queryset = queryset.filter(is_watch_and_buy=True)
        if is_best_seller == 'true':
            return queryset.filter(is_best_seller=True).order_by('-id')
            
        if is_new_arrival == 'true':
            return queryset.filter(is_new_arrival=True).order_by('-id')

        # 3. Fallback: Filter by Category Slug (for the navbar links)
        if category_slug and category_slug != 'all':
            queryset = queryset.filter(category__slug=category_slug)
            
        return queryset.order_by('-id')
    
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # 🔥 THE FIX: Tell Django to use the slug field for lookups
    lookup_field = 'slug'

    


        
class ReviewListCreateView(generics.ListCreateAPIView): # 🔥 Support both GET and POST
    serializer_class = ReviewSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
            return Review.objects.filter(product__slug=self.kwargs['slug']).order_by('-created_at')
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
    def perform_create(self, serializer):
        product = Product.objects.get(slug=self.kwargs['slug'])
        serializer.save(product=product)

class ValidateCouponView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        code = request.data.get('code', '').strip().upper()
        # Convert to string first to avoid float issues in Decimal
        order_total = Decimal(str(request.data.get('order_total', 0)))
        
        if not code:
            return Response({'error': 'Coupon code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            coupon = Coupon.objects.get(code=code, active=True)
            now = timezone.now() # ✅ Now this will work
            
            # Check expiry
            if coupon.valid_from > now or coupon.valid_to < now:
                return Response({'error': 'Coupon has expired'}, status=status.HTTP_400_BAD_REQUEST)
            if coupon.uses_count >= coupon.usage_limit:
                return Response({'error': 'Coupon usage limit reached'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check min order value
            if order_total < coupon.min_order_value:
                return Response({
                    'error': f'Minimum order value of ₹{coupon.min_order_value} required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Calculate discount
            discount = 0
            if coupon.discount_type == 'percentage':
                discount = (order_total * coupon.value) / 100
            else:
                discount = coupon.value
            
            return Response({
                'success': True,
                'discount': float(discount),
                'code': coupon.code,
                'message': f'Coupon {code} applied successfully!'
            }, status=status.HTTP_200_OK)
            
        except Coupon.DoesNotExist:
            return Response({'error': 'Invalid coupon code'}, status=status.HTTP_404_NOT_FOUND)