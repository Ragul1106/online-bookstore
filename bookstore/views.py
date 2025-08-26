from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Author, Book, Category, Cart, CartItem, OrderItem, Order
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

def book_list(request):
    books = Book.objects.select_related('author').prefetch_related('categories')
    categories = Category.objects.all()
    authors = Author.objects.all()

    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) | 
            Q(author__name__icontains=search_query)
        )

    category_filter = request.GET.get('category', '')
    if category_filter:
        books = books.filter(categories__id=category_filter)

    author_filter = request.GET.get('author', '')
    if author_filter:
        books = books.filter(author__id=author_filter)
    
    context = {
        'books': books,
        'categories': categories,
        'authors': authors,
        'search_query': search_query,
        'selected_category': category_filter,
        'selected_author': author_filter,
    }
    return render(request, 'bookstore/book_list.html', context)

def author_detail(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    books = author.books.all()
    return render(request, 'bookstore/author_detail.html', {
        'author': author,
        'books': books
    })

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    books = category.books.all()
    return render(request, 'bookstore/category_detail.html', {
        'category': category,
        'books': books
    })

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'bookstore/book_detail.html', {
        'book': book
    })

def author_list(request):
    authors = Author.objects.all().order_by('name')
    return render(request, 'bookstore/author_list.html', {
        'authors': authors
    })

def category_list(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'bookstore/category_list.html', {
        'categories': categories
    })

def get_or_create_cart(request):
    """Get or create cart for user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

@require_POST
def add_to_cart(request, book_id):
    """Add book to cart"""
    book = get_object_or_404(Book, id=book_id)
    cart = get_or_create_cart(request)

    if book.stock_quantity <= 0:
        messages.error(request, f"{book.title} is out of stock!")
        return redirect('book_list')

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        book=book,
        defaults={'quantity': 1}
    )
    
    if not created:
        if cart_item.quantity + 1 > book.stock_quantity:
            messages.warning(request, f"Cannot add more {book.title}. Only {book.stock_quantity} in stock!")
        else:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Added another {book.title} to cart!")
    else:
        messages.success(request, f"{book.title} added to cart!")
    
    return redirect('book_list')

def view_cart(request):
    """Display cart contents"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'bookstore/cart.html', context)

@require_POST
def update_cart(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        if quantity <= cart_item.book.stock_quantity:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f"Updated {cart_item.book.title} quantity!")
        else:
            messages.error(request, f"Only {cart_item.book.stock_quantity} {cart_item.book.title} in stock!")
    else:
        cart_item.delete()
        messages.success(request, f"Removed {cart_item.book.title} from cart!")
    
    return redirect('view_cart')

@require_POST
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    book_title = cart_item.book.title
    cart_item.delete()
    messages.success(request, f"Removed {book_title} from cart!")
    return redirect('view_cart')

def checkout(request):
    """Checkout process - collect shipping info"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.warning(request, "Your cart is empty!")
        return redirect('book_list')
    
    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key if not request.user.is_authenticated else None,
            email=request.POST.get('email'),
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            postal_code=request.POST.get('postal_code'),
            country=request.POST.get('country', 'India'),
            total_amount=cart.total_price
        )
        
        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                book=item.book,
                quantity=item.quantity,
                price=item.book.price
            )
        
        # Store order ID in session for payment
        request.session['order_id'] = order.id
        
        return redirect('payment', order_id=order.id)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'bookstore/checkout.html', context)

def payment(request, order_id):
    """Payment processing page"""
    order = get_object_or_404(Order, id=order_id)
    
    context = {
        'order': order,
    }
    return render(request, 'bookstore/payment.html', context)

def order_success(request, order_id):
    """Order success page"""
    order = get_object_or_404(Order, id=order_id)
    

    cart = get_or_create_cart(request)
    cart.items.all().delete()

    for item in order.items.all():
        book = item.book
        book.stock_quantity -= item.quantity
        book.save()
    
    context = {
        'order': order,
    }
    return render(request, 'bookstore/order_success.html', context)

@staff_member_required
def order_management(request):
    """Staff order management dashboard"""
    orders = Order.objects.all().order_by('-created_at')
    
    context = {
        'orders': orders,
        'pending_count': orders.filter(status='pending').count(),
        'processing_count': orders.filter(status='processing').count(),
        'shipped_count': orders.filter(status='shipped').count(),
    }
    return render(request, 'bookstore/order_management.html', context)

@staff_member_required
def update_order_status(request, order_id):
    """Update order status"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {order.get_status_display()}')
    
    return redirect('order_management')

