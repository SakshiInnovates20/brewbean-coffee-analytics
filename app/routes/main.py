from flask import Blueprint, render_template, jsonify
from app.db import check_db_connection

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """
    Renders the BrewBean Coffee Welcome Page.
    """
    return render_template('index.html')

@main_bp.route('/health')
def health_check():
    """
    Health check endpoint.
    Verifies that Flask is running and reports the connection status to MySQL.
    """
    db_status = check_db_connection()
    
    response = {
        "status": "ok",
        "service": "BrewBean Analytics System",
        "version": "1.0.0",
        "database": db_status
    }
    
    # Return HTTP 200 OK regardless of DB state so health monitoring tool knows Flask is up,
    # but db_status clearly indicates database connectivity status.
    return jsonify(response), 200
