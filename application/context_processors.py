def sidebar_context(request):
    user = getattr(request, "user", None)
    current_url = getattr(request, "resolver_match", None)
    current_name = current_url.url_name if current_url else ""

    nav_items = [
        {"name": "Dashboard", "url_name": "dashboard", "icon": "dashboard"},
    ]

    if user and user.is_authenticated:
        role = getattr(user, "role", None)

        if role in ("superadmin", "admin"):
            nav_items.append(
                {
                    "section": "Essential Data",
                    "name": "Product",
                    "icon": "products",
                    "collapsible": True,
                    "dropdown_id": "nav-product",
                    "open": current_name in ("product_list", "product_stock"),
                    "children": [
                        {
                            "name": "List",
                            "url_name": "product_list",
                            "icon": "list",
                        },
                        {
                            "name": "Stock",
                            "url_name": "product_stock",
                            "icon": "stock",
                        },
                    ],
                }
            )

        if role == "superadmin":
            nav_items.append(
                {
                    "name": "User Management",
                    "url_name": "user_list",
                    "icon": "users",
                    "children": [
                        {
                            "name": "User List",
                            "url_name": "user_list",
                            "icon": "list",
                        },
                    ],
                }
            )

    nav_items.append(
        {
            "name": "Personal Settings",
            "url_name": "settings",
            "icon": "settings",
            "children": [
                {
                    "name": "Settings",
                    "url_name": "settings",
                    "icon": "settings",
                },
            ],
        }
    )
    return {"sidebar_nav": nav_items}
