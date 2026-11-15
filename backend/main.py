# CRUD APP - Create, Remove, Update, Delete

from flask import request, jsonify, Response
import csv
import io
from datetime import date as date_class
from config import app, db
from models import Contact, ContactAccess, Equipment, EquipmentLocation, EquipmentNetwork, EquipmentChangeHistory, EquipmentType, EquipmentState, Maintenance, MaintenanceType
from enum import IntEnum
from sqlalchemy import cast, String, or_
from sqlalchemy.exc import SQLAlchemyError

class HTTPStatus(IntEnum):
    CREATED = 201
    BAD_REQUEST = 400
    CONFLICT = 409
    UNAUTHORIZED = 401
    NOT_FOUND = 404

VALID_PERMISSIONS = {
    "VIEW_EQUIPMENT",
    "MANAGE_EQUIPMENT",
    "VIEW_MAINTENANCE",
    "MANAGE_MAINTENANCE",
    "VIEW_REPORTS",
    "MANAGE_USERS",
}

ROLE_PERMISSIONS = {
    "Administrator": sorted(VALID_PERMISSIONS),
    "Network Engineer": ["VIEW_EQUIPMENT", "MANAGE_EQUIPMENT", "VIEW_MAINTENANCE", "MANAGE_MAINTENANCE", "VIEW_REPORTS"],
    "IT Technician": ["VIEW_EQUIPMENT", "VIEW_REPORTS"],
}


def sync_contact_permissions(contact):
    permissions = ROLE_PERMISSIONS.get(contact.role)
    if permissions is None:
        return
    if not contact.access:
        contact.access = ContactAccess()
    contact.access.permissions_list = permissions


def create_simple_pdf(title, rows):
    lines = [title, ""]
    lines.extend(" | ".join(str(value or "") for value in row)[:110] for row in rows)
    content = ["BT", "/F1 11 Tf", "50 780 Td"]
    for line in lines:
        safe_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content.append(f"({safe_line}) Tj")
        content.append("0 -16 Td")
    content.append("ET")
    stream = "\n".join(content).encode("latin-1", errors="replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode())
    return bytes(pdf)

# AUTH ROUTES 

# LOGIN
@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email")
    password = request.json.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), HTTPStatus.BAD_REQUEST

    contact = Contact.query.filter_by(email=email).first()

    if not contact or contact.password != password:
        return jsonify({"message": "Invalid email or password."}), HTTPStatus.UNAUTHORIZED
    sync_contact_permissions(contact)
    db.session.commit()

    return jsonify({"message": "Login successful!", "user": contact.to_json()})

# REGISTER
@app.route("/register", methods=["POST"])
def register():
    first_name = request.json.get("firstName")
    last_name = request.json.get("lastName")
    email = request.json.get("email")
    password = request.json.get("password")
    role = request.json.get("role", "IT Technician")

    if not first_name or not last_name or not email or not password:
        return jsonify({"message": "All fields are required."}), HTTPStatus.BAD_REQUEST
    if role not in ROLE_PERMISSIONS:
        return jsonify({"message": "Invalid role selected."}), HTTPStatus.BAD_REQUEST

    existing = Contact.query.filter_by(email=email).first()
    if existing:
        return jsonify({"message": "Email already registered."}), HTTPStatus.BAD_REQUEST

    new_contact = Contact(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        role=role,
        is_admin=1 if role == "Administrator" else 0
    )

    try:
        db.session.add(new_contact)
        db.session.flush()
        access = ContactAccess(contact_id=new_contact.id)
        access.permissions_list = ROLE_PERMISSIONS[role]
        db.session.add(access)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": str(e)}), HTTPStatus.BAD_REQUEST

    return jsonify({"message": "Account created!", "user": new_contact.to_json()}), HTTPStatus.CREATED

# CONTACT ROUTES 
@app.route("/contacts", methods=["GET"])
def get_contacts():
    contacts = Contact.query.all() # SELECT * FROM CONTACTS
    for contact in contacts:
        sync_contact_permissions(contact)
    db.session.commit()
    json_contacts = list(map(lambda x: x.to_json(), contacts)) # collects the results into a new map object (but we cast it to a list).
    return jsonify({"contacts": json_contacts})

