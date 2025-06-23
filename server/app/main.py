from flask import Flask
from routes import app as routes_blueprint

app = Flask(__name__)
app.register_blueprint(routes_blueprint)

if __name__ == "__main__":
    app.run(port=5001, debug=True)
