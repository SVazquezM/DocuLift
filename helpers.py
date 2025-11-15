import requests

from flask import redirect, render_template, session
from functools import wraps

TECHNICAL_SPECS = {
    'machineRoom': [
        'Arriba',
        'Abajo',
        'Lateral',
        'Sin cuarto'
    ],

    'controlSystem': [
        '1 velocidad',
        '2 velocidades',
        'Variador Frec.'
    ],

    'nominalTension': [
        '400',
        '380',
        '230'
    ],

    'doorType': [
        'LA2',
        'LA3',
        'CA2',
        'CA3'
    ],

    'cableDiameter': [
        '6,0',
        '6,5',
        '8',
        '10',
        '12',
        '14'
    ],

    'ratio': [
        '1:1',
        '2:1',
        '4:1',
        '1:2'
    ],

    'cabRails': [
        'R-3',
        'R-5',
        'R-7',
        'R-12'
    ],

    'cwRails': [
        'R-3',
        'R-5',
        'R-7',
        'R-12'
    ],
}

CERTIFICATES = {
    'lockingDevice': [
        'TIPO 11/R-L',
        'TIPO 01/C',
        'TIPO 41/C',
        'TIPO 43/R'
    ],

    'machineBrake': [
        'FZD10A',
        'FZD12A',
        'FZD12C',
        'FZD14A'
    ],

    'parachute': [
        'ASG-65',
        'ASG-100',
        'ASG-120'
    ],

    'speedGovernor': [
        'SGN-200',
        'SGN-300',
        'VEGA',
        'VEGA 300'
    ],

    'buffer': [
        '300400',
        '300401',
        '300402',
        '300403'
    ],

    'safetyCircuit': [
        'LXM-02',
        'RS-200',
        'KXL-400'
    ],

    'ucmDETECT': [
        'MIC-20.50-DETECT.'
    ],

    'ucmACT': [
        'MIC-20.50-ACT.'
    ],  
    
}

def login_required(f):
    """Decorate routes to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return render_template("login2.html")
        return f(*args, **kwargs)

    return decorated_function    

def get_technical_specs():
    """Return the technical specs"""
    return TECHNICAL_SPECS

def get_certificates():
    """Return the certificates"""
    return CERTIFICATES