# CREATE CONTACTS (Admin only)
@app.route("/create_contact", methods=["POST"])
def create_contact():
    first_name = request.json.get("firstName")
    last_name = request.json.get("lastName")
    email = request.json.get("email")
    password = request.json.get("password", "default123")
    role = request.json.get("role")
    is_admin = request.json.get("isAdmin", 0)
    if role == "Administrator":
        is_admin = 1

    if not first_name or not last_name or not email or not role:
        return jsonify({"message": "You need to include full name, email, and role."}), HTTPStatus.BAD_REQUEST
    if role not in ROLE_PERMISSIONS:
        return jsonify({"message": "Invalid role selected."}), HTTPStatus.BAD_REQUEST
    
    new_contact = Contact(first_name=first_name, last_name=last_name, email=email, password=password, role=role, is_admin=is_admin)

    try:
        db.session.add(new_contact) # update database
        db.session.flush()
        access = ContactAccess(contact_id=new_contact.id)
        access.permissions_list = ROLE_PERMISSIONS[role]
        db.session.add(access)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": str(e)}), HTTPStatus.BAD_REQUEST

    return jsonify({"message" : "User created!"}), HTTPStatus.CREATED

# UPDATE CONTACTS
@app.route("/update_contact/<int:user_id>", methods=["PATCH"])
def update_contact(user_id):
    contact = Contact.query.get(user_id)

    if not contact:
        return jsonify({"message" : "User not found"}), HTTPStatus.NOT_FOUND
    
    data = request.json
    role = data.get("role", contact.role)
    if role not in ROLE_PERMISSIONS:
        return jsonify({"message": "Invalid role selected."}), HTTPStatus.BAD_REQUEST
    contact.first_name = data.get("firstName", contact.first_name)
    contact.last_name = data.get("lastName", contact.last_name)
    contact.email = data.get("email", contact.email)
    contact.role = role
    contact.is_admin = 1 if role == "Administrator" else 0
    if not contact.access:
        contact.access = ContactAccess()
    contact.access.permissions_list = ROLE_PERMISSIONS[role]

    db.session.commit() # update database

    return jsonify({"message" : "User updated."})

# DELETE CONTACTS
@app.route("/delete_contact/<int:user_id>", methods = ["DELETE"])
def delete_contact(user_id):

    contact = Contact.query.get(user_id)
    
    if not contact:
        return jsonify({"message" : "User not found"}), HTTPStatus.NOT_FOUND
    
    db.session.delete(contact) # update database
    db.session.commit()

    return jsonify({"message" : "User deleted!"})

# ================ 
# EQUIPMENT ROUTES 

# GET ALL EQUIPMENT
@app.route("/equipment", methods=["GET"])
def get_equipment():
    query = Equipment.query
    search = request.args.get("search", "").strip()
    equipment_type = request.args.get("type")
    equipment_state = request.args.get("state")
    location = request.args.get("location", "").strip()
    responsible = request.args.get("responsible")

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Equipment.type.ilike(search_pattern),
                Equipment.model.ilike(search_pattern),
                Equipment.serial_number.ilike(search_pattern),
            )
        )
    if equipment_type:
        query = query.filter(Equipment.type == equipment_type)
    if equipment_state:
        query = query.filter(Equipment.equipment_state == equipment_state)
    elif request.args.get("includeArchived") != "true":
        query = query.filter(Equipment.equipment_state != EquipmentState.ARCHIVED.value)
    if responsible:
        query = query.filter(Equipment.assigned_to == responsible)
    if location:
        location_pattern = f"%{location}%"
        query = query.join(EquipmentLocation).filter(
            or_(
                cast(EquipmentLocation.floor, String).ilike(location_pattern),
                cast(EquipmentLocation.room_number, String).ilike(location_pattern),
                EquipmentLocation.description.ilike(location_pattern),
            )
        )

    equipment = query.order_by(Equipment.id).all()
    json_equipment = list(map(lambda x: x.to_json(), equipment))
    return jsonify({"equipment": json_equipment})


@app.route("/equipment/<int:equipment_id>", methods=["GET"])
def get_equipment_details(equipment_id):
    equipment = Equipment.query.get(equipment_id)
    if not equipment:
        return jsonify({"message": "Equipment not found"}), HTTPStatus.NOT_FOUND

    details = equipment.to_json()
    details["maintenanceHistory"] = [
        maintenance.to_json()
        for maintenance in sorted(
            equipment.maintenance_records,
            key=lambda record: record.date,
            reverse=True,
        )
    ]
    details["changeHistory"] = [
        change.to_json()
        for change in sorted(equipment.change_history, key=lambda item: item.changed_at, reverse=True)
    ]
    return jsonify({"equipment": details})

