from config import db
from enum import Enum

class EquipmentState(Enum) : 

    OPERATIONAL = "OPERATIONAL"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"
    DAMAGED = "DAMAGED"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"

class EquipmentType(Enum) :

    FIREWALL = "FIREWALL"
    ROUTER = "ROUTER"
    SWITCH = "SWITCH"
    SERVER = "SERVER"
    OTHER = "OTHER" 

class MaintenanceType(Enum) :
    
    PREVENTIVE = "PREVENTIVE"
    CORRECTIVE = "CORRECTIVE"
    SOFTWARE_UPDATE = "SOFTWARE_UPDATE"
    REPLACEMENT = "REPLACEMENT"
    INSPECTION = "INSPECTION"

# database model represented as a python class
# Responsable / User responsible for the equipment registry in the app
class Contact(db.Model) :
    
    id = db.Column(db.Integer, primary_key = True) # primary key for database
    first_name = db.Column(db.String(80), unique=False, nullable=False)
    last_name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(80), unique=False, nullable=False)
    is_admin = db.Column(db.Integer, default=0) # 1 = Admin, 0 = User

    # Converts data above to JSON to send to API
    def to_json(self):
        return {
            "id" : self.id,
            "firstName": self.first_name,
            "lastName" : self.last_name,
            "email" : self.email,
            "role" : self.role,
            "isAdmin" : self.is_admin
        }

# Equipment database    
class Equipment(db.Model) : 
    
    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.String(80), unique=False, nullable=False)
    model = db.Column(db.String(80), unique=False, nullable=False)
    serial_number = db.Column(db.String(10), unique=True, nullable=False)
    equipment_state = db.Column(db.String(80), nullable=False, default="OPERATIONAL")
    assigned_to = db.Column(db.Integer, db.ForeignKey("contact.id"), nullable=True)

    # Relationships
    location_details = db.relationship("EquipmentLocation", backref="equipment", uselist=False, cascade="all, delete-orphan")
    assigned_contact = db.relationship("Contact", backref="equipment")

    def to_json(self):
        return {
            "id" : self.id,
            "type" : self.type,
            "model" : self.model,
            "serialNumber" : self.serial_number,
            "equipmentState" : self.equipment_state,
            "assignedTo" : self.assigned_contact.to_json() if self.assigned_contact else None,
            "locationDetails" : self.location_details.to_json() if self.location_details else None
        }

class EquipmentLocation(db.Model) :

    id = db.Column(db.Integer, db.ForeignKey("equipment.id"), primary_key=True)
    floor = db.Column(db.Integer, nullable=False)
    room_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200), nullable=True)

    def to_json(self):
        return {
            "id" : self.id,
            "floor" : self.floor,
            "roomNumber" : self.room_number,
            "description" : self.description
        }

class Maintenance(db.Model) :

    id = db.Column(db.Integer, primary_key=True) # primary key for Maintenance records
    # Foreign key to associate maintenance record with specific equipment
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    maintenance_type = db.Column(db.String(80), nullable=False)

    equipment = db.relationship("Equipment", backref="maintenance_records")

    def to_json(self):
        return {
            "id" : self.id,
            "equipmentId" : self.equipment_id,
            "equipmentName" : f"{self.equipment.type} - {self.equipment.model} ({self.equipment.serial_number})" if self.equipment else None,
            "date" : self.date.isoformat(),
            "description" : self.description,
            "maintenanceType" : self.maintenance_type
        }