from seeds.config import DB, PASSWORD, connect

def create_view():
    uid, models = connect()
    inherit_id = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'search', [[('key', '=', 'website_event.registration_template')]])
    if not inherit_id:
        print("Registration template not found")
        return
    
    arch = '''
    <xpath expr="//button[@data-bs-target='#modal_ticket_registration']" position="replace">
        <t t-if="request.env.user._is_public()">
            <a t-attf-href="/web/login?redirect=/event/#{slug(event)}" t-attf-class="btn btn-primary {{cta_additional_classes}}">Register</a>
        </t>
        <t t-else="">
            <button type="button" data-bs-toggle="modal" data-bs-target="#modal_ticket_registration" t-attf-class="btn btn-primary {{cta_additional_classes}}">Register</button>
        </t>
    </xpath>
    '''
    
    # Check if our view already exists
    existing = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'search', [[('key', '=', 'iz_event_login_required')]])
    if existing:
        models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'write', [existing, {'arch': arch}])
        print('Updated existing view ID:', existing[0])
    else:
        res = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'create', [{
            'name': 'Require Login to Register',
            'key': 'iz_event_login_required',
            'type': 'qweb',
            'mode': 'extension',
            'inherit_id': inherit_id[0],
            'arch': arch,
            'active': True
        }])
        print('Created view ID:', res)

if __name__ == '__main__':
    create_view()
