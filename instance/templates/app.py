from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import qrcode
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class Violation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(20))
    violation_type = db.Column(db.String(100))
    location = db.Column(db.String(100))
    date = db.Column(db.String(20))
    fine = db.Column(db.Integer)
    status = db.Column(db.String(20), default="Unpaid")


@app.route("/")
def index():
    records = Violation.query.all()
    return render_template("index.html", records=records)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        vehicle = request.form["vehicle"]
        violation = request.form["violation"]
        location = request.form["location"]
        date = request.form["date"]
        fine = request.form["fine"]

        new_record = Violation(
            vehicle_number=vehicle,
            violation_type=violation,
            location=location,
            date=date,
            fine=fine
        )

        db.session.add(new_record)
        db.session.commit()

        # QR Code generation
        url = f"http://127.0.0.1:5000/status/{new_record.id}"
        img = qrcode.make(url)
        img.save(f"static/qr_{new_record.id}.png")

        return redirect("/")

    return render_template("add.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        vehicle = request.form["vehicle"]
        records = Violation.query.filter_by(vehicle_number=vehicle).all()
        return render_template("search.html", records=records)

    return render_template("search.html", records=None)


@app.route("/status/<int:id>")
def status(id):
    record = Violation.query.get_or_404(id)
    return render_template("status.html", record=record)


@app.route("/pay/<int:id>")
def pay(id):
    record = Violation.query.get_or_404(id)
    record.status = "Paid"
    db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    if not os.path.exists("database.db"):
        with app.app_context():
            db.create_all()

    app.run(debug=True)
