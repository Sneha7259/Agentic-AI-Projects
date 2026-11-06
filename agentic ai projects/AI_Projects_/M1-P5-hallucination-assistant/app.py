from flask import Flask, render_template, request, jsonify
from verifier import run_agent
app=Flask(__name__)
@app.get('/')
def home(): return render_template('index.html')
@app.post('/api/ask')
def ask():
    data=request.get_json(silent=True) or {}; question=(data.get('question') or '').strip()
    if not question: return jsonify({'error':'Please enter a question.'}),400
    if len(question)>1200: return jsonify({'error':'Question is too long (maximum 1,200 characters).'}),400
    return jsonify(run_agent(question))
if __name__=='__main__': app.run(debug=False,port=5001)
