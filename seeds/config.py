import xmlrpc.client

URL      = "http://localhost:8069"
DB       = "iron_zone"
USERNAME = "bjeferssonvinicio2005@gmail.com"
PASSWORD = "admin123"

def connect():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    if not uid:
        raise Exception("Auth failed. Verify USERNAME/PASSWORD in seeds/config.py")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    return uid, models

def create(uid, models, model, vals_list):
    return models.execute_kw(DB, uid, PASSWORD, model, "create", [vals_list])

def search_read(uid, models, model, domain, fields):
    return models.execute_kw(DB, uid, PASSWORD, model, "search_read", [domain], {"fields": fields})
