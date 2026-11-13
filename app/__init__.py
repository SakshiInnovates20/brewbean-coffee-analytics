from flask import Flask
from app.config import Config

def create_app(config_class=Config):
    """
    Application Factory pattern to construct and configure the Flask app instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register routes/blueprints
    from app.routes.main import main_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.shops import shops_bp
    from app.routes.products import products_bp
    from app.routes.customers import customers_bp
    from app.routes.sales import sales_bp
    from app.routes.marketing import marketing_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(shops_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(marketing_bp)

    return app
