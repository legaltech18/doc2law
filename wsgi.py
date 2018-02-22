from flask import Flask, render_template, request
from search import search

    
application = Flask(__name__)

@application.route("/")
@application.route("/search")
def index():
    return render_template("index.html")

@application.route("/query", methods=['POST'])
def query():
    query = request.form['query']
    langauge = 'en'
    response = search(query)
    #return results
    return render_template("search.html", response = response, query=query)
    
if __name__ == '__main__':
    application.run()   
