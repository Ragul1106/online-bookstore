from django.contrib import admin
from django.utils.html import format_html
from .models import Author, Book, Category
from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'book_count', 'photo_preview']
    search_fields = ['name']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at', 'photo_preview']
    
    def book_count(self, obj):
        return obj.books.count()
    book_count.short_description = 'Number of Books'
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 50%;" />', obj.photo.url)
        return "No Photo"
    photo_preview.short_description = 'Photo Preview'

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'price', 'stock_quantity', 'cover_preview', 'created_at']
    list_filter = ['author', 'categories', 'created_at']
    search_fields = ['title', 'author__name', 'isbn']
    filter_horizontal = ['categories']
    readonly_fields = ['created_at', 'updated_at', 'cover_preview']
    
    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.cover_image.url)
        return "No Cover"
    cover_preview.short_description = 'Cover Preview'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'isbn', 'publication_date')
        }),
        ('Images', {
            'fields': ('cover_image', 'cover_preview')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock_quantity')
        }),
        ('Categories', {
            'fields': ('categories',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'book_count']
    search_fields = ['name']
    
    def book_count(self, obj):
        return obj.books.count()
    book_count.short_description = 'Number of Books'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer_name', 'email', 'total_amount', 
        'status_badge', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'country']
    search_fields = ['email', 'first_name', 'last_name', 'id']
    readonly_fields = ['created_at', 'updated_at']
    
    def customer_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    customer_name.short_description = 'Customer'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'processing': 'blue', 
            'shipped': 'green',
            'delivered': 'success',
            'cancelled': 'red'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} orders marked as processing.')
    mark_as_processing.short_description = "Mark selected orders as processing"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_as_shipped.short_description = "Mark selected orders as shipped"
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_as_delivered.short_description = "Mark selected orders as delivered"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'book_title', 'quantity', 'price', 'subtotal']
    list_filter = ['order__status', 'order__created_at']
    
    def order_id(self, obj):
        return obj.order.id
    order_id.short_description = 'Order #'
    
    def book_title(self, obj):
        return obj.book.title
    book_title.short_description = 'Book'
