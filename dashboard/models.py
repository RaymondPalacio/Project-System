from django.db import models
from flask_sqlalchemy import SQLAlchemy

# Initialize the database object
db = SQLAlchemy()

# Define the Flower model
class Flower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Flower {self.id}: {self.image_name}>'
