from odoo import api, SUPERUSER_ID
import json

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    xml_ids = [
        "nexo_dealer.view_purchase_order_graph_nexo",
        "nexo_dealer.view_nexo_purchase_request_kanban",
        "nexo_dealer.view_nexo_purchase_request_graph",
        "nexo_dealer.view_nexo_purchase_request_pivot",
    ]
    for xmlid in xml_ids:
        try:
            view = env.ref(xmlid, raise_if_not_found=False)
            if view and view.exists():
                arch = dict(view.arch_db or {})
                if "en_US" in arch and "es_ES" not in arch:
                    arch["es_ES"] = arch["en_US"]
                    cr.execute("UPDATE ir_ui_view SET arch_db = %s WHERE id = %s",
                               [json.dumps(arch), view.id])
        except Exception:
            pass
