{
    "name": "Custom Apps Menu - App Drawer",
    "version": "18.0.1.0.0",
    "category": "Hidden",
    "summary": "App Drawer con barra de búsqueda en lugar del dropdown de apps",
    "author": "Tu Empresa",
    "depends": ["web"],
    "installable": True,
    "license": "LGPL-3",
    "assets": {
        "web.assets_backend": [
            "custom_apps_menu/static/src/components/apps_menu/apps_menu.scss",
            "custom_apps_menu/static/src/components/apps_menu/apps_menu.esm.js",
        ],
    },
}
