from FlaskApp import app

if __name__ == '__main__':
    app.run(host=app.config.get("FLASK_HOST"),
            port=app.config.get("FLASK_PORT"),
            debug=app.config.get("FLASK_DEBUG"))
