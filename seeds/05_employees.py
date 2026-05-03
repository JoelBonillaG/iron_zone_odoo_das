from config import DB, PASSWORD, connect, create


DEPARTMENTS = [
    {"name": "Administracion"},
    {"name": "Entrenamiento"},
    {"name": "Atencion al Cliente"},
    {"name": "Operaciones"},
]

JOBS = [
    {"name": "Administrador del Gimnasio", "department": "Administracion"},
    {"name": "Entrenador Personal", "department": "Entrenamiento"},
    {"name": "Recepcionista", "department": "Atencion al Cliente"},
    {"name": "Tecnico de Mantenimiento", "department": "Operaciones"},
]

EMPLOYEES = [
    {
        "name": "Daniela Morales",
        "job": "Administrador del Gimnasio",
        "department": "Administracion",
        "work_email": "daniela.morales@ironzone.com",
        "mobile_phone": "0991234521",
        "work_phone": "032400101",
    },
    {
        "name": "Mateo Rivas",
        "job": "Entrenador Personal",
        "department": "Entrenamiento",
        "work_email": "mateo.rivas@ironzone.com",
        "mobile_phone": "0991234522",
        "work_phone": "032400102",
    },
    {
        "name": "Camila Torres",
        "job": "Recepcionista",
        "department": "Atencion al Cliente",
        "work_email": "camila.torres@ironzone.com",
        "mobile_phone": "0991234523",
        "work_phone": "032400103",
    },
    {
        "name": "Jorge Paredes",
        "job": "Tecnico de Mantenimiento",
        "department": "Operaciones",
        "work_email": "jorge.paredes@ironzone.com",
        "mobile_phone": "0991234524",
        "work_phone": "032400104",
    },
]


def search_one(uid, models, model, domain, fields=None):
    records = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        model,
        "search_read",
        [domain],
        {"fields": fields or ["id"], "limit": 1, "context": {"active_test": False}},
    )
    return records[0] if records else None


def create_or_update(uid, models, model, domain, values, fields=None):
    record = search_one(uid, models, model, domain, fields=fields)
    if record:
        models.execute_kw(DB, uid, PASSWORD, model, "write", [[record["id"]], values])
        return record["id"], False
    return create(uid, models, model, values), True


def run():
    uid, models = connect()

    department_ids = {}
    print("Syncing employee departments...")
    for department in DEPARTMENTS:
        department_id, created = create_or_update(
            uid,
            models,
            "hr.department",
            [("name", "=", department["name"])],
            department,
            fields=["id", "name"],
        )
        department_ids[department["name"]] = department_id
        action = "Created" if created else "Updated"
        print(f"  {action} department: {department['name']}")

    job_ids = {}
    print("Syncing employee job positions...")
    for job in JOBS:
        values = {
            "name": job["name"],
            "department_id": department_ids[job["department"]],
        }
        job_id, created = create_or_update(
            uid,
            models,
            "hr.job",
            [("name", "=", job["name"])],
            values,
            fields=["id", "name"],
        )
        job_ids[job["name"]] = job_id
        action = "Created" if created else "Updated"
        print(f"  {action} job position: {job['name']}")

    created_count = 0
    updated_count = 0
    print("Syncing employees...")
    for employee in EMPLOYEES:
        values = {
            "name": employee["name"],
            "job_title": employee["job"],
            "job_id": job_ids[employee["job"]],
            "department_id": department_ids[employee["department"]],
            "work_email": employee["work_email"],
            "mobile_phone": employee["mobile_phone"],
            "work_phone": employee["work_phone"],
            "active": True,
        }
        _, created = create_or_update(
            uid,
            models,
            "hr.employee",
            [("work_email", "=", employee["work_email"])],
            values,
            fields=["id", "name"],
        )
        if created:
            created_count += 1
        else:
            updated_count += 1
        action = "Created" if created else "Updated"
        print(f"  {action} employee: {employee['name']} ({employee['job']})")

    print(f"Done: {created_count} employees created, {updated_count} updated.")


if __name__ == "__main__":
    run()
