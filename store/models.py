from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_navbar_visible = models.BooleanField(default=False, help_text="Show on Desktop Navbar")
    is_featured = models.BooleanField(default=False, help_text="Show in Category Circles")

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class Color(models.Model):
    name = models.CharField(max_length=50) # e.g., "Ruby Red"
    hex_code = models.CharField(max_length=7, help_text="#FFFFFF")
    def __str__(self): return self.name

class Size(models.Model):
    name = models.CharField(max_length=10) # e.g., "S", "XL", "38"
    def __str__(self): return self.name

class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, help_text="GTD-SR-01")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Professional details
    description = models.TextField(blank=True, null=True)
    features = models.TextField(
        blank=True, 
        null=True, 
        help_text="Separate features by new lines (Optional)"
    )
    care_instructions = models.TextField(
        blank=True, 
        null=True, 
        help_text="Separate instructions by new lines (Optional)"
    )
    
    # Homepage Toggles
    is_new_arrival = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)

    is_featured_lehenga = models.BooleanField(default=False, verbose_name="In Featured Lehengas")
    is_saree_collection = models.BooleanField(default=False, verbose_name="In Sarees Collection")
    is_kids_collection = models.BooleanField(default=False, verbose_name="In Kids Collection")
    is_watch_and_buy = models.BooleanField(default=False) # 🔥 Added
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sku} - {self.title}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='products/')
    video = models.FileField(upload_to='videos/products/', null=True, blank=True) # 🔥 Added

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)
    price_override = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Extra amount to add to base prices (e.g., 200 for L size)"
    )
    
    def __str__(self):
        return f"{self.product.title} - {self.color.name} - {self.size.name}"

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    image = models.ImageField(upload_to='reviews/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SiteConfig(models.Model):
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=1999.00)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

