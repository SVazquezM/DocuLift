import os
import io
import html
import logging
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, make_response
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from email_validator import validate_email, EmailNotValidError
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from datetime import datetime

from helpers import login_required, get_technical_specs, get_certificates

logger = logging.getLogger(__name__)

# Configure application
app = Flask(__name__)

# Custom filter

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQlite database
db = SQL("sqlite:///project.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Main page"""
    query = """
            SELECT id, order_number, rae, lift_address, created_at, updated_at
            FROM projects_test
            WHERE user_id = ?
            ORDER BY COALESCE(updated_at, created_at) DESC, id DESC
            """

    query_2 = """
              SELECT code, label FROM modification_types
              """

    query_3 = """
              SELECT code, label FROM applicable_norms
              """

    query_4 = """
              SELECT code, label FROM legalization_process
              """

    projects =  db.execute(query, session["user_id"])
    modification_types = db.execute(query_2)
    applicable_norms = db.execute(query_3)
    legalization_process = db.execute(query_4)
    technical_specs = get_technical_specs()
    certificates = get_certificates()
    print("certificates", certificates);

    return render_template("layout9.html", projects=projects, modification_types=modification_types,
                            applicable_norms=applicable_norms, legalization_process=legalization_process,
                            technical_specs=technical_specs, certificates=certificates)


@app.route("/login", methods=["POST"])
def login():
    """Log user in"""

    email = request.form.get("loginEmail")
    password = request.form.get("loginPassword")

    errors = {}

    if not email:
        errors["loginEmail"] = "Campo requerido"
    else:
        try:
            emailinfo = validate_email(email, check_deliverability=False)
            normalized_email = emailinfo.normalized
        except EmailNotValidError:
            errors["loginEmail"] = "Correo electrónico no válido"
    
    if not password:
        errors["loginPassword"] = "Campo requerido"
    
    if errors:
        return jsonify({
            "success": False,
            "fieldErrors": errors
        }), 403
    
    try:
        rows = db.execute("SELECT * FROM users WHERE email = ?", normalized_email)
        if len(rows) != 1:
            return jsonify({
                "success": False,
                "message": "Correo electrónico y/o contraseña incorrectos."
            }), 403
        elif not check_password_hash(rows[0]["password_hash"], password):
            return jsonify({
                "success": False,
                "message": "Contraseña incorrecta."
            }), 403
        session["user_id"] = rows[0]["id"]
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": "Ha ocurrido un error al procesar la solicitud"}), 500


@app.route("/register", methods=["POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()
    
    email = request.form.get("registerEmail")
    name = request.form.get("registerUser")
    password = request.form.get("registerPassword")

    errors = {}

    if not email:
        errors["registerEmail"] = "Campo requerido"
    else:
        try:
            emailinfo = validate_email(email, check_deliverability=False)
            normalized_email = emailinfo.normalized

            rows = db.execute("SELECT 1 FROM users WHERE email = ?", normalized_email)
            if len(rows) != 0:
                errors["registerEmail"] = "Ya existe una cuenta con el correo electrónico introducido"
        except EmailNotValidError:
            errors["registerEmail"] = "Correo electrónico no válido"

    if not name:
        errors["registerUser"] = "Campo requerido"
    elif len(name) < 3:
        errors["registerUser"] = "El nombre debe tener al menos 3 caracteres"

    if not password:
        errors["registerPassword"] = "Campo requerido"
    elif len(password) < 9:
        errors["registerPassword"] = "Contraseña debe tener al menos 9 caracteres"
    else:
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        if not (has_lower and has_upper):
            errors["registerPassword"] = "Contraseña debe contener letras mayúsculas y minúsculas"
        elif not any(c.isdigit() for c in password):
            errors["registerPassword"] = "Contraseña debe contener al menos un dígito numérico"
        else:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                errors["registerPassword"] = "Contraseña debe contener al menos un carácter especial"

    if errors:
        return jsonify({
            "success": False,
            "fieldErrors": errors
        }), 400
    try:
        user_id = db.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            name, normalized_email, generate_password_hash(password)
        )
        session["user_id"] = user_id
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": "Ha ocurrido un error al procesar la solicitud"}), 500


@app.route("/validate-field-public", methods=["POST"])
def validate_field_public():
    """Validate individual field"""
    
    data = request.get_json()
    field = data.get("field")
    value = data.get("value")
    
    if not value:
        return jsonify({"success": False, "message": "Campo requerido"})

    if field == "loginEmail":
        try:
            emailinfo = validate_email(value, check_deliverability=False)
            return jsonify({"success": True, "message": ""})
        except EmailNotValidError:
            return jsonify({"success": False, "message": "Correo electrónico no válido"})
            
    if field == "loginPassword":
        return jsonify({"success": True, "message": ""})
    
    if field == "email":
        try:
            emailinfo = validate_email(value, check_deliverability=False)
            normalized_email = emailinfo.normalized
            rows = db.execute("SELECT * FROM users WHERE email = ?", normalized_email)
            if len(rows) != 0:
                return jsonify({"success": False, "message": "Ya existe una cuenta con el correo electrónico introducido"})
            return jsonify({"success": True, "message": ""})
        except EmailNotValidError:
            return jsonify({"success": False, "message": "Correo electrónico no válido"})
    
    elif field == "username":
        if len(value) < 3:
            return jsonify({"success": False, "message": "El nombre debe tener al menos 3 caracteres"})
        # Aquí podrías verificar si el usuario ya existe en la base de datos
        return jsonify({"success": True, "message": ""})
    
    elif field == "password":
        rule_errors = []
        # Regla: longitud mínima 9
        if len(value) < 9:
            rule_errors.append("len")
        # Regla: mayúsculas y minúsculas
        has_upper = any(c.isupper() for c in value)
        has_lower = any(c.islower() for c in value)
        if not (has_upper and has_lower):
            rule_errors.append("case")
        # Regla: al menos un dígito
        if not any(c.isdigit() for c in value):
            rule_errors.append("digit")
        # Regla: al menos un caracter especial
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in value):
            rule_errors.append("special")

        return jsonify({"success": len(rule_errors) == 0, "message": rule_errors})
    
    return jsonify({"success": False, "message": "Campo no válido"})

@app.route("/validate-field", methods=["POST"])
@login_required

def validate_field():
    """Validate indivial fiel login required"""

    data = request.get_json()
    field = data.get("field")
    value = data.get("value")
    project_id = data.get("project_id") or ""

    if not value:
        return jsonify({"success": False, "message":"Campo requerido"})
    
    elif field == "orderNumber":
        
        if not project_id:
            rows = db.execute(
                "SELECT * FROM projects_test WHERE user_id = ? AND order_number = ?",
                session["user_id"], value
            )
            if len(rows) != 0:
                return jsonify({"success": False, "message": "Nº de orden ya en uso"})

            return jsonify({"success": True, "message": ""})
        
        if project_id.isdigit():
            rows = db.execute(
                "SELECT 1 FROM projects_test WHERE user_id = ? AND order_number = ? AND id != ?",
                session["user_id"], value, int(project_id)
            )
            if len(rows) != 0:
                return jsonify({"success": False, "message": "Nº de orden ya en uso"})

        return jsonify({"success": True, "message": ""})
    
    elif field == "clientZip" or  field == "liftZip":
        if not (value.isdigit() and len(value) == 5):
            return jsonify({"success": False, "message": "El código postal debe tener 5 dígitos"})
    
    elif field == "modification_types":   
        
        # Verificar que los códigos existan en la base de datos
        try:
            placeholders = ','.join('?' * len(value))
            rows = db.execute(f"SELECT code FROM {field} WHERE code IN ({placeholders})", *value)
            if len(rows) != len(value):
                return jsonify({"success": False, "message": "Tipo de modificación inválido"})
        except Exception:
            return jsonify({"success": False, "message": "Error al validar tipos de modificación"})

    elif field == "applicable_norms":

        try:
            placeholders = ','.join('?' * len(value))
            rows = db.execute(f"SELECT code FROM {field} WHERE code IN ({placeholders})", *value)
            if len(rows) != len(value):
                return jsonify({"success": False, "message": "Normativa aplicable inválida"})
        except Exception:
            return jsonify({"success": False, "message": "Error al validar normativas aplicables"})
    
    elif field == "legalization_process":

        try:
            rows = db.execute(f"SELECT code FROM legalization_process WHERE code = ?", value)
            if len(rows) != len(value):
                return jsonify({"success": False, "message": "Proceso de legalización inválido"})
        except Exception:
            return jsonify({"success": False, "message": "Error al validar el proceso de legalización"})
    
    return jsonify({"success": True, "message": ""})

@app.route("/add-project", methods=["POST"])
@login_required
def add_project():
    """Add new project"""
    order = request.form.get("orderNumber").strip()
    rae = request.form.get("rae").strip()
    client_name = request.form.get("clientName").strip()
    client_nif = request.form.get("clientNIF").strip()
    client_address = request.form.get("clientAddress").strip()
    client_city = request.form.get("clientCity").strip()
    client_zip = request.form.get("clientZip").strip()
    lift_address = request.form.get("liftAddress").strip()
    lift_city = request.form.get("liftCity").strip()
    lift_zip = request.form.get("liftZip").strip()
    mod_types = request.form.getlist('modification_types')
    norms = request.form.getlist('applicable_norms')
    process = request.form.get('legalization_process')
    exam_type = request.form.get(('examType').strip() or "")
    oca = request.form.get(('oca').strip() or "")
    qms = request.form.get(('qualityManagementSystem').strip() or "")
    nominal_load = request.form.get(("nominalLoad").strip() or "")
    speed = request.form.get(("speed").strip() or "")
    machine_room = request.form.get(("machineRoomInput").strip() or "")
    passengers = request.form.get(("passengers").strip() or "")
    control_system = request.form.get(("controlSystemInput").strip() or "")
    cab_dimensions = request.form.get(("cabDimensions").strip() or "")
    stops = request.form.get(("stops").strip() or "")
    nominal_tension = request.form.get(("nominalTensionInput").strip() or "")
    door_type = request.form.get(("doorTypeInput").strip() or "")
    travel = request.form.get(("travel").strip() or "")
    nominal_power = request.form.get(("nominalPower").strip() or "")
    door_size = request.form.get(("doorSize").strip() or "")
    num_cable = request.form.get(("numCable").strip() or "")
    nominal_intensity = request.form.get(("nominalIntensity").strip() or "")
    cable_diameter = request.form.get(("cableDiameterInput").strip() or "")
    ratio = request.form.get(("ratioInput").strip() or "")
    cab_mass = request.form.get(("cabMass").strip() or "")
    cab_rails = request.form.get(("cabRailsInput").strip() or "")
    cw_mass = request.form.get(("cwMass").strip() or "")
    cw_rails = request.form.get(("cwRailsInput").strip() or "")
    locking_device1 = request.form.get(("lockingDevice1Input").strip() or "")
    locking_device2 = request.form.get(("lockingDevice2Input").strip() or "")
    machine_brake = request.form.get(("machineBrakeInput").strip() or "")
    cab_parachute = request.form.get(("cabParachuteInput").strip() or "")
    cw_parachute = request.form.get(("cwParachuteInput").strip() or "")
    cab_speed_governor = request.form.get(("cabSpeedGovernorInput").strip() or "")
    cw_speed_governor = request.form.get(("cwSpeedGovernorInput").strip() or "")
    cab_buffer = request.form.get(("cabBufferInput").strip() or "")
    cw_buffer = request.form.get(("cwBufferInput").strip() or "")
    safety_circuit = request.form.get(("safetyCircuitInput").strip() or "")
    ucm_detect = request.form.get(("ucmDETECTInput").strip() or "")
    ucm_act = request.form.get(("ucmACTInput").strip() or "")
    ucm_stop = request.form.get(("ucmSTOPInput").strip() or "")
    errors = {}

    if not order:
        errors["orderNumber"] = "Campo requerido"
    else:
        rows = db.execute(
            "SELECT * FROM projects_test WHERE user_id = ? AND order_number = ?",
            session["user_id"], order
        )
        if len(rows) != 0:
            errors["orderNumber"] = "Nº de orden ya en uso"
    
    if not rae:
        errors["rae"] = "Campo requerido"
    
    if not client_name:
        errors["clientName"] = "Campo requerido"
    
    if not client_nif:
        errors["clientNIF"] = "Campo requerido"
    if not client_address:
        errors["clientAddress"] = "Campo requerido"
    
    if not client_city:
        errors["clientCity"] = "Campo requerido"
    
    if not client_zip:
        errors["clientZip"] = "Campo requerido"
    elif not (client_zip.isdigit() and len(client_zip) == 5):
        errors["clientZip"] = "El código postal debe tener 5 dígitos"
    
    if not lift_address:
        errors["liftAddress"] = "Campo requerido"

    if not lift_city:
        errors["liftCity"] = "Campo requerido"
    
    if not lift_zip:
        errors["liftZip"] = "Campo requerido"
    elif not (lift_zip.isdigit() and len(lift_zip) == 5):
        errors["liftZip"] = "El código postal debe tener 5 dígitos" 

    if not mod_types:
        errors["ModificationTypesInput"] = "Campo requerido"   
    else:
        placeholders = ','.join('?' *  len(mod_types))
        rows = db.execute(f"SELECT code FROM modification_types WHERE code IN ({placeholders})", *mod_types)
        if len(rows) != len(mod_types):
            errors["ModificationTypesInput"] = "Tipo de modificación inválido" 

    if not norms:
        errors["AplicableNormsInput"] = "Campo requerido"
    else:
        placeholders = ','.join('?' * len(norms))
        rows = db.execute(f"SELECT code FROM applicable_norms WHERE code IN ({placeholders})", *norms)
        if len(rows) != len(norms):
            errors["AplicableNormsInput"] = "Normativa aplicable inválida"
    
    if not process:
        errors["LegalizationProcessInput"] = "Campo requerido"
    else:
        rows = db.execute("SELECT code FROM legalization_process WHERE code = ?", process)
        if len(rows) != 1:
            errors["LegalizationProcessInput"] = "Proceso de legalización inválido"

    if errors:
        return jsonify({
            "success": False,
            "fieldErrors": errors
        }), 400
    
    try:
        project_id = db.execute("""
            INSERT INTO projects_test (user_id, order_number, rae, client_name, 
                                    client_nif, client_address, client_city, client_zip, 
                                    lift_address, lift_city, lift_zip, exam_type, oca, qms,
                                    nominal_load, speed, machine_room, passengers, control_system,
                                    cab_dimensions, stops, nominal_tension, door_type, travel,
                                    nominal_power, door_size, num_cable, nominal_intensity,
                                    cable_diameter, ratio, cab_mass, cab_rails, cw_mass, cw_rails,
                                    locking_device1, locking_device2, machine_brake, cab_parachute, cw_parachute,
                                    cab_speed_governor, cw_speed_governor, cab_buffer, cw_buffer, safety_circuit,
                                    ucm_detect, ucm_act, ucm_stop,
                                    created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,    session["user_id"], order, rae, client_name, client_nif, client_address, 
                client_city, client_zip, lift_address, lift_city, lift_zip, exam_type, oca, qms,
                nominal_load, speed, machine_room, passengers, control_system, cab_dimensions, stops,
                nominal_tension, door_type, travel, nominal_power, door_size, num_cable, nominal_intensity,
                cable_diameter, ratio, cab_mass, cab_rails, cw_mass, cw_rails, locking_device1, locking_device2,
                machine_brake, cab_parachute, cw_parachute, cab_speed_governor, cw_speed_governor, cab_buffer, cw_buffer, 
                safety_circuit, ucm_detect, ucm_act, ucm_stop)

        if mod_types:
            placeholders = ','.join('?' * len(mod_types))
            rows = db.execute(f"SELECT id, code FROM modification_types WHERE code IN ({placeholders})", *mod_types)
            code_to_id = {row['code']: row['id'] for row in rows}

            for code in mod_types:
                mt_id = code_to_id[code]
                db.execute("INSERT INTO project_modification_types (project_id,modification_type_id) VALUES (?, ?)",
                           project_id, mt_id)

        if norms:
            placeholders = ','.join('?' * len(norms))
            rows = db.execute(f"SELECT id, code FROM applicable_norms WHERE code IN ({placeholders})", *norms)
            norm_code_to_id = {row['code']: row['id'] for row in rows}
            
            for code in norms:
                norm_id = norm_code_to_id[code]
                db.execute("INSERT INTO project_applicable_norms (project_id,applicable_norm_id) VALUES (?, ?)",
                           project_id, norm_id)
        
        if process:
            rows = db.execute("SELECT id FROM legalization_process WHERE code = ?", process)
            process_id = rows[0]['id']

            db.execute("INSERT INTO project_legalization_process (project_id, legalization_process_id) VALUES (?, ?)",
                       project_id, process_id)
        
        new_project = db.execute(
            """SELECT id, order_number, rae, lift_address, created_at, updated_at
            FROM projects_test WHERE id = ?""",
            project_id
        )[0]
        return jsonify({"success": True, "project": new_project})
    
    except Exception as e:
        return jsonify({"success": False, "message": "Ha ocurrido un error al procesar su solicitud"}), 500

@app.route("/update-project", methods=["POST"])
@login_required
def update_project():
    """Add new project"""
    project_id = request.form.get("id").strip()
    order = request.form.get("orderNumber").strip()
    rae = request.form.get("rae").strip()
    client_name = request.form.get("clientName").strip()
    client_nif = request.form.get("clientNIF").strip()
    client_address = request.form.get("clientAddress").strip()
    client_city = request.form.get("clientCity").strip()
    client_zip = request.form.get("clientZip").strip()
    lift_address = request.form.get("liftAddress").strip()
    lift_city = request.form.get("liftCity").strip()
    lift_zip = request.form.get("liftZip").strip()
    mod_types = request.form.getlist('modification_types')
    norms = request.form.getlist('applicable_norms')
    process = request.form.get('legalization_process')
    exam_type = request.form.get(("examType").strip() or "")
    oca = request.form.get(("oca").strip() or "")
    qms = request.form.get(("qualityManagementSystem").strip() or "")
    nominal_load = request.form.get(("nominalLoad").strip() or "")
    speed = request.form.get(("speed").strip() or "")
    machine_room = request.form.get(("machineRoomInput").strip() or "")
    passengers = request.form.get(("passengers").strip() or "")
    control_system = request.form.get(("controlSystemInput").strip() or "")
    cab_dimensions = request.form.get(("cabDimensions").strip() or "")
    stops = request.form.get(("stops").strip() or "")
    nominal_tension = request.form.get(("nominalTensionInput").strip() or "")
    door_type = request.form.get(("doorTypeInput").strip() or "")
    travel = request.form.get(("travel").strip() or "")
    nominal_power = request.form.get(("nominalPower").strip() or "")
    door_size = request.form.get(("doorSize").strip() or "")
    num_cable = request.form.get(("numCable").strip() or "")
    nominal_intensity = request.form.get(("nominalIntensity").strip() or "")
    cable_diameter = request.form.get(("cableDiameterInput").strip() or "")
    ratio = request.form.get(("ratioInput").strip() or "")
    cab_mass = request.form.get(("cabMass").strip() or "")
    cab_rails = request.form.get(("cabRailsInput").strip() or "")
    cw_mass = request.form.get(("cwMass").strip() or "")
    cw_rails = request.form.get(("cwRailsInput").strip() or "")
    locking_device1 = request.form.get(("lockingDevice1Input").strip() or "")
    locking_device2 = request.form.get(("lockingDevice2Input").strip() or "")
    machine_brake = request.form.get(("machineBrakeInput").strip() or "")
    cab_parachute = request.form.get(("cabParachuteInput").strip() or "")
    cw_parachute = request.form.get(("cwParachuteInput").strip() or "")
    cab_speed_governor = request.form.get(("cabSpeedGovernorInput").strip() or "")
    cw_speed_governor = request.form.get(("cwSpeedGovernorInput").strip() or "")
    cab_buffer = request.form.get(("cabBufferInput").strip() or "")
    cw_buffer = request.form.get(("cwBufferInput").strip() or "")
    safety_circuit = request.form.get(("safetyCircuitInput").strip() or "")
    ucm_detect = request.form.get(("ucmDETECTInput").strip() or "")
    ucm_act = request.form.get(("ucmACTInput").strip() or "")
    ucm_stop = request.form.get(("ucmSTOPInput").strip() or "")

    errors = {}

    if not project_id or not project_id.isdigit():
        return jsonify({"success": False, "message": "Solicitud inválida"}), 400
    # Confirmar que existe y pertenece al usuario
    rows = db.execute("SELECT 1 FROM projects_test WHERE id = ? AND user_id = ? LIMIT 1",
                      int(project_id), session["user_id"])
    if len(rows) == 0:
        return jsonify({"success": False, "message": "Proyecto no encontrado"}), 404

    if not order:
        errors["orderNumber"] = "Campo requerido"
    else:
        rows = db.execute(
            "SELECT 1 FROM projects_test WHERE user_id = ? AND order_number = ? AND id != ?",
            session["user_id"], order, int(project_id)
        )
        if len(rows) != 0:
            errors["orderNumber"] = "Nº de orden ya en uso"
    
    if not rae:
        errors["rae"] = "Campo requerido"
    
    if not client_name:
        errors["clientName"] = "Campo requerido"
    
    if not client_nif:
        errors["clientNIF"] = "Campo requerido"
    if not client_address:
        errors["clientAddress"] = "Campo requerido"
    
    if not client_city:
        errors["clientCity"] = "Campo requerido"
    
    if not client_zip:
        errors["clientZip"] = "Campo requerido"
    elif not (client_zip.isdigit() and len(client_zip) == 5):
        errors["clientZip"] = "El código postal debe tener 5 dígitos"
    
    if not lift_address:
        errors["liftAddress"] = "Campo requerido"

    if not lift_city:
        errors["liftCity"] = "Campo requerido"
    
    if not lift_zip:
        errors["liftZip"] = "Campo requerido"
    elif not (lift_zip.isdigit() and len(lift_zip) == 5):
        errors["liftZip"] = "El código postal debe tener 5 dígitos"    
    
    if not mod_types:
        errors["ModificationTypesInput"] = "Campo requerido"
    else:
        placeholders = ','.join('?' * len(mod_types))
        rows = db.execute(f"SELECT code FROM modification_types WHERE code IN ({placeholders})", *mod_types)
        if len(rows) != len(mod_types):
            errors["ModificationTypesInput"] = "Tipo de modificación inválido"
    
    if not norms:
        errors["AplicableNormsInput"] = "Campo requerido"
    else:
        placeholders = ','.join('?' * len(norms))
        rows = db.execute(f"SELECT code FROM applicable_norms WHERE code IN ({placeholders})", *norms)
        if len(rows) != len(norms):
            errors["AplicableNormsInput"] = "Normativa aplicable inválido"
    
    if not process:
        errors["LegalizationProcessInput"] = "Campo requerido"
    else:
        rows = db.execute("SELECT code FROM legalization_process WHERE code = ?", process)
        if len(rows) != 1:
            errors["LegalizationProcessInput"] = "Proceso de legalización inválido"
    
    if errors:
        return jsonify({
            "success": False,
            "fieldErrors": errors
        }), 400

    try:
        db.execute(
            """
            UPDATE projects_test
            SET order_number = ?,
                rae = ?,
                client_name = ?,
                client_nif = ?,
                client_address = ?,
                client_city = ?,
                client_zip = ?,
                lift_address = ?,
                lift_city = ?,
                lift_zip = ?,
                exam_type = ?,
                oca = ?,
                qms = ?,
                nominal_load = ?,
                speed = ?,
                machine_room = ?,
                passengers = ?,
                control_system = ?,
                cab_dimensions = ?,
                stops = ?,
                nominal_tension = ?,
                door_type = ?,
                travel = ?,
                nominal_power = ?,
                door_size = ?,
                num_cable = ?,
                nominal_intensity = ?,
                cable_diameter = ?,
                ratio = ?,
                cab_mass = ?,
                cab_rails = ?,
                cw_mass = ?,
                cw_rails = ?,
                locking_device1 = ?,
                locking_device2 = ?,
                machine_brake = ?,
                cab_parachute = ?,
                cw_parachute = ?,
                cab_speed_governor = ?,
                cw_speed_governor = ?,
                cab_buffer = ?,
                cw_buffer = ?,
                safety_circuit = ?,
                ucm_detect = ?,
                ucm_act = ?,
                ucm_stop = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            order,
            rae,
            client_name,
            client_nif,
            client_address,
            client_city,
            client_zip,
            lift_address,
            lift_city,
            lift_zip,
            exam_type,
            oca,
            qms,
            nominal_load,
            speed,
            machine_room,
            passengers,
            control_system,
            cab_dimensions,
            stops,
            nominal_tension,
            door_type,
            travel,
            nominal_power,
            door_size,
            num_cable,
            nominal_intensity,
            cable_diameter,
            ratio,
            cab_mass,
            cab_rails,
            cw_mass,
            cw_rails,
            locking_device1,
            locking_device2,
            machine_brake,
            cab_parachute,
            cw_parachute,
            cab_speed_governor,
            cw_speed_governor,
            cab_buffer,
            cw_buffer,
            safety_circuit,
            ucm_detect,
            ucm_act,
            ucm_stop,
            int(project_id),
        )

        if mod_types:
            db.execute("DELETE FROM project_modification_types WHERE project_id = ?", project_id)
            placeholders = ','.join('?' * len(mod_types))
            rows = db.execute(f"SELECT id, code FROM modification_types WHERE code IN ({placeholders})", *mod_types)
            code_to_id = {row['code']: row['id'] for row in rows}

            for code in mod_types:
                mt_id = code_to_id[code]
                db.execute("INSERT INTO project_modification_types (project_id,modification_type_id) VALUES (?, ?)",
                           project_id, mt_id)

        if norms:
            db.execute("DELETE FROM project_applicable_norms WHERE project_id = ?", project_id)
            placeholders = ','.join('?' * len(norms))
            rows = db.execute(f"SELECT id, code FROM applicable_norms WHERE code IN ({placeholders})", *norms)
            norm_code_to_id = {row['code']: row['id'] for row in rows}

            for code in norms:
                norm_id = norm_code_to_id[code]
                db.execute("INSERT INTO project_applicable_norms (project_id,applicable_norm_id) VALUES (?, ?)",
                           project_id, norm_id)
                  
        if process:
            db.execute("DELETE FROM project_legalization_process WHERE project_id = ?", project_id)
            rows = db.execute("SELECT id FROM legalization_process WHERE code = ?", process)
            process_id = rows[0]['id']

            db.execute("INSERT INTO project_legalization_process (project_id, legalization_process_id) VALUES (?, ?)",
                       project_id, process_id)

        updated_project = db.execute(
            """
            SELECT id, order_number, rae, lift_address, created_at, updated_at
            FROM projects_test WHERE id = ?
            """,
            int(project_id),
        )[0]
        return jsonify({"success": True, "project": updated_project})
    
    except Exception as e:
        return jsonify({"success": False, "message": "Ha ocurrido un error al procesar su solicitud"}), 500

@app.route("/delete-project", methods=["POST"])
@login_required
def delete_project():
    """Delete project"""
    project_id = request.form.get("id")
    if not project_id or not project_id.isdigit():
        return jsonify({"success": False, "message": "Solicitud inválida"}), 400
    # Confirmar que existe y pertenece al usuario
    rows = db.execute("SELECT 1 FROM projects_test WHERE id = ? AND user_id = ? LIMIT 1",
                      int(project_id), session["user_id"])
    if len(rows) == 0:
        return jsonify({"success": False, "message": "Proyecto no encontrado"}), 404
        
    try:
        db.execute("DELETE FROM projects_test WHERE id = ? AND user_id = ?",
                   int(project_id), session["user_id"])
        return jsonify({"success": True, "id": int(project_id)})
    except Exception:
        return jsonify({"success": False, "message": "Error interno"}), 500

@app.route("/get-project", methods=["POST"])
@login_required
def get_project():
    """Get project data"""
    data = request.get_json()
    project_id = data.get('projectId')

    text_fields = ["order_number", "rae", "client_name", "client_nif", "client_address",
                 "client_city", "client_zip", "lift_address", "lift_city", "lift_zip", 
                 "exam_type", "oca", "qms", "nominal_load", "speed", "machine_room", "passengers",
                 "control_system", "cab_dimensions", "stops", "nominal_tension", "door_type", "travel",
                 "nominal_power", "door_size", "num_cable", "nominal_intensity", "cable_diameter", "ratio",
                 "cab_mass", "cab_rails", "cw_mass", "cw_rails", "locking_device1", "locking_device2", "machine_brake",
                 "cab_parachute", "cw_parachute", "cab_speed_governor", "cw_speed_governor", "cab_buffer", "cw_buffer", 
                 "safety_circuit", "ucm_detect", "ucm_act", "ucm_stop"]
    
    if not project_id or not project_id.isdigit():
        return jsonify({"success": False, "message": "Solicitud inválida"}), 400
    # Confirmar que existe y pertenece al usuario
    rows = db.execute("SELECT 1 FROM projects_test WHERE id = ? AND user_id = ? LIMIT 1",
                      int(project_id), session["user_id"])
    if len(rows) == 0:
        return jsonify({"success": False, "message": "Proyecto no encontrado"}), 404
    try:
        project_data = db.execute(
            """SELECT id, order_number, rae, client_name,
            client_nif, client_address, client_city, client_zip,
            lift_address, lift_city, lift_zip, exam_type, oca, qms,
            nominal_load, speed, machine_room, passengers, control_system,
            cab_dimensions, stops, nominal_tension, door_type, travel,
            nominal_power, door_size, num_cable, nominal_intensity,
            cable_diameter, ratio, cab_mass, cab_rails, cw_mass, cw_rails, locking_device1, locking_device2, machine_brake,
            cab_parachute, cw_parachute, cab_speed_governor, cw_speed_governor, cab_buffer, cw_buffer, safety_circuit,
            ucm_detect, ucm_act, ucm_stop FROM projects_test 
            WHERE id = ? AND user_id = ?""",
            project_id, session["user_id"]
        )[0]

        modification_types = db.execute(
            """SELECT code 
            FROM modification_types
            JOIN project_modification_types ON modification_types.id = project_modification_types.modification_type_id
            WHERE project_modification_types.project_id = ?""", project_id
        )

        applicable_norms = db.execute(
            """SELECT code 
            FROM applicable_norms
            JOIN project_applicable_norms ON applicable_norms.id = project_applicable_norms.applicable_norm_id
            WHERE project_applicable_norms.project_id = ?""", project_id
        )

        legalization_process = db.execute(
            """SELECT code 
            FROM legalization_process
            JOIN project_legalization_process ON legalization_process.id = project_legalization_process.legalization_process_id
            WHERE project_legalization_process.project_id = ?""", project_id
        )
        
        # Sanitizar campos de texto de forma segura
        for field in text_fields:
            if field in project_data and project_data[field] is not None:
                project_data[field] = html.escape(str(project_data[field]))

        project_data["modification_types"] = modification_types
        project_data["applicable_norms"] = applicable_norms
        project_data["legalization_process"] = legalization_process
        
        return jsonify({"success": True, "data": project_data})

    except Exception as e:
        return jsonify({"success": False, "message": "Ha ocurrido un error al procesar su solicitud"}), 500

@app.route("/generate-pdf/<int:project_id>")
@login_required
def generate_pdf(project_id):
    """Generate PDF"""
    text_fields = ["order_number", "rae", "client_name", "client_nif", "client_address",
                 "client_city", "client_zip", "lift_address", "lift_city", "lift_zip", 
                 "exam_type", "oca", "qms", "nominal_load", "speed", "machine_room", "passengers",
                 "control_system", "cab_dimensions", "stops", "nominal_tension", "door_type", "travel",
                 "nominal_power", "door_size", "num_cable", "nominal_intensity", "cable_diameter", "ratio",
                 "cab_mass", "cab_rails", "cw_mass", "cw_rails", "locking_device1", "locking_device2", "machine_brake",
                 "cab_parachute", "cw_parachute", "cab_speed_governor", "cw_speed_governor", "cab_buffer", "cw_buffer", 
                 "safety_circuit", "ucm_detect", "ucm_act", "ucm_stop"]
    
    # Confirmar que existe y pertenece al usuario
    rows = db.execute("SELECT 1 FROM projects_test WHERE id = ? AND user_id = ? LIMIT 1",
                      int(project_id), session["user_id"])
    if len(rows) == 0:
        return jsonify({"success": False, "message": "Proyecto no encontrado"}), 404
    try:
        project_data = db.execute(
            """SELECT id, order_number, rae, client_name,
            client_nif, client_address, client_city, client_zip,
            lift_address, lift_city, lift_zip, exam_type, oca, qms,
            nominal_load, speed, machine_room, passengers, control_system,
            cab_dimensions, stops, nominal_tension, door_type, travel,
            nominal_power, door_size, num_cable, nominal_intensity,
            cable_diameter, ratio, cab_mass, cab_rails, cw_mass, cw_rails, locking_device1, locking_device2, machine_brake,
            cab_parachute, cw_parachute, cab_speed_governor, cw_speed_governor, cab_buffer, cw_buffer, safety_circuit,
            ucm_detect, ucm_act, ucm_stop, created_at, updated_at FROM projects_test 
            WHERE id = ? AND user_id = ?""",
            project_id, session["user_id"]
        )[0]
        if project_data.get('created_at'):
            try:
                project_data['created_at'] = datetime.fromisoformat(project_data['created_at'].replace('Z', '+00:00'))
            except:
                project_data['created_at'] = datetime.now()

        if project_data.get('updated_at'):
            try:
                project_data['updated_at'] = datetime.fromisoformat(project_data['updated_at'].replace('Z', '+00:00'))
            except:
                project_data['updated_at'] = project_data['created_at']

        modification_types = db.execute(
            """SELECT code, label
            FROM modification_types
            JOIN project_modification_types ON modification_types.id = project_modification_types.modification_type_id
            WHERE project_modification_types.project_id = ?""", project_id
        )

        applicable_norms = db.execute(
            """SELECT code, label
            FROM applicable_norms
            JOIN project_applicable_norms ON applicable_norms.id = project_applicable_norms.applicable_norm_id
            WHERE project_applicable_norms.project_id = ?""", project_id
        )

        legalization_process = db.execute(
            """SELECT code, label
            FROM legalization_process
            JOIN project_legalization_process ON legalization_process.id = project_legalization_process.legalization_process_id
            WHERE project_legalization_process.project_id = ?""", project_id
        )
        

        # Sanitizar campos de texto de forma segura
        for field in text_fields:
            if field in project_data and project_data[field] is not None:
                project_data[field] = html.escape(str(project_data[field]))

        project_data["modification_types"] = modification_types if modification_types else []
        project_data["applicable_norms"] = applicable_norms if applicable_norms else []
        project_data["legalization_process"] = legalization_process if legalization_process else []
        project_data["mod_codes"] = [mod['code'] for mod in modification_types]
        project_data["process_codes"] = [legalization['code'] for legalization in legalization_process]

        html_content = render_template("pdf/documento.html", project_data=project_data)
        
        import os 
        css_path = os.path.join(app.static_folder, 'pdf', 'styles.css')
  
        font_config = FontConfiguration()
        pdf = HTML(string=html_content).write_pdf(
            stylesheets=[CSS(filename=css_path)],
            font_config=font_config
        )

        response = make_response(pdf)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f'inline; filename="proyecto_{project_data["order_number"]}.pdf"'

        return response

    except Exception as e:
        logger.error(f"Error generando PDF para proyecto {project_id}: {e}")
        return jsonify({"success": False, "message": "Ha ocurrido un error al procesar su solicitud"}), 500
    

@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")