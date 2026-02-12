from django.urls import path
from .views import GlobalSearchView, CategoryListView, HomeFixedDataView, SiteConfigView,ProductListView,ProductDetailView,ReviewListCreateView,WatchBuyListView

urlpatterns = [
    path('search/', GlobalSearchView.as_view(), name='global-search'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('home-data/', HomeFixedDataView.as_view(), name='home-data'),
    path('config/', SiteConfigView.as_view(), name='site-config'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    # 🔥 THE FIX: Add this line for reviews
    path('products/<slug:slug>/reviews/', ReviewListCreateView.as_view(), name='product-reviews'),
    path('watch-buy/', WatchBuyListView.as_view(), name='watch-buy-list'),
]