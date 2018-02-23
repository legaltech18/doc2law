from flask import Flask, render_template, request
from search import run_search


application = Flask(__name__)

@application.route("/")
@application.route("/search")
def index():
    return render_template("index.html")

@application.route("/handoff")
def handoff():
    return render_template("handoff.html")

@application.route("/query", methods=['POST'])
def query():
    query = request.form['query']
    response = run_search(query)
    print(response[0][0])
    return render_template("search.html", response=response, query=query)

if __name__ == '__main__':
    application.run(debug=True)
