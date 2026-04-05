from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from catalog.forms import CategoryForm
from catalog.models import Category


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
