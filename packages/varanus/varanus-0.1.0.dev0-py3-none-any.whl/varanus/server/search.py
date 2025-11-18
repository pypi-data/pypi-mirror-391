from typing import ClassVar

from django import forms
from django.db import models


class SearchField:
    form_class: ClassVar[type] = forms.Form

    def __init__(self, field_name=None):
        self.name = None
        self.field_name = field_name or ""
        self.prefix = f"{self.field_name}_" if self.field_name else ""

    def __set_name__(self, owner, name):
        # print("__set_name__", owner, name)
        assert issubclass(owner, Search)
        self.name = name
        if not self.field_name:
            self.field_name = name
            self.prefix = f"{self.field_name}_"
        owner.fields.append(self)

    def __get__(self, instance, owner=None):
        # print("__get__", instance, owner)
        if owner is None:
            return self

    def __set__(self, instance, value):
        print("__set__", instance, value)

    def formfields(self, queryset=None):
        raise NotImplementedError()

    def clean(self, raw_data):
        cleaned_data = {}
        for name, field in self.formfields():
            raw_value = field.widget.value_from_datadict(
                raw_data, None, f"{self.prefix}{name}"
            )
            try:
                cleaned_data[name] = field.to_python(raw_value)
            except forms.ValidationError:
                cleaned_data[name] = None
        return cleaned_data

    def apply(self, queryset, field_data):
        return queryset


class SearchForm(forms.Form):
    fieldsets: dict[SearchField, list[forms.BoundField]]


class Search:
    fields: ClassVar[list[SearchField]] = []
    form_class: ClassVar[type] = SearchForm

    def __init__(self, queryset: models.QuerySet):
        self._queryset = queryset

    def field_data(self, raw_data):
        for field in self.fields:
            data = field.clean(raw_data)
            yield field, data

    def get_queryset(self, raw_data, for_field=None):
        qs = self._queryset
        for field, data in self.field_data(raw_data):
            print(field, data)
            if field == for_field:
                continue
            qs = field.apply(qs, data)
        return qs

    def get_form(self, data=None, **kwargs) -> SearchForm:
        form = self.form_class(data=data, **kwargs)
        form.fieldsets = {}
        for field in self.fields:
            qs = self.get_queryset(data or {}, for_field=field)
            for name, formfield in field.formfields(qs):
                field_name = field.prefix + name
                form.fields[field_name] = formfield
                form.fieldsets.setdefault(field, []).append(form[field_name])
        return form

    def execute(self, data):
        return self.get_queryset(data)


class DateFilter(SearchField):
    def formfields(self, queryset=None):
        yield "start", forms.DateField(required=False)
        yield "end", forms.DateField(required=False)

    def apply(self, queryset, cleaned_data):
        filters = {}
        if start := cleaned_data.get("start"):
            filters[f"{self.field_name}__gte"] = start
        return queryset.filter(**filters)


class Facet(SearchField):
    def get_choices(self, queryset=None):
        pass


class ChoiceFacet(Facet):
    def formfields(self, queryset=None):
        choices = (
            [
                (c, c)
                for c in queryset.order_by(self.field_name)
                .values_list(self.field_name, flat=True)
                .distinct(self.field_name)
            ]
            if queryset
            else []
        )
        yield "value", forms.MultipleChoiceField(choices=choices, required=False)
