from splent_framework.hooks.template_hooks import register_template_hook
from flask import render_template


def login_signup_items():
    return render_template("hooks/anonymous_sidebar_items.html")

def logout_item():
    return render_template("hooks/authenticated_sidebar_items.html")

register_template_hook("layout.anonymous_sidebar", login_signup_items)
register_template_hook("layout.authenticated_sidebar", logout_item)