# CREATE EQUIPMENT
@app.route("/create_equipment", methods=["POST"])
def create_equipment():
    eq_type = request.json.get("type")
    model = request.json.get("model")
    serial_number = request.json.get("serialNumber")
    equipment_state = request.json.get("equipmentState", "OPERATIONAL")
    assigned_to = request.json.get("assignedTo")

    if not eq_type or not model or not serial_number:
        return jsonify({"message": "Type, model, and serial number are required."}), HTTPStatus.BAD_REQUEST

    if len(serial_number) < 10:
        return jsonify({"message": "Serial Number must be at least 10 characters long."}), HTTPStatus.BAD_REQUEST
    
    valid_types = [e.value for e in EquipmentType]
    valid_states = [e.value for e in EquipmentState]

    if eq_type not in valid_types:
        return jsonify({"message": f"Invalid type. Must be one of: {valid_types}"}), HTTPStatus.BAD_REQUEST

    if equipment_state not in valid_states:
        return jsonify({"message": f"Invalid state. Must be one of: {valid_states}"}), HTTPStatus.BAD_REQUEST

    new_equipment = Equipment(
        type=eq_type,
        model=model,
        serial_number=serial_number,
        equipment_state=equipment_state,
        assigned_to=assigned_to
    )

    try:
        db.session.add(new_equipment)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": str(e)}), HTTPStatus.BAD_REQUEST

    return jsonify({"message": "Equipment created!"}), HTTPStatus.CREATED


@app.route("/bulk_import_equipment", methods=["POST"])
def bulk_import_equipment():
    uploaded_file = request.files.get("file")
    if not uploaded_file or not uploaded_file.filename.lower().endswith(".csv"):
        return jsonify({"message": "A CSV file is required."}), HTTPStatus.BAD_REQUEST

    try:
        rows = list(csv.DictReader(io.TextIOWrapper(uploaded_file.stream, encoding="utf-8-sig", newline="")))
    except (UnicodeDecodeError, csv.Error):
        return jsonify({"message": "The CSV file could not be read."}), HTTPStatus.BAD_REQUEST

    required_columns = {"type", "model", "serialNumber"}
    if not rows or not required_columns.issubset(rows[0].keys()):
        return jsonify({"message": "CSV must include type, model, and serialNumber columns."}), HTTPStatus.BAD_REQUEST

    valid_types = {equipment_type.value for equipment_type in EquipmentType}
    valid_states = {equipment_state.value for equipment_state in EquipmentState}
    serial_numbers = set()
    equipment_to_create = []

    for row_number, row in enumerate(rows, start=2):
        eq_type = row.get("type", "").strip()
        model = row.get("model", "").strip()
        serial_number = row.get("serialNumber", "").strip()
        equipment_state = row.get("equipmentState", "OPERATIONAL").strip() or "OPERATIONAL"
        assigned_to = row.get("assignedTo", "").strip() or None

        if not eq_type or not model or not serial_number:
            return jsonify({"message": f"Row {row_number}: type, model, and serialNumber are required."}), HTTPStatus.BAD_REQUEST
        if eq_type not in valid_types:
            return jsonify({"message": f"Row {row_number}: invalid type."}), HTTPStatus.BAD_REQUEST
        if equipment_state not in valid_states:
            return jsonify({"message": f"Row {row_number}: invalid equipmentState."}), HTTPStatus.BAD_REQUEST
        if len(serial_number) < 10 or serial_number in serial_numbers or Equipment.query.filter_by(serial_number=serial_number).first():
            return jsonify({"message": f"Row {row_number}: serialNumber is invalid or already exists."}), HTTPStatus.BAD_REQUEST
        if assigned_to and (not assigned_to.isdigit() or not Contact.query.get(int(assigned_to))):
            return jsonify({"message": f"Row {row_number}: assignedTo does not exist."}), HTTPStatus.BAD_REQUEST

        equipment = Equipment(
            type=eq_type,
            model=model,
            serial_number=serial_number,
            equipment_state=equipment_state,
            assigned_to=int(assigned_to) if assigned_to else None,
        )
        equipment_to_create.append((equipment, row))
        serial_numbers.add(serial_number)

    try:
        for equipment, row in equipment_to_create:
            db.session.add(equipment)
            db.session.flush()
            if row.get("floor") or row.get("roomNumber"):
                if not row.get("floor") or not row.get("roomNumber"):
                    raise ValueError("Both floor and roomNumber are required for a location.")
                equipment.location_details = EquipmentLocation(
                    id=equipment.id,
                    floor=int(row["floor"]),
                    room_number=int(row["roomNumber"]),
                    description=row.get("locationDescription", "").strip() or None,
                )
            network_values = {key: row.get(key, "").strip() or None for key in ("ipAddress", "macAddress", "hostname", "vlan")}
            if any(network_values.values()):
                equipment.network_parameters = EquipmentNetwork(id=equipment.id, **{
                    "ip_address": network_values["ipAddress"],
                    "mac_address": network_values["macAddress"],
                    "hostname": network_values["hostname"],
                    "vlan": network_values["vlan"],
                })
        db.session.commit()
    except (ValueError, TypeError, SQLAlchemyError) as error:
        db.session.rollback()
        return jsonify({"message": f"Import failed: {error}"}), HTTPStatus.BAD_REQUEST

    return jsonify({"message": f"{len(equipment_to_create)} devices imported successfully."}), HTTPStatus.CREATED

