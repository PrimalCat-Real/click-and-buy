from django.contrib import admin
from .models import UserProfile, Category, Product, Order, OrderItem, BonusTransaction, Review
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_bonus_points')
    list_select_related = ('profile',)

    def get_bonus_points(self, instance):
        try:
            return instance.profile.bonus_points
        except UserProfile.DoesNotExist:
            return None
    get_bonus_points.short_description = 'Bonus Points'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'price', 'stock', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated', 'category']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    raw_id_fields = ['category']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 1
    readonly_fields = ('price_at_purchase', 'get_cost_display')

    def get_cost_display(self, instance):
        return instance.get_cost()
    get_cost_display.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_display', 'first_name', 'last_name', 'email', 'phone', 'delivery_option', 'status', 'paid', 'created_at', 'total_amount']
    list_filter = ['paid', 'created_at', 'updated_at', 'status', 'delivery_option']
    search_fields = ['id', 'first_name', 'last_name', 'email', 'phone']
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at', 'user', 'total_amount', 'bonus_points_earned', 'bonus_points_used')

    def user_display(self, obj):
        return obj.user.username if obj.user else "Guest"
    user_display.short_description = "Customer"

@admin.register(BonusTransaction)
class BonusTransactionAdmin(admin.ModelAdmin):
    list_display = ['user_profile_link', 'order_link', 'points', 'transaction_type', 'reason', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['user_profile__user__username', 'order__id', 'reason']
    list_select_related = ('user_profile__user', 'order')

    def user_profile_link(self, obj):
        if obj.user_profile and obj.user_profile.user:
            link = reverse("admin:auth_user_change", args=[obj.user_profile.user.id])
            return format_html('<a href="{}">{}</a>', link, obj.user_profile.user.username)
        return "-"
    user_profile_link.short_description = 'User'

    def order_link(self, obj):
        if obj.order:
            link = reverse("admin:store_order_change", args=[obj.order.id])
            return format_html('<a href="{}">Order #{}</a>', link, obj.order.id)
        return "-"
    order_link.short_description = 'Order'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at', 'is_approved']
    list_filter = ['is_approved', 'created_at', 'rating']
    search_fields = ['user__username', 'product__name', 'text']
    actions = ['approve_reviews_action', 'disapprove_reviews_action']

    def approve_reviews_action(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews_action.short_description = "Approve selected reviews"

    def disapprove_reviews_action(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_reviews_action.short_description = "Disapprove selected reviews"