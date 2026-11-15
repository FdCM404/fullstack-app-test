from config import db
from enum import Enum
from datetime import datetime
import json

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
    access = db.relationship("ContactAccess", backref="contact", uselist=False, cascade="all, delete-orphan")

    # Converts data above to JSON to send to API
    def to_json(self):
        return {
            "id" : self.id,
            "firstName": self.first_name,
            "lastName" : self.last_name,
            "email" : self.email,
            "role" : self.role,
            "isAdmin" : self.is_admin
            ,"permissions": self.access.permissions_list if self.access else []
        }

class ContactAccess(db.Model) :

    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey("contact.id"), unique=True, nullable=False)
    permissions = db.Column(db.Text, nullable=False, default="[]")

    @property
    def permissions_list(self):
        try:
            return json.loads(self.permissions)
        except (TypeError, json.JSONDecodeError):
            return []

    @permissions_list.setter
    def permissions_list(self, value):
        self.permissions = json.dumps(value)

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
            ,"networkParameters" : self.network_parameters.to_json() if self.network_parameters else None
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

class EquipmentNetwork(db.Model) :

    id = db.Column(db.Integer, db.ForeignKey("equipment.id"), primary_key=True)
    ip_address = db.Column(db.String(45), nullable=True)
    mac_address = db.Column(db.String(17), nullable=True)
    hostname = db.Column(db.String(120), nullable=True)
    vlan = db.Column(db.String(20), nullable=True)

    equipment = db.relationship("Equipment", backref=db.backref("network_parameters", uselist=False))

    def to_json(self):
        return {
            "ipAddress": self.ip_address,
            "macAddress": self.mac_address,
            "hostname": self.hostname,
            "vlan": self.vlan
        }

class EquipmentChangeHistory(db.Model) :

    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)
    changed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    field_name = db.Column(db.String(80), nullable=False)
    previous_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    changed_by = db.Column(db.Integer, db.ForeignKey("contact.id"), nullable=True)

    equipment = db.relationship(
        "Equipment",
        backref=db.backref("change_history", cascade="all, delete-orphan"),
    )
    user = db.relationship("Contact")

    def to_json(self):
        return {
            "id": self.id,
            "changedAt": self.changed_at.isoformat(),
            "field": self.field_name,
            "previousValue": self.previous_value,
            "newValue": self.new_value,
            "changedBy": self.user.to_json() if self.user else None
        }

class Maintenance(db.Model) :

    id = db.Column(db.Integer, primary_key=True) # primary key for Maintenance records
    # Foreign key to associate maintenance record with specific equipment
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    maintenance_type = db.Column(db.String(80), nullable=False)

    equipment = db.relationship(
        "Equipment",
        backref=db.backref("maintenance_records", cascade="all, delete-orphan"),
    )

    def to_json(self):
        return {
            "id" : self.id,
            "equipmentId" : self.equipment_id,
            "equipmentName" : f"{self.equipment.type} - {self.equipment.model} ({self.equipment.serial_number})" if self.equipment else None,
            "date" : self.date.isoformat(),
            "description" : self.description,
            "maintenanceType" : self.maintenance_type
        }