from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from storages.backends.s3boto3 import S3Boto3Storage

class Category(models.Model):
    category = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.category

class Books(models.Model):
    ISBN = models.CharField(max_length=70, null=True)
    Book_Title = models.CharField(max_length=255, null=True)
    Book_Author = models.CharField(max_length=255, null=True)
    Description = models.TextField(null=True)
    Year_Of_Publication = models.CharField(max_length=4, null=True)  # Restricted to 4 characters for year
    Publisher = models.CharField(max_length=255, null=True)
    Image_URL = models.URLField(max_length=255, null=True)  # Changed to URLField
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)


    def __str__(self):
        return self.ISBN

    def save(self, *args, **kwargs):
        # Automatically generate slug from Book_Title if not provided
        if not self.slug:
            self.slug = slugify(self.Book_Title)
        super(Books, self).save(*args, **kwargs)

class About(models.Model):
    About_text = models.TextField(max_length=1250, null=True)

    def save(self, *args, **kwargs):
        # Check if an instance already exists
        if About.objects.exists() and not self.pk:
            raise ValidationError("Only one instance of About can exist.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.About_text

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, null=True, blank=True)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

class CustomUser(AbstractUser):
    age = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    image_url = models.ImageField(upload_to='profile_images/' , storage=S3Boto3Storage(),null=True, blank=True)

    # Override related_name to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',  # Custom related_name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',  # Custom related_name
        blank=True
    )

class Rating(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)  # Make sure this is an integer field

    def save(self, *args, **kwargs):
        if self.rating < 0 or self.rating > 10:
            raise ValueError("Rating must be between 0 and 10.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} rated {self.book.ISBN} - {self.rating}"


class CartItem(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
     return f'{self.book.Book_Title} book order by {self.user.username}'
    


class OrderPlaced(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey('Books', on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    date_ordered = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered')
    ], default='Pending')

    def __str__(self):
        return f'Order {self.id} for {self.product.Book_Title} by {self.user.username}'


class ShippingInfo(models.Model):
    order = models.OneToOneField(OrderPlaced, on_delete=models.CASCADE)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"Shipping Info for Order {self.order.id}"
    


