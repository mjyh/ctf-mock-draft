from flask import Flask

# app = Flask(__name__)
# @app.route('/')
# def home():
#     return "Hello, this is my CTF Mock Draft site!"
#
# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")  # this looks in the 'templates/' folder

if __name__ == "__main__":
    app.run(debug=True)