# UPDATE EQUIPMENT
@app.route("/update_equipment/<int:equipment_id>", methods=["PATCH"])
def update_equipment(equipment_id):
    equipment = Equipment.query.get(equipment_id)

    if not equipment:
        return jsonify({"message": "Equipment not found"}), HTTPStatus.NOT_FOUND

    data = request.json
    changes = []

    def record_change(field, previous, new):
        if previous != new:
            changes.append((field, previous, new))

    valid_types = [e.value for e in EquipmentType]
    valid_states = [e.value for e in EquipmentState]

    if "type" in data and data["type"] not in valid_types:
        return jsonify({"message": f"Invalid type. Must be one of: {valid_types}"}), HTTPStatus.BAD_REQUEST

    if "equipmentState" in data and data["equipmentState"] not in valid_states:
        return jsonify({"message": f"Invalid state. Must be one of: {valid_states}"}), HTTPStatus.BAD_REQUEST

    new_type = data.get("type", equipment.type)
    new_model = data.get("model", equipment.model)
    new_serial_number = data.get("serialNumber", equipment.serial_number)
    new_state = data.get("equipmentState", equipment.equipment_state)
    new_assigned_to = data.get("assignedTo", equipment.assigned_to)
    record_change("type", equipment.type, new_type)
    record_change("model", equipment.model, new_model)
    record_change("serialNumber", equipment.serial_number, new_serial_number)
    record_change("equipmentState", equipment.equipment_state, new_state)
    record_change("assignedTo", equipment.assigned_to, new_assigned_to)
    equipment.type = new_type
    equipment.model = new_model
    equipment.serial_number = new_serial_number
    equipment.equipment_state = new_state
    equipment.assigned_to = new_assigned_to

    location_data = data.get("locationDetails")
    if location_data:
        location = equipment.location_details
        if not location:
            if location_data.get("floor") is None or location_data.get("roomNumber") is None:
                return jsonify({"message": "Floor and room are required."}), HTTPStatus.BAD_REQUEST
            location = EquipmentLocation(id=equipment.id)
            equipment.location_details = location
        new_floor = location_data.get("floor", location.floor)
        new_room = location_data.get("roomNumber", location.room_number)
        new_description = location_data.get("description", location.description)
        record_change("location.floor", location.floor, new_floor)
        record_change("location.roomNumber", location.room_number, new_room)
        record_change("location.description", location.description, new_description)
        location.floor, location.room_number, location.description = new_floor, new_room, new_description

    network_data = data.get("networkParameters")
    if network_data is not None:
        network = equipment.network_parameters
        if not network:
            network = EquipmentNetwork(id=equipment.id)
            equipment.network_parameters = network
        for field, column in (("ipAddress", "ip_address"), ("macAddress", "mac_address"), ("hostname", "hostname"), ("vlan", "vlan")):
            new_value = network_data.get(field, getattr(network, column))
            record_change(f"network.{field}", getattr(network, column), new_value)
            setattr(network, column, new_value)

    user_id = data.get("changedBy")
    for field, previous, new in changes:
        db.session.add(EquipmentChangeHistory(
            equipment_id=equipment.id,
            field_name=field,
            previous_value=str(previous) if previous is not None else None,
            new_value=str(new) if new is not None else None,
            changed_by=user_id
        ))

    db.session.commit()

    return jsonify({"message": "Equipment updated."})

