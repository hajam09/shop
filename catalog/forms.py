from django import forms
from django.utils.text import slugify

from catalog.models import Category
from catalog.utils import category_descendant_pks


class CategoryForm(forms.ModelForm):
    slug = forms.SlugField(
        max_length=160,
        required=False,
        help_text='Leave blank to generate from the name.',
    )

    class Meta:
        model = Category
        fields = ('name', 'slug', 'parent', 'description', 'isActive', 'sortOrder')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        parent_qs = Category.objects.select_related(
            'parent',
            'parent__parent',
            'parent__parent__parent',
            'parent__parent__parent__parent',
            'parent__parent__parent__parent__parent',
        ).order_by('sortOrder', 'name')
        if self.instance.pk:
            forbidden = {self.instance.pk} | category_descendant_pks(self.instance.pk)
            parent_qs = parent_qs.exclude(pk__in=forbidden)
        self.fields['parent'].queryset = parent_qs
        self.fields['parent'].required = False
        self.fields['parent'].empty_label = '— Top level —'
        self.fields['parent'].label_from_instance = lambda obj: obj.get_full_path()
        self.fields['parent'].widget.attrs.setdefault('class', 'form-select')
        for name in ('name', 'slug', 'description', 'sortOrder'):
            if name in self.fields:
                self.fields[name].widget.attrs.setdefault('class', 'form-control')
        if 'isActive' in self.fields:
            self.fields['isActive'].widget.attrs.setdefault('class', 'form-check-input')

    def clean_parent(self):
        parent = self.cleaned_data.get('parent')
        instance = self.instance
        if not parent:
            return parent
        if not instance.pk:
            return parent
        if parent.pk == instance.pk:
            raise forms.ValidationError('A category cannot be its own parent.')
        if parent.pk in category_descendant_pks(instance.pk):
            raise forms.ValidationError('A category cannot be parented under one of its descendants.')
        return parent

    def _unique_slug(self, base: str) -> str:
        slug = base
        n = 2
        qs = Category.objects.all()
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        while qs.filter(slug=slug).exists():
            slug = f'{base}-{n}'
            n += 1
        return slug

    def save(self, commit=True):
        instance = super().save(commit=False)
        name = instance.name or ''
        base = slugify(name) or 'category' if not instance.slug else instance.slug
        instance.slug = self._unique_slug(base)
        if commit:
            instance.save()
            self.save_m2m()
        return instance
