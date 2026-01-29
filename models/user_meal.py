from database import db
from flask_login import UserMixin

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="meals")

    description = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    indicator = db.Column(db.Boolean, default=True)
