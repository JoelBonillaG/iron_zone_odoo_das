import xmlrpc.client
from config import DB, PASSWORD, connect

uid, models = connect()
views = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'search_read', [[('arch_db', 'ilike', 'organizer')]], {'fields': ['key', 'arch_db']})
for v in views:
    key = v.get('key') or ''
    if 'event' in key:
        filename = "view_" + key.replace('.', '_') + ".xml"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(v['arch_db'])
print('Done!')
