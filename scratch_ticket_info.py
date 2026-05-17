from seeds.config import DB, PASSWORD, connect

def create_view():
    uid, models = connect()
    inherit_id = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'search', [[('key', '=', 'website_event.event_description_full')]])
    if not inherit_id:
        print("Registration template not found")
        return
    
    arch = '''
    <data>
        <xpath expr="//aside[@id='o_wevent_event_main_sidebar']/div[hasclass('d-none', 'd-lg-block', 'border-bottom', 'pb-2', 'mb-3')]" position="before">
            <div class="o_wevent_sidebar_block border-bottom pb-3 mb-4 d-none d-lg-block">
                <h6 class="o_wevent_sidebar_title">Información del Boleto</h6>
                <div class="mb-2 d-flex align-items-center">
                    <i class="fa fa-ticket fa-fw me-2 text-muted"/> 
                    <strong class="me-2">Precio:</strong> 
                    <t t-if="event.event_ticket_ids and event.event_ticket_ids[0].price > 0">
                        <span t-out="event.event_ticket_ids[0].price" t-options="{'widget': 'monetary', 'display_currency': website.currency_id}"/>
                    </t>
                    <t t-else="">
                        <span class="badge text-bg-success">Gratis</span>
                    </t>
                </div>
                <div class="mb-2 d-flex align-items-center">
                    <i class="fa fa-users fa-fw me-2 text-muted"/> 
                    <strong class="me-2">Cupos Disponibles:</strong> 
                    <span t-out="event.seats_available"/> / <span t-out="event.seats_max"/>
                </div>
            </div>
        </xpath>
        
        <xpath expr="//header[hasclass('d-lg-none', 'mt-4', 'mb-2', 'py-3', 'border-top')]" position="after">
            <div class="o_wevent_sidebar_block border-bottom pb-3 mb-4 d-lg-none mt-3">
                <h6 class="o_wevent_sidebar_title">Información del Boleto</h6>
                <div class="mb-2 d-flex align-items-center">
                    <i class="fa fa-ticket fa-fw me-2 text-muted"/> 
                    <strong class="me-2">Precio:</strong> 
                    <t t-if="event.event_ticket_ids and event.event_ticket_ids[0].price > 0">
                        <span t-out="event.event_ticket_ids[0].price" t-options="{'widget': 'monetary', 'display_currency': website.currency_id}"/>
                    </t>
                    <t t-else="">
                        <span class="badge text-bg-success">Gratis</span>
                    </t>
                </div>
                <div class="mb-2 d-flex align-items-center">
                    <i class="fa fa-users fa-fw me-2 text-muted"/> 
                    <strong class="me-2">Cupos Disponibles:</strong> 
                    <span t-out="event.seats_available"/> / <span t-out="event.seats_max"/>
                </div>
            </div>
        </xpath>
    </data>
    '''
    
    existing = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'search', [[('key', '=', 'iz_event_ticket_info')]])
    if existing:
        models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'write', [existing, {'arch': arch}])
        print('Updated existing view ID:', existing[0])
    else:
        res = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'create', [{
            'name': 'Show Event Ticket Info',
            'key': 'iz_event_ticket_info',
            'type': 'qweb',
            'mode': 'extension',
            'inherit_id': inherit_id[0],
            'arch': arch,
            'active': True
        }])
        print('Created view ID:', res)

if __name__ == '__main__':
    create_view()
