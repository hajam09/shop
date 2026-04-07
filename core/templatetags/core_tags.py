from django import template
from django.core.paginator import Page
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def cartItemCount(request):
    from django.db.models import Sum

    from checkout.models import Cart, CartItem

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, isCheckedOut=False).first()
        if not cart:
            return 0
        return CartItem.objects.filter(cart=cart).aggregate(q=Sum('quantity'))['q'] or 0

    if not request.session.session_key:
        return 0
    cart = Cart.objects.filter(sessionKey=request.session.session_key, isCheckedOut=False).first()
    if not cart:
        return 0
    return CartItem.objects.filter(cart=cart).aggregate(q=Sum('quantity'))['q'] or 0


@register.simple_tag
def wishlistItemCount(request):
    from django.db.models import Count

    from accounts.models import Wishlist, WishlistItem

    if not request.user.is_authenticated:
        return 0
    wishlist = Wishlist.objects.filter(user=request.user, isDefault=True).first()
    if not wishlist:
        return 0
    return WishlistItem.objects.filter(wishlist=wishlist).aggregate(c=Count('id'))['c'] or 0


@register.simple_tag
def paginationComponent(request, objects: Page):
    if not objects.has_other_pages():
        return mark_safe('<span></span>')

    # Preserve current querystring (except page) so pagination keeps filters like ?q=...
    params = request.GET.copy()
    params.pop('page', None)
    query = f"&{params.urlencode()}" if params else ''

    if objects.has_previous():
        href = f'?page={objects.previous_page_number()}{query}'
        previousPageLink = f'''
        <li class="page-item">
            <a class="page-link" href="{href}" tabindex="-1">Previous</a>
        </li>
        '''
        firstPageLink = f'''
        <li class="page-item">
            <a class="page-link" href="?page=1{query}" tabindex="-1">First</a>
        </li>
        '''

    else:
        previousPageLink = f'''
        <li class="page-item disabled">
            <a class="page-link" href="#" tabindex="-1">Previous</a>
        </li>
        '''
        firstPageLink = f'''
        <li class="page-item disabled">
            <a class="page-link" href="?page=1{query}" tabindex="-1">First</a>
        </li>
        '''

    if objects.has_next():
        href = f'?page={objects.next_page_number()}{query}'
        nextPageLink = f'''
        <li class="page-item">
            <a class="page-link" href="{href}" tabindex="-1">Next</a>
        </li>
        '''
        lastPageLink = f'''
        <li class="page-item">
            <a class="page-link" href="?page={objects.paginator.num_pages}{query}" tabindex="-1">Last</a>
        </li>
        '''

    else:
        nextPageLink = f'''
        <li class="page-item disabled">
            <a class="page-link" href="#" tabindex="-1">Next</a>
        </li>
        '''
        lastPageLink = f'''
        <li class="page-item disabled">
            <a class="page-link" href="?page={objects.paginator.num_pages}{query}" tabindex="-1">Last</a>
        </li>
        '''

    pageNumberLinks = ''
    EITHER_SIDE_PAGE_LIMIT = 20
    pageRange = objects.paginator.page_range
    if pageRange.stop > EITHER_SIDE_PAGE_LIMIT:
        currentPage = int(request.GET.get('page') or 1)
        minRange = currentPage - EITHER_SIDE_PAGE_LIMIT // 2
        maxRange = currentPage + EITHER_SIDE_PAGE_LIMIT // 2

        if minRange <= 0:
            minRange = 1
        if maxRange > pageRange.stop:
            maxRange = pageRange.stop

        pageRange = range(minRange, maxRange)

    for pageNumber in pageRange:
        if objects.number == pageNumber:
            pageNumberLinks += f'''
                <li class="page-item active"><a class="page-link" href="#">{pageNumber}</a></li>
            '''
        else:
            href = f"?page={pageNumber}{query}"
            pageNumberLinks += f'''
                <li class="page-item"><a class="page-link" href="{href}">{pageNumber}</a></li>
            '''

    itemContent = f'''
    <div class="row">
        <div class="col-md-12" style="width: 1100px;">
            <nav aria-label="Page navigation example">
                <ul class="pagination justify-content-center">
                    {firstPageLink}
                    {previousPageLink}
                    {pageNumberLinks}
                    {nextPageLink}
                    {lastPageLink}
                </ul>
            </nav>
        </div>
    </div>
    '''
    return mark_safe(itemContent)
