# CRUD APP - Create, Remove, Update, Delete

from flask import request, jsonify
from config import app, db
from models import Contact, Equipment, EquipmentType, EquipmentState, Maintenance, MaintenanceType
from enum import IntEnum

class HTTPStatus(IntEnum):
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404

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

    return jsonify({"message": "Login successful!", "user": contact.to_json()})

# REGISTER
@app.route("/register", methods=["POST"])
def register():
    first_name = request.json.get("firstName")
    last_name = request.json.get("lastName")
    email = request.json.get("email")
    password = request.json.get("password")
    role = request.json.get("role", "User")

    if not first_name or not last_name or not email or not password:
        return jsonify({"message": "All fields are required."}), HTTPStatus.BAD_REQUEST

    existing = Contact.query.filter_by(email=email).first()
    if existing:
        return jsonify({"message": "Email already registered."}), HTTPStatus.BAD_REQUEST

    new_contact = Contact(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        role=role,
        is_admin=0
    )

    try:
        db.session.add(new_contact)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": str(e)}), HTTPStatus.BAD_REQUEST

    return jsonify({"message": "Account created!", "user": new_contact.to_json()}), HTTPStatus.CREATED

# CONTACT ROUTES 
@app.route("/contacts", methods=["GET"])
def get_contacts():
    contacts = Contact.query.all() # SELECT * FROM CONTACTS
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

    if not first_name or not last_name or not email or not role:
        return jsonify({"message": "You need to include full name, email, and role."}), HTTPStatus.BAD_REQUEST
    
    new_contact = Contact(first_name=first_name, last_name=last_name, email=email, password=password, role=role, is_admin=is_admin)

    try:
        db.session.add(new_contact) # update database
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
    contact.first_name = data.get("firstName", contact.first_name)
    contact.last_name = data.get("lastName", contact.last_name)
    contact.email = data.get("email", contact.email)
    contact.role = data.get("role", contact.role)

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
    equipment = Equipment.query.all()
    json_equipment = list(map(lambda x: x.to_json(), equipment))
    return jsonify({"equipment": json_equipment})

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

# UPDATE EQUIPMENT
@app.route("/update_equipment/<int:equipment_id>", methods=["PATCH"])
def update_equipment(equipment_id):
    equipment = Equipment.query.get(equipment_id)

    if not equipment:
        return jsonify({"message": "Equipment not found"}), HTTPStatus.NOT_FOUND

    data = request.json

    valid_types = [e.value for e in EquipmentType]
    valid_states = [e.value for e in EquipmentState]

    if "type" in data and data["type"] not in valid_types:
        return jsonify({"message": f"Invalid type. Must be one of: {valid_types}"}), HTTPStatus.BAD_REQUEST

    if "equipmentState" in data and data["equipmentState"] not in valid_states:
        return jsonify({"message": f"Invalid state. Must be one of: {valid_states}"}), HTTPStatus.BAD_REQUEST

    equipment.type = data.get("type", equipment.type)
    equipment.model = data.get("model", equipment.model)
    equipment.serial_number = data.get("serialNumber", equipment.serial_number)
    equipment.equipment_state = data.get("equipmentState", equipment.equipment_state)
    equipment.assigned_to = data.get("assignedTo", equipment.assigned_to)

    db.session.commit()

    return jsonify({"message": "Equipment updated."})

# DELETE EQUIPMENT
@app.route("/delete_equipment/<int:equipment_id>", methods=["DELETE"])
def delete_equipment(equipment_id):
    equipment = Equipment.query.get(equipment_id)

    if not equipment:
        return jsonify({"message": "Equipment not found"}), HTTPStatus.NOT_FOUND

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
        return jsonify({"message": "Equipment not found."}), HTTPStatus.NOT_FOUND

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

    maintenance.equipment_id = data.get("equipmentId", maintenance.equipment_id)
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