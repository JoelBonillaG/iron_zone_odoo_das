from config import connect, create

CUSTOMERS = [
    {"name": "Carlos Andrade",     "email": "candrade@gmail.com",    "phone": "0991234501", "street": "Av. Cevallos 123",    "city": "Ambato", "vat": "1801234567001"},
    {"name": "María Sánchez",      "email": "msanchez@gmail.com",    "phone": "0991234502", "street": "Calle Bolívar 456",   "city": "Ambato", "vat": "1712345678"},
    {"name": "Luis Moreira",       "email": "lmoreira@gmail.com",    "phone": "0991234503", "street": "Av. Miraflores 789",  "city": "Ambato", "vat": "0912345678001"},
    {"name": "Ana Villacís",       "email": "avillacis@gmail.com",   "phone": "0991234504", "street": "Calle Sucre 321",     "city": "Ambato", "vat": "1802345678"},
    {"name": "Diego Paredes",      "email": "dparedes@gmail.com",    "phone": "0991234505", "street": "Av. El Rey 654",      "city": "Ambato", "vat": "1713456789"},
    {"name": "Sofía Castillo",     "email": "scastillo@gmail.com",   "phone": "0991234506", "street": "Calle Montalvo 987",  "city": "Ambato", "vat": "0923456789"},
    {"name": "Andrés Flores",      "email": "aflores@gmail.com",     "phone": "0991234507", "street": "Av. Rodrigues 147",   "city": "Ambato", "vat": "1803456789"},
    {"name": "Gabriela Torres",    "email": "gtorres@gmail.com",     "phone": "0991234508", "street": "Calle Espejo 258",    "city": "Ambato", "vat": "1714567890"},
    {"name": "Sebastián Ruiz",     "email": "sruiz@gmail.com",       "phone": "0991234509", "street": "Av. Los Shyris 369",  "city": "Ambato", "vat": "0934567890"},
    {"name": "Valeria Guzmán",     "email": "vguzman@gmail.com",     "phone": "0991234510", "street": "Calle Pichincha 741", "city": "Ambato", "vat": "1804567890"},
]

def run():
    uid, models = connect()
    count = 0
    for c in CUSTOMERS:
        c["customer_rank"] = 1
        c["country_id"] = 63  # Ecuador
        create(uid, models, "res.partner", c)
        count += 1
        print(f"  Created customer: {c['name']}")
    print(f"Done: {count} customers created.")

if __name__ == "__main__":
    run()
