from decimal import Decimal

from django.db.models import Count, Q, Sum

from products.models import Product


def filter_products(queryset, params):
    q = params.get("q", "").strip()
    if q:
        queryset = queryset.filter(
            Q(product_name__icontains=q) | Q(hsn_code__icontains=q) | Q(product_id__icontains=q)
        )

    category_id = params.get("category", "").strip()
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    buy_min = params.get("buy_min", "").strip()
    buy_max = params.get("buy_max", "").strip()
    sell_min = params.get("sell_min", "").strip()
    sell_max = params.get("sell_max", "").strip()

    def _to_decimal(val):
        try:
            return Decimal(val)
        except Exception:
            return None

    if buy_min:
        d = _to_decimal(buy_min)
        if d is not None:
            queryset = queryset.filter(buy_price__gte=d)
    if buy_max:
        d = _to_decimal(buy_max)
        if d is not None:
            queryset = queryset.filter(buy_price__lte=d)
    if sell_min:
        d = _to_decimal(sell_min)
        if d is not None:
            queryset = queryset.filter(sell_price__gte=d)
    if sell_max:
        d = _to_decimal(sell_max)
        if d is not None:
            queryset = queryset.filter(sell_price__lte=d)

    return queryset.select_related("category", "created_by")


def product_summary(queryset):
    agg = queryset.aggregate(
        total_count=Count("id"),
        total_buy=Sum("buy_price"),
        total_mrp=Sum("mrp"),
    )
    return {
        "total_count": agg["total_count"] or 0,
        "total_buy": agg["total_buy"] or Decimal("0"),
        "total_mrp": agg["total_mrp"] or Decimal("0"),
    }
