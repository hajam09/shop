from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from catalog.forms import CategoryForm
from catalog.models import Category, Product, ProductImage
from checkout.models import Cart, CartItem


def _build_category_tree(categories):
    """Group categories by parent and attach .tree_children to each node; return roots."""
    by_parent = {}
    for c in categories:
        by_parent.setdefault(c.parent_id, []).append(c)
    for lst in by_parent.values():
        lst.sort(key=lambda x: (x.sortOrder, x.name.lower()))

    def attach(node):
        node.tree_children = by_parent.get(node.pk, [])
        for ch in node.tree_children:
            attach(ch)

    roots = by_parent.get(None, [])
    for r in roots:
        attach(r)
    return roots


def productView(request):
    pass


def productImageView(request):
    pass


def _get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user, isCheckedOut=False)
        return cart

    if not request.session.session_key:
        request.session.create()
    cart, _ = Cart.objects.get_or_create(sessionKey=request.session.session_key, isCheckedOut=False)
    return cart


def productSearchView(request):
    q = (request.GET.get('q') or '').strip()
    qs = (
        Product.objects.select_related('seller')
        .prefetch_related(
            Prefetch(
                'productImages',
                queryset=ProductImage.objects.order_by('-isPrimary', 'order', 'createdAt'),
            )
        )
        .filter(isActive=True)
    )

    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(brand__icontains=q)
            | Q(category__icontains=q)
            | Q(description__icontains=q)
            | Q(sku__icontains=q)
        )

    qs = qs.order_by('-isFeatured', '-createdAt')
    paginator = Paginator(qs, 24)
    page_obj = paginator.get_page(request.GET.get('page') or 1)
    products = list(page_obj.object_list)

    for p in products:
        imgs = list(getattr(p, 'productImages', []).all())
        primary = imgs[0] if imgs else None
        # ProductImage.getImage returns a dummy URL if needed.
        p.primaryImageUrl = primary.getImage if primary else 'https://dummyimage.com/1080x1080/'

    return render(
        request,
        'catalog/product_search.html',
        {
            'q': q,
            'page_obj': page_obj,
            'products': products,
            'total_count': paginator.count,
        },
    )


def productDetailView(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('seller').prefetch_related(
            Prefetch(
                'productImages',
                queryset=ProductImage.objects.order_by('-isPrimary', 'order', 'createdAt'),
            ),
            'variants',
        ),
        slug=slug,
        isActive=True,
    )

    images = list(product.productImages.all())
    primary_image = images[0] if images else None
    primary_image_url = primary_image.getImage if primary_image else 'https://dummyimage.com/1080x1080/'

    variants = [v for v in product.variants.all() if v.isActive]
    has_variants = bool(variants)

    related = (
        Product.objects.filter(isActive=True)
        .exclude(pk=product.pk)
        .filter(Q(category=product.category) | Q(brand=product.brand))
        .order_by('-isFeatured', '-createdAt')[:6]
    )

    return render(
        request,
        'catalog/product_detail.html',
        {
            'product': product,
            'images': images,
            'primary_image_url': primary_image_url,
            'variants': variants,
            'has_variants': has_variants,
            'related_products': related,
        },
    )


def addToCartView(request, slug):
    if request.method != 'POST':
        return redirect('catalog:product-detail', slug=slug)

    product = get_object_or_404(Product, slug=slug, isActive=True)
    variants = list(product.variants.filter(isActive=True))

    variant_id = (request.POST.get('variant') or '').strip()
    variant = None
    if variant_id:
        variant = get_object_or_404(product.variants, pk=variant_id, isActive=True)

    if variants and not variant:
        messages.error(request, 'Please select a variant.')
        return redirect('catalog:product-detail', slug=slug)

    try:
        quantity = int(request.POST.get('quantity') or 1)
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(1, min(quantity, 999))

    unit_price = variant.price if (variant and variant.price is not None) else product.price
    cart = _get_or_create_cart(request)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={
            'quantity': quantity,
            'unitPrice': unit_price,
            'lineTotal': unit_price * quantity,
        },
    )
    if not created:
        item.quantity = min(999, item.quantity + quantity)
        item.unitPrice = unit_price
        item.lineTotal = unit_price * item.quantity
        item.save(update_fields=['quantity', 'unitPrice', 'lineTotal'])

    messages.success(request, 'Added to cart.')
    return redirect('catalog:product-detail', slug=slug)


def categoryView(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created.')
            return redirect('catalog:category-view')
    else:
        form = CategoryForm()

    # Enough depth for typical trees; deeper chains add extra queries per hop.
    categories = Category.objects.all().select_related(
        'parent',
        'parent__parent',
        'parent__parent__parent',
        'parent__parent__parent__parent',
        'parent__parent__parent__parent__parent',
    )
    categories = list(categories)
    category_roots = _build_category_tree(categories)

    return render(
        request,
        'catalog/category-view.html',
        {
            'form': form,
            'category_roots': category_roots,
        },
    )


def categoryEditView(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated.')
            return redirect('catalog:category-view')
    else:
        form = CategoryForm(instance=category)

    return render(
        request,
        'catalog/category_edit.html',
        {
            'form': form,
            'category': category,
        },
    )


def categoryDeleteView(request, pk):
    category = get_object_or_404(Category, pk=pk)
    sub_count = category.subcategories.count()
    product_link_count = category.categoryProducts.count()

    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category “{name}” was deleted.')
        return redirect('catalog:category-view')

    return render(
        request,
        'catalog/category_confirm_delete.html',
        {
            'category': category,
            'sub_count': sub_count,
            'product_link_count': product_link_count,
        },
    )