# DELETE EQUIPMENT
@app.route("/delete_equipment/<int:equipment_id>", methods=["DELETE"])
def delete_equipment(equipment_id):
    equipment = Equipment.query.get(equipment_id)

    if not equipment:
        return jsonify({"message": "Equipment not found"}), HTTPStatus.NOT_FOUND

    if equipment.maintenance_records or equipment.change_history:
        message = (
            "Equipment has associated maintenance history. The operation will be converted to logical archiving."
            if equipment.maintenance_records
            else "Equipment has associated change history. The operation will be converted to logical archiving."
        )
        return jsonify({
            "message": message,
            "requiresArchive": True,
        }), HTTPStatus.CONFLICT

    if request.args.get("confirmed") != "true":
        return jsonify({
            "message": "Confirm equipment deletion.",
            "requiresConfirmation": True,
        }), HTTPStatus.CONFLICT

    db.session.delete(equipment)
    db.session.commit()

    return jsonify({"message": "Equipment deleted!"})

# ==================== 
# MAINTENANCE ROUTES 

# GET ALL MAINTENANCES
@app.route("/maintenances", methods=["GET"])
def get_maintenances():
    maintenances = Maintenance.query.all()
    json_maintenances = list(map(lambda x: x.to_json(), maintenances))
    return jsonify({"maintenances": json_maintenances})


@app.route("/reports", methods=["GET"])
def generate_report():
    report_type = request.args.get("reportType", "maintenance")
    export_format = request.args.get("format", "csv").lower()
    equipment_id = request.args.get("equipmentId")
    equipment_state = request.args.get("state")
    equipment_type = request.args.get("equipmentType")
    maintenance_type = request.args.get("maintenanceType")
    start_date = request.args.get("startDate")
    end_date = request.args.get("endDate")

    if report_type not in ("equipment", "maintenance") or export_format not in ("csv", "pdf"):
        return jsonify({"message": "Invalid report type or export format."}), HTTPStatus.BAD_REQUEST

    if start_date:
        try:
            date_class.fromisoformat(start_date)
        except ValueError:
            return jsonify({"message": "Invalid start date."}), HTTPStatus.BAD_REQUEST
    if end_date:
        try:
            date_class.fromisoformat(end_date)
        except ValueError:
            return jsonify({"message": "Invalid end date."}), HTTPStatus.BAD_REQUEST
    if start_date and end_date and start_date > end_date:
        return jsonify({"message": "Start date cannot be after end date."}), HTTPStatus.BAD_REQUEST

    if report_type == "equipment":
        query = Equipment.query
        if equipment_id:
            query = query.filter(Equipment.id == equipment_id)
        if equipment_state:
            query = query.filter(Equipment.equipment_state == equipment_state)
        if equipment_type:
            query = query.filter(Equipment.type == equipment_type)
        records = query.order_by(Equipment.id).all()
        headers = ["ID", "Type", "Model", "Serial Number", "State", "Responsible"]
        rows = [[record.id, record.type, record.model, record.serial_number, record.equipment_state,
                 f"{record.assigned_contact.first_name} {record.assigned_contact.last_name}" if record.assigned_contact else ""] for record in records]
    else:
        query = Maintenance.query.join(Equipment)
        if equipment_id:
            query = query.filter(Maintenance.equipment_id == equipment_id)
        if equipment_state:
            query = query.filter(Equipment.equipment_state == equipment_state)
        if equipment_type:
            query = query.filter(Equipment.type == equipment_type)
        if maintenance_type:
            query = query.filter(Maintenance.maintenance_type == maintenance_type)
        if start_date:
            query = query.filter(Maintenance.date >= date_class.fromisoformat(start_date))
        if end_date:
            query = query.filter(Maintenance.date <= date_class.fromisoformat(end_date))
        records = query.order_by(Maintenance.date.desc()).all()
        headers = ["ID", "Equipment", "Date", "Type", "Description"]
        rows = [[record.id, record.equipment.serial_number, record.date.isoformat(), record.maintenance_type, record.description] for record in records]

    if not rows:
        return jsonify({"message": "Não existem dados para os critérios selecionados"}), HTTPStatus.NOT_FOUND

    if export_format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(rows)
        return Response(output.getvalue(), mimetype="text/csv", headers={
            "Content-Disposition": f"attachment; filename={report_type}-report.csv"
        })

    pdf = create_simple_pdf(f"{report_type.title()} Report", [headers] + rows)
    return Response(pdf, mimetype="application/pdf", headers={
        "Content-Disposition": f"attachment; filename={report_type}-report.pdf"
    })

