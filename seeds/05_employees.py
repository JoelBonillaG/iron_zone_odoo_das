from config import DB, PASSWORD, connect, create


DEPARTMENTS = [
    {"name": "Administracion"},
    {"name": "Entrenamiento"},
    {"name": "Atencion al Cliente"},
    {"name": "Operaciones"},
    {"name": "Nutricion"},
    {"name": "Marketing"},
    {"name": "Finanzas"},
    {"name": "Recursos Humanos"},
    {"name": "Mantenimiento"},
    {"name": "Seguridad"},
]

JOBS = [
    {"name": "Administrador del Gimnasio", "department": "Administracion"},
    {"name": "Entrenador Personal", "department": "Entrenamiento"},
    {"name": "Recepcionista", "department": "Atencion al Cliente"},
    {"name": "Tecnico de Mantenimiento", "department": "Operaciones"},
    {"name": "Instructor de CrossFit", "department": "Entrenamiento"},
    {"name": "Instructor de Yoga", "department": "Entrenamiento"},
    {"name": "Instructor de Spinning", "department": "Entrenamiento"},
    {"name": "Nutricionista", "department": "Nutricion"},
    {"name": "Especialista en Marketing", "department": "Marketing"},
    {"name": "Especialista en Finanzas", "department": "Finanzas"},
]

EMPLOYEES = [
    {
        "name": "Carlos Mendez",
        "job": "Instructor de CrossFit",
        "department": "Entrenamiento",
        "work_email": "josuegarcab2@gmail.com",
        "mobile_phone": "0991234525",
        "work_phone": "032400105",
    },
    {
        "name": "Sofia Garcia",
        "job": "Instructor de Yoga",
        "department": "Entrenamiento",
        "work_email": "josuegarcab2@hotmail.com",
        "mobile_phone": "0991234526",
        "work_phone": "032400106",
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


def archive_old_demo_employees(uid, models):
    allowed_emails = [employee["work_email"] for employee in EMPLOYEES]
    old_ids = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "hr.employee",
        "search",
        [[("work_email", "!=", False), ("work_email", "not in", allowed_emails)]],
    )
    if old_ids:
        models.execute_kw(DB, uid, PASSWORD, "hr.employee", "write", [old_ids, {"active": False}])
        print(f"Archived {len(old_ids)} old demo employee(s).")


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
    archive_old_demo_employees(uid, models)
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
