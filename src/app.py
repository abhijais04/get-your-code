from DownloadService import DownloadService
import logging
from flask import Flask, jsonify, request, render_template, url_for, redirect, make_response
from constants import Websites
app = Flask(__name__)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

@app.route('/process_form_input', methods=['POST'])
def process_form_input():
    return download_solutions()


@app.route('/home', methods=['GET'])
def render_homepage():
    return render_template("index.html")


@app.route('/details/<website_name>')
def render_download_page(website_name):
    if website_name == 'codeforces':
        return render_template('codeforces_render.html')
    elif website_name == 'spoj':
        return render_template('spoj_render.html')
    return redirect(url_for('render_homepage'))


def download_solutions():
    username = request.form.get('username')
    password = request.form.get('password')
    headers = {"Content-Type": "application/json"}
    logging.info(request.form)
    
    website_name = request.form.get('website')
    website_id = get_website_id(website_name)
    params = {
        "username": username,
        "password": password
        }
        
    try:
        DownloadService.downloadSolutions(website_id, params)
        return render_template('success.html')
    except Exception as e:
        print("Error here !!!")
        return render_template('error.html')

def get_website_id(website_name):
    logging.info("Website name: " + website_name)
    logging.info(website_name=="codeforces")
    website_id = None
    if website_name == "codeforces":
        website_id = Websites.CODEFORCES
    elif website_name == "spoj":
        website_id = Websites.SPOJ

    return website_id

if __name__ == "__main__":
    app.run(debug=True)
