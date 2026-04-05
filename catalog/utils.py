from catalog.models import Category


def category_descendant_pks(root_pk):
    """Return primary keys of all descendants of root_pk (not including root_pk)."""
    found = set()
    frontier = list(Category.objects.filter(parent_id=root_pk).values_list('pk', flat=True))
    while frontier:
        pk = frontier.pop()
        if pk in found:
            continue
        found.add(pk)
        frontier.extend(Category.objects.filter(parent_id=pk).values_list('pk', flat=True))
    return found
