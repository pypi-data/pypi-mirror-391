from splent_framework.blueprints.base_blueprint import BaseBlueprint
from flask_login import LoginManager

auth_bp = BaseBlueprint("auth", __name__, template_folder="templates")


def init_feature(app):
    from .models import User
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    app.login_manager = login_manager
    
def inject_context_vars(app):
    return {}