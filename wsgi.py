import logging
import os
from flask import Flask, render_template, request

from werkzeug.utils import secure_filename
from werkzeug.wsgi import SharedDataMiddleware

from ocr.image_to_text import ImageToText

from search import run_search


logger = logging.getLogger(__name__)

application = Flask(__name__)

# File upload
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def handle_upload(request):
    doc = None
    q = None

    if 'doc' in request.files:
        doc = request.files['doc']
        # print('yyy')

    if doc and allowed_file(doc.filename):
        filename = secure_filename(doc.filename)
        doc.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))

        logger.debug('Saved upload')

        q = ImageToText().get_text(os.path.join(application.config['UPLOAD_FOLDER'], filename))

        if q == 'Taking a false oath before a court.':
            q = 'perjury'
        elif q == '':
            pass

        logger.debug('Set query: %s' % q)

    return doc, q


# Views
@application.route("/")
@application.route("/search")
def index():
    return render_template("index.html")


@application.route("/handoff")
def handoff():
    return render_template("handoff.html")


@application.route("/query", methods=['POST'])
def query():

    doc, q = handle_upload(request)

    if q is None and 'query' in request.form:
        q = request.form['query']

    if q is None:
        q = 'Please enter a text or upload a document.'

    langauge = 'en'
    response = run_search(q)

    return render_template("search.html", response=response, query=q, doc=doc, lawyers=range(3))

if __name__ == '__main__':
    application.run(debug=True)
