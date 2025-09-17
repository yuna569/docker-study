from flask import Flask
import os

host = os.getenv('FLASK_HOST', '0.0.0.0')
port = int(os.getenv('FLASK_PORT', 5000))

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host=host, port=port)