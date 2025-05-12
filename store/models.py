from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bonus_points = models.PositiveIntegerField(default=0, verbose_name="Bonus Points")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone Number")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name="Category Name")
    slug = models.SlugField(max_length=200, unique=True, blank=True, help_text="Automatically generated from the name if left blank.")
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        ordering = ('name',)
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name="Category")
    name = models.CharField(max_length=200, db_index=True, verbose_name="Product Name")
    slug = models.SlugField(max_length=200, db_index=True, unique=True, blank=True, help_text="Automatically generated from the name if left blank.")
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, verbose_name="Image")
    description = models.TextField(blank=True, verbose_name="Description")
    characteristics = models.TextField(blank=True, verbose_name="Characteristics")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock Quantity")
    available = models.BooleanField(default=True, verbose_name="Available for Order")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    updated = models.DateTimeField(auto_now=True, verbose_name="Date Updated")

    class Meta:
        ordering = ('name',)
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Order(models.Model):
    DELIVERY_CHOICES = [
        ('pickup', 'Pickup Point'),
        ('nova_poshta', 'Nova Poshta'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, related_name='orders', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="User")
    first_name = models.CharField(max_length=50, verbose_name="First Name")
    last_name = models.CharField(max_length=50, verbose_name="Last Name")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Phone")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date Updated")
    delivery_option = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='nova_poshta', verbose_name="Delivery Option")
    delivery_address_details = models.TextField(verbose_name="Address/NP Branch/Pickup Point")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Amount")
    bonus_points_used = models.PositiveIntegerField(default=0, verbose_name="Bonus Points Used")
    bonus_points_earned = models.PositiveIntegerField(default=0, verbose_name="Bonus Points Earned")
    paid = models.BooleanField(default=False, verbose_name="Paid")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Order Status")

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f'Order {self.id} by {self.first_name} {self.last_name}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Order")
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.PROTECT, verbose_name="Product")
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price at Purchase")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f'{self.quantity} x {self.product.name} in order {self.order.id}'

    def get_cost(self):
        return self.price_at_purchase * self.quantity

class BonusTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('earn', 'Earned'),
        ('spend', 'Spent'),
    ]
    user_profile = models.ForeignKey(UserProfile, related_name='bonus_transactions', on_delete=models.CASCADE, verbose_name="User Profile")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Related Order")
    points = models.IntegerField(verbose_name="Points Amount")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, verbose_name="Transaction Type")
    reason = models.CharField(max_length=255, blank=True, verbose_name="Reason/Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Transaction Date")

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Bonus Points Transaction'
        verbose_name_plural = 'Bonus Points Transactions'

    def __str__(self):
        return f'{self.get_transaction_type_display()} {self.points} points for {self.user_profile.user.username}'

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE, verbose_name="Product")
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE, verbose_name="User")
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Rating (1-5)")
    text = models.TextField(verbose_name="Review Text")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    is_approved = models.BooleanField(default=False, verbose_name="Approved by Moderator")

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ('product', 'user')

    def __str__(self):
        return f'Review by {self.user.username} for {self.product.name} (Rating: {self.rating})'