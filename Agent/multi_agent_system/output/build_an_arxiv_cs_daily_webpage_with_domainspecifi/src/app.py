import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
import fetch_data

app = Flask(__name__, template_folder='../templates', static_folder='../static')

CATEGORIES = {
    'cs.AI': 'Artificial Intelligence',
    'cs.CV': 'Computer Vision',
    'cs.CL': 'Computation and Language',
    'cs.LG': 'Machine Learning'
}

@app.route('/')
def index():
    category = request.args.get('category', 'cs.AI')
    papers = fetch_data.fetch_papers(category)
    return render_template('index.html', papers=papers, categories=CATEGORIES, current_category=category)

@app.route('/paper/<paper_id>')
def paper_detail(paper_id):
    paper = fetch_data.get_paper_details(paper_id)
    return render_template('paper.html', paper=paper)

if __name__ == '__main__':
    app.run(debug=True)
