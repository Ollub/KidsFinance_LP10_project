from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    with open('index.html', 'r') as file:
        first_page = file.read()
    return first_page


if __name__ == '__main__':
    app.run() 