from flask import Flask, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Reasons(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    hidden = db.Column(db.Boolean, nullable=False, default=False)

@app.route('/')
def index():
    reasons = Reasons.query.filter_by(hidden=False).all()
    if not reasons:
        return redirect('/admin')

    reason = random.choice(reasons)
    return render_template('index.html', reason=reason) 

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == 'POST':
        reason_content=request.form['reason']
        new_reason = Reasons(content = reason_content)

        try:
            db.session.add(new_reason)
            db.session.commit()
            return redirect('/')
        except:
            return 'Error in adding the reason'
         
    else:
        return render_template('admin.html')

@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    reason=Reasons.query.get_or_404(id)
    reason.hidden=True
    db.session.commit()
    return redirect('/')


if __name__ == "__main__":

    with app.app_context():
        db.create_all()

app.run(debug=True)