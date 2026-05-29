from django.contrib import messages
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import TemplateView

from application.mixins import AdminOrSuperAdminRequiredMixin
from products.forms import CategoryForm, ProductForm
from products.models import Category, Product, ProductImage
from products.services import filter_products, product_summary

PER_PAGE_OPTIONS = (10, 20, 50, 100)


class ProductPageMixin(AdminOrSuperAdminRequiredMixin):
    def get_filtered_queryset(self):
        return filter_products(Product.objects.all(), self.request.GET)

    def get_pagination_context(self, queryset):
        per_page = self.request.GET.get("per_page", "20")
        try:
            per_page = int(per_page)
        except (TypeError, ValueError):
            per_page = 20
        if per_page not in PER_PAGE_OPTIONS:
            per_page = 20

        paginator = Paginator(queryset, per_page)
        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        start = 0 if paginator.count == 0 else page_obj.start_index()
        end = 0 if paginator.count == 0 else page_obj.end_index()

        return {
            "page_obj": page_obj,
            "paginator": paginator,
            "per_page": per_page,
            "per_page_options": PER_PAGE_OPTIONS,
            "record_start": start,
            "record_end": end,
            "record_total": paginator.count,
        }

    def get_filter_context(self):
        return {
            "categories": Category.objects.all(),
            "filters": self.request.GET,
            "filter_qs": self.request.GET.urlencode(),
        }


class ProductListView(ProductPageMixin, TemplateView):
    template_name = "products/list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_filtered_queryset()
        ctx.update(self.get_pagination_context(qs))
        ctx.update(self.get_filter_context())
        ctx["page_title"] = "Product List"
        ctx["is_stock_page"] = False
        ctx["summary"] = product_summary(qs)
        return ctx


def build_stock_context(request, **overrides):
    """Build Stock page context (shared for GET and failed product form POST)."""
    mixin = ProductPageMixin()
    mixin.request = request
    qs = mixin.get_filtered_queryset()
    ctx = {
        "page_title": "Stock",
        "is_stock_page": True,
        "summary": product_summary(qs),
        "category_form": CategoryForm(),
        "product_form": ProductForm(),
        "edit_product": None,
        "can_delete": request.user.role == "superadmin",
        "show_category_modal": False,
        "show_product_modal": False,
        "show_bulk_modal": False,
    }
    ctx.update(mixin.get_pagination_context(qs))
    ctx.update(mixin.get_filter_context())
    ctx.update(overrides)
    return ctx


class ProductStockView(ProductPageMixin, TemplateView):
    template_name = "products/stock.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(build_stock_context(self.request))
        ctx["show_category_modal"] = self.request.GET.get("open_category") == "1"
        ctx["show_product_modal"] = self.request.GET.get("open_product") == "1"
        ctx["show_bulk_modal"] = self.request.GET.get("open_bulk") == "1"

        edit_id = self.request.GET.get("edit_product")
        if edit_id:
            ctx["edit_product"] = get_object_or_404(Product, pk=edit_id)
            ctx["product_form"] = ProductForm(instance=ctx["edit_product"])
            ctx["show_product_modal"] = True
        return ctx


class CategoryCreateView(AdminOrSuperAdminRequiredMixin, View):
    def post(self, request):
        form = CategoryForm(request.POST)
        redirect_to = request.POST.get("next", "product_stock")
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully.")
            return redirect(redirect_to)
        messages.error(request, "Could not add category. Please check the form.")
        return redirect(f"{redirect_to}?open_category=1")


class ProductCreateView(AdminOrSuperAdminRequiredMixin, View):
    def post(self, request):
        form = ProductForm(request.POST)
        redirect_to = request.POST.get("next", "product_stock")
        if form.is_valid():
            try:
                product = form.save(commit=False)
                product.created_by = request.user
                product.save()
                self._save_images(request, product)
            except IntegrityError:
                form.add_error(
                    "product_id",
                    "This Product ID already exists. Each product must have a unique Product ID.",
                )
            else:
                messages.success(request, "Product added successfully.")
                return redirect(redirect_to)

        if not form.errors:
            messages.error(request, "Could not add product. Please check the form.")
        else:
            messages.error(request, "Please fix the errors below.")
        ctx = build_stock_context(
            request,
            product_form=form,
            show_product_modal=True,
        )
        return render(request, "products/stock.html", ctx)

    @staticmethod
    def _save_images(request, product):
        for image in request.FILES.getlist("product_images"):
            ProductImage.objects.create(product=product, image=image)


class ProductUpdateView(AdminOrSuperAdminRequiredMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(request.POST, instance=product)
        redirect_to = request.POST.get("next", "product_stock")
        if form.is_valid():
            try:
                product = form.save()
                self._remove_images(request, product)
                ProductCreateView._save_images(request, product)
            except IntegrityError:
                form.add_error(
                    "product_id",
                    "This Product ID already exists. Each product must have a unique Product ID.",
                )
            else:
                messages.success(request, "Product updated successfully.")
                return redirect(redirect_to)

        if not form.errors:
            messages.error(request, "Could not update product. Please check the form.")
        else:
            messages.error(request, "Please fix the errors below.")
        ctx = build_stock_context(
            request,
            product_form=form,
            edit_product=product,
            show_product_modal=True,
        )
        return render(request, "products/stock.html", ctx)

    @staticmethod
    def _remove_images(request, product):
        remove_ids = request.POST.getlist("remove_images")
        if remove_ids:
            product.images.filter(pk__in=remove_ids).delete()


class ProductDeleteView(AdminOrSuperAdminRequiredMixin, View):
    def post(self, request, pk):
        if request.user.role != "superadmin":
            messages.error(request, "Only SuperAdmin can delete products.")
            return redirect("product_stock")
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        messages.success(request, "Product deleted successfully.")
        redirect_to = request.POST.get("next", "product_stock")
        return redirect(redirect_to)
