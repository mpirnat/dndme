import json
import logging
import os

from flask import Flask
from flask import render_template
app = Flask(__name__)

base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '../..'))

# Don't clog the dndme shell with logging
if 'FLASK_SUPPRESS_LOGGING' in os.environ:
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.logger.disabled = True


@app.route("/api/player-view")
def player_view_api():
    try:
        with open(base_dir+"/player_view.json", 'r') as f:
            return f.read()
    except IOError:
        content = json.dumps({'error': 'Unable to read player_view.json'})
        return (content, 404, {})
    except Exception as e:
        content = json.dumps({'error': str(e)})
        return (content, 500, {})


@app.route("/player-view")
def player_view():
    return render_template("player-view.html")
