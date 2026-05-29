from decimal import Decimal, InvalidOperation

from django import forms

from products.models import Category, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "description")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Category name"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Description"}
            ),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Category name is required.")
        return name


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            "product_id",
            "product_name",
            "category",
            "hsn_code",
            "volume_unit",
            "volume_size",
            "quantity",
            "mrp",
            "buy_price",
            "sell_price",
            "remark",
            "is_active",
        )
        widgets = {
            "product_id": forms.TextInput(attrs={"class": "form-control", "placeholder": "Product ID", "required": True}),
            "product_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Product name", "required": True}),
            "category": forms.Select(attrs={"class": "form-control", "required": True}),
            "hsn_code": forms.TextInput(attrs={"class": "form-control", "placeholder": "HSN code", "required": True}),
            "volume_unit": forms.Select(attrs={"class": "form-control", "required": True}),
            "volume_size": forms.NumberInput(attrs={"class": "form-control", "placeholder": "0", "step": "0.01", "required": True}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "placeholder": "0", "min": "0", "required": True}),
            "mrp": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Optional", "step": "0.01"}),
            "buy_price": forms.NumberInput(attrs={"class": "form-control", "placeholder": "0", "step": "0.01", "required": True}),
            "sell_price": forms.NumberInput(attrs={"class": "form-control", "placeholder": "0", "step": "0.01", "required": True}),
            "remark": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Remark"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_product_id(self):
        product_id = self.cleaned_data["product_id"].strip()
        if not product_id:
            raise forms.ValidationError("Product ID is required.")
        qs = Product.objects.filter(product_id__iexact=product_id)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                "This Product ID already exists. Each product must have a unique Product ID."
            )
        return product_id

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.product_id = instance.product_id.strip()
        if commit:
            instance.save()
        return instance

    def clean_volume_size(self):
        return self._positive_decimal(self.cleaned_data["volume_size"], "Volume size")

    def clean_quantity(self):
        qty = self.cleaned_data["quantity"]
        if qty is None or qty < 0:
            raise forms.ValidationError("Quantity must be zero or greater.")
        return qty

    def clean_buy_price(self):
        return self._positive_decimal(self.cleaned_data["buy_price"], "Buy price")

    def clean_sell_price(self):
        return self._positive_decimal(self.cleaned_data["sell_price"], "Sell price")

    def clean_mrp(self):
        mrp = self.cleaned_data.get("mrp")
        if mrp in (None, ""):
            return None
        return self._positive_decimal(mrp, "MRP")

    @staticmethod
    def _positive_decimal(value, label):
        if value is None:
            raise forms.ValidationError(f"{label} is required.")
        try:
            dec = Decimal(value)
        except (InvalidOperation, TypeError):
            raise forms.ValidationError(f"Enter a valid {label.lower()}.")
        if dec < 0:
            raise forms.ValidationError(f"{label} cannot be negative.")
        return dec
