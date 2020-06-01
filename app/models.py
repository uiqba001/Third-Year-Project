from flask_login import UserMixin
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


# budget table
class Budget(db.Model):
    __tablename__ = "budget"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    allocation = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# money spend table for budgets
class MoneySpent(db.Model):
    __tablename__ = "money_spent"
    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    amount_spent = db.Column(db.Integer)


# savings pot table
class SavingsPot(db.Model):
    __tablename__ = "savings_pot"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    savings_goal = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# saved money table for savings pots
class MoneySaved(db.Model):
    __tablename__ = "money_saved"
    id = db.Column(db.Integer, primary_key=True)
    savings_pot_id = db.Column(db.Integer, db.ForeignKey('savings_pot.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount_saved = db.Column(db.Integer)


# actions table for recent actions
class Actions(db.Model):
    __tablename__ = "actions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action_type = db.Column(db.String(100))  # (e.g. CREATED_BUDGET, SPENT_MONEY, SAVED_MONEY etc.)
    action_value = db.Column(db.String(100))  # (e.g. 100 if they SPENT_MONEY, or "Groceries"" if they CREATED_BUDGET)
    time = db.Column(db.DateTime)


# user table
class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    budgets = db.relationship("Budget", backref=backref("budgets"))
    savings_pots = db.relationship("SavingsPot", backref = backref("savings_pots"))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
