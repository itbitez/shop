from django.db import models
from django.utils.text import slugify
from colorfield.fields import ColorField
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
# Signal to automatically create or update the user profile when the user is created or saved.
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    categories = models.ManyToManyField(Category, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(blank=True, null=True)
    short_description = models.TextField()
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')  # Main product image
    created_at = models.DateTimeField(auto_now_add=True)

    # New Fields
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)
    tags = models.ManyToManyField('Tag', related_name='products', blank=True)
    colors = models.ManyToManyField('Color', related_name='products', blank=True)
    brands = models.ManyToManyField(Brand, related_name='products', blank=True)  # Multiple brand selection

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='gallery_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_gallery/')

    def __str__(self):
        return f"Image for {self.product.name}"


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50)
    color_code = ColorField(default='#FFFFFF')

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    rating = models.IntegerField(default=1)  # Rating out of 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user} for {self.product.name}"


class SiteSettings(models.Model):
    site_title = models.CharField(max_length=255, default='My Website')
    logo = models.ImageField(upload_to='site_settings/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site_settings/', blank=True, null=True)

    def __str__(self):
        return "Site Settings"
    

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    address = models.TextField()
    state = models.CharField(max_length=100)
    postcode = models.IntegerField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    additional_info = models.TextField()
    amount = models.CharField(max_length=100)
    payment_id = models.CharField(max_length=200, null=True, blank=True)
    paid = models.BooleanField(default=False, null=True)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.CharField(max_length=200)
    image = models.ImageField(upload_to='products/')
    quantity = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
    total = models.CharField(max_length=1000)

    def __str__(self):
        return self.order.user.username