# CREATE MAINTENANCE
@app.route("/create_maintenance", methods=["POST"])
def create_maintenance():
    equipment_id = request.json.get("equipmentId")
    date = request.json.get("date")
    description = request.json.get("description")
    maintenance_type = request.json.get("maintenanceType")

    if not equipment_id or not date or not description or not maintenance_type:
        return jsonify({"message": "Equipment, date, description, and type are required."}), HTTPStatus.BAD_REQUEST

    valid_types = [e.value for e in MaintenanceType]
    if maintenance_type not in valid_types:
        return jsonify({"message": f"Invalid maintenance type. Must be one of: {valid_types}"}), HTTPStatus.BAD_REQUEST

    equipment = Equipment.query.get(equipment_id)
    if not equipment:
        return jsonify({"message": "Equipment not found. The maintenance record was not created."}), HTTPStatus.NOT_FOUND
    if equipment.equipment_state in (EquipmentState.UNDER_MAINTENANCE.value, EquipmentState.ARCHIVED.value):
        return jsonify({"message": "Maintenance cannot be registered while the equipment is under maintenance or archived."}), HTTPStatus.BAD_REQUEST

    from datetime import date as date_class
    try:
        parsed_date = date_class.fromisoformat(date)
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD."}), HTTPStatus.BAD_REQUEST

    new_maintenance = Maintenance(
        equipment_id=equipment_id,
        date=parsed_date,
        description=description,
        maintenance_type=maintenance_type
    )

    try:
        db.session.add(new_maintenance)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": str(e)}), HTTPStatus.BAD_REQUEST

    return jsonify({"message": "Maintenance record created!"}), HTTPStatus.CREATED

# UPDATE MAINTENANCE
@app.route("/update_maintenance/<int:maintenance_id>", methods=["PATCH"])
def update_maintenance(maintenance_id):
    maintenance = Maintenance.query.get(maintenance_id)

    if not maintenance:
        return jsonify({"message": "Maintenance record not found"}), HTTPStatus.NOT_FOUND

    data = request.json

    valid_types = [e.value for e in MaintenanceType]
    if "maintenanceType" in data and data["maintenanceType"] not in valid_types:
        return jsonify({"message": f"Invalid maintenance type. Must be one of: {valid_types}"}), HTTPStatus.BAD_REQUEST

    if "date" in data:
        from datetime import date as date_class
        try:
            data["date"] = date_class.fromisoformat(data["date"])
        except ValueError:
            return jsonify({"message": "Invalid date format. Use YYYY-MM-DD."}), HTTPStatus.BAD_REQUEST
        maintenance.date = data["date"]

    equipment_id = data.get("equipmentId", maintenance.equipment_id)
    equipment = Equipment.query.get(equipment_id)
    if not equipment:
        return jsonify({"message": "Equipment not found. The maintenance record was not updated."}), HTTPStatus.NOT_FOUND
    if equipment.equipment_state in (EquipmentState.UNDER_MAINTENANCE.value, EquipmentState.ARCHIVED.value):
        return jsonify({"message": "Maintenance cannot be updated while the equipment is under maintenance or archived."}), HTTPStatus.BAD_REQUEST

    maintenance.equipment_id = equipment_id
    maintenance.description = data.get("description", maintenance.description)
    maintenance.maintenance_type = data.get("maintenanceType", maintenance.maintenance_type)

    db.session.commit()

    return jsonify({"message": "Maintenance record updated."})

# DELETE MAINTENANCE
@app.route("/delete_maintenance/<int:maintenance_id>", methods=["DELETE"])
def delete_maintenance(maintenance_id):
    maintenance = Maintenance.query.get(maintenance_id)

    if not maintenance:
        return jsonify({"message": "Maintenance record not found"}), HTTPStatus.NOT_FOUND

    db.session.delete(maintenance)
    db.session.commit()

    return jsonify({"message": "Maintenance record deleted!"})

# RUN APP
if __name__ == "__main__":
    
    with app.app_context(): # Context of the application
        db.create_all()

    app.run(debug=True)