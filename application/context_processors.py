def sidebar_context(request):
    user = getattr(request, "user", None)
    nav_items = [
        {"name": "Dashboard", "url_name": "dashboard", "icon": "dashboard"},
    ]
    if user and user.is_authenticated and getattr(user, "role", None) == "superadmin":
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
