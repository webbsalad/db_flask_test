from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path='/static', static_folder='static')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    mail = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Float, default=0)

    def __repr__(self):
        return f"{self.id, self.name, self.mail, self.rating}"

def create_tables():
    with app.app_context():
        db.create_all()

#############################################################################

@app.route('/')
def index():
    items = Item.query.order_by(Item.id).all()
    return render_template("index.html", data=items)


@app.route('/update', methods=['POST'])
def update():
    data = request.json
    for row in data:
        item = Item.query.get(row['id'])
        if item:
            item.name = row['name']
            item.mail = row['mail']
            item.rating = row['rating']
            db.session.commit()
        else:
            new_item = Item(
                id=row['id'],
                name=row['name'],
                mail=row['mail'],
                rating=row['rating']
            )
            db.session.add(new_item)
            db.session.commit()
    return 'Success'


@app.route('/delete/<int:item_id>', methods=['DELETE'])
def delete(item_id):
    item = Item.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return 'Success', 200
    else:
        return 'Not Found', 404


if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
