from django.db import models  # Fixed the 'import db' error here

class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class HeroSlide(models.Model):
    # Help text provides the note for the admin panel
    image = models.ImageField(
        upload_to='hero_slides/', 
        help_text="Recommended Ratios: 21:8 for Desktop (e.g., 2100x800px) and 3:2 for Mobile (e.g., 1200x800px). Ensure titles are part of the image."
    )
    link_url = models.CharField(
        max_length=255, 
        default="/category/all", 
        help_text="The internal route the user goes to (e.g., /category/sarees or /category/all)"
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Hero Slide {self.order} - {self.link_url}"

    
class BrandStorySettings(SingletonModel):
    tagline = models.CharField(max_length=100, default="The Art of Draping")
    # This field now controls both styled lines
    heading = models.CharField(
        max_length=255, 
        default="Traditional Elegance | Effortlessly Styled",
        help_text="Line 1 and Line 2 are separated by '|'. Line 2 will automatically be Pink and Italic."
    )
    content = models.TextField(
        help_text="The main description (rendered in italics)", 
        default="Every design is a tribute to the timeless beauty of the Indian woman."
    )
    experience_years = models.IntegerField(default=5)

    def __str__(self):
        return "Global Brand Story Settings"
    
class BrandStoryImage(models.Model):
    # This allows multiple images for the BrandStory slider
    settings = models.ForeignKey(BrandStorySettings, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='brand_story/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

class Announcement(models.Model):
    message = models.CharField(max_length=255, help_text="Text for the top scrolling bar")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.message