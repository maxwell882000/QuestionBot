from . import bp
from flask import render_template
from flask_login import login_required


@bp.route('/')
@login_required
def index():
    return render_template('admin/index.html')
