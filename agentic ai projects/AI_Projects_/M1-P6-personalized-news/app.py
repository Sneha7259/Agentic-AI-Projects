from flask import Flask,render_template,request,jsonify
from news import build_digest,CATEGORIES
app=Flask(__name__)
@app.get('/')
def home():return render_template('index.html')
@app.post('/api/digest')
def digest():
    data=request.get_json(silent=True) or {}; interests=data.get('interests') or []
    if not isinstance(interests,list) or not interests:return jsonify({'error':'Select at least one interest.'}),400
    if len(interests)>len(CATEGORIES):return jsonify({'error':'Too many categories.'}),400
    return jsonify(build_digest(interests))
if __name__=='__main__':app.run(debug=False,port=5002)
