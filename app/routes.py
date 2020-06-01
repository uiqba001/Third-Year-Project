import re

from flask import render_template, flash, redirect, url_for, session
from flask import request
from flask_login import current_user, login_user, login_required
from flask_login import logout_user

import app.database as db_helper
from app import app
from app import db
from app.action_types import BudgetActions, SavingsActions
from app.models import User
from app.validation import validate_create_or_edit_pot, validate_number, \
    validate_amount_to_remove_is_less_than_pot_total


# returning jinja template of index page through flask route
@app.route('/')
@app.route('/index')
@login_required
def index():
    budgets = db_helper.get_budgets(current_user)

    budget_allocation_and_spent = [
        PotTargetAndTotalAmount(budget.name, budget.allocation, db_helper.get_total_amount_spent_for_budget(budget.id),
                                budget.id)
        for budget in budgets]

    savings_pots = db_helper.get_savings_pots(current_user)

    savings_pot_goal_and_saved = [
        PotTargetAndTotalAmount(saving_pot.name, saving_pot.savings_goal,
                                db_helper.get_total_amount_saved_for_savings_pot(saving_pot.id),
                                saving_pot.id)
        for saving_pot in savings_pots]

    budget_averages = db_helper.get_average_for_every_budget(current_user)
    savings_averages = db_helper.get_average_for_every_savings_pot(current_user)
    budget_pie_chart_info = db_helper.get_budget_pie_chart_info(current_user)
    savings_pie_chart_info = db_helper.get_savings_pie_chart_info(current_user)
    total_saved = db_helper.get_total_saved(current_user.id)
    total_number_of_budgets = len(db_helper.get_budgets(current_user))
    total_number_of_savings_pots = len(db_helper.get_savings_pots(current_user))
    total_budget_allocations = db_helper.get_total_budget_allocation(current_user)

    return render_template("index.html", title='Home Page', budgets=budget_allocation_and_spent,
                           pots=savings_pot_goal_and_saved, budget_averages=budget_averages,
                           savings_averages=savings_averages, budget_pie_chart_info=budget_pie_chart_info,
                           savings_pie_chart_info=savings_pie_chart_info, total_saved=total_saved,
                           total_number_of_budgets=total_number_of_budgets,
                           total_number_of_savings_pots=total_number_of_savings_pots,
                           total_budget_allocations=total_budget_allocations)


# logic to validate and log users in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form["emailAddress"]
        password = request.form["password"]
        user = db_helper.get_user(email)
        if user is None or not user.check_password(password=password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))

    return render_template('login.html', title='Sign In')


# logic to log a user out of current session
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# logic to register and validate a user on the register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    session.pop("_flashes", None)

    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]

        validation_failed = False
        if not is_valid_email(email):
            flash("Invalid email")
            validation_failed = True
        if len(password) < 6:
            flash("Password must be at least 6 characters in length")
            validation_failed = True
        if db_helper.get_user(email) is not None:
            flash("This email already exists, please choose another email")
            validation_failed = True

        if validation_failed:
            return redirect(url_for('register'))

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))

    return render_template('register.html', title='Register')


# function employing regex to examine whether a correct email format has been used
def is_valid_email(email):
    return re.search("^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+.[a-zA-Z]+", email)


# logic for creating budgets using the database helper
@app.route('/budgets/create', methods=['GET', 'POST'])
@login_required
def create_budget():
    if request.method == 'POST':
        name = request.form["budgetName"]
        allocation = request.form["budgetAllocation"]

        validation_passed = validate_create_or_edit_pot(name, allocation)
        if not validation_passed:
            return redirect(url_for('create_budget'))
        db_helper.create_budget(name, allocation, current_user.id)
        return redirect(url_for('display_budgets'))

    return render_template('create_budget.html', title='Create A Budget')


# logic to display a budget using the database helper
@app.route('/budgets', methods=['GET', 'POST'])
@login_required
def display_budgets():
    if request.method == 'POST':
        budget_id = int(request.form["pot_id"])
        if request.form["submit_type"] == "edit":

            name = request.form["pot_name"]
            allocation = request.form["pot_amount"]
            if validate_create_or_edit_pot(name, allocation):
                db_helper.edit_budget(budget_id, name, int(allocation), current_user.id)

        elif request.form["submit_type"] == "delete":
            db_helper.delete_budget(budget_id, current_user.id)

        elif request.form["submit_type"] == "add_money":

            amount_spent = request.form["amount_increased"]
            if validate_number(amount_spent, "amount spent"):
                db_helper.spend_money(int(amount_spent), budget_id, current_user.id)

        elif request.form["submit_type"] == "remove_money":

            remove_spent = request.form["amount_decreased"]
            if validate_number(remove_spent, "removed amount"):
                spent_so_far = db_helper.get_total_amount_spent_for_budget(budget_id)
                if validate_amount_to_remove_is_less_than_pot_total(int(remove_spent), spent_so_far):
                    db_helper.spend_money(-int(remove_spent), budget_id, current_user.id)
        return redirect(url_for('display_budgets'))

    budgets = db_helper.get_budgets(current_user)

    budget_allocation_and_spent = [
        PotTargetAndTotalAmount(budget.name, budget.allocation, db_helper.get_total_amount_spent_for_budget(budget.id),
                                budget.id)
        for budget in budgets]

    recent_budget_actions = db_helper.get_recent_actions(current_user.id, [action.value for action in BudgetActions])

    return render_template('base_pots.html', title='Budgets', is_budget=True,
                           pots=budget_allocation_and_spent,
                           recent_pot_actions=recent_budget_actions)


# logic to display savings pots, using the database helper
# NEED TO GET VALIDATION WORKING FOR REMOVING SAVED MONEY
@app.route('/savings-pots', methods=['GET', 'POST'])
@login_required
def display_savings_pots():
    if request.method == 'POST':
        pot_id = int(request.form["pot_id"])
        if request.form["submit_type"] == "edit":

            name = request.form["pot_name"]
            savings_goal = request.form["pot_amount"]
            if validate_create_or_edit_pot(name, savings_goal):
                db_helper.edit_savings_pot(pot_id, name, int(savings_goal), current_user.id)

        elif request.form["submit_type"] == "delete":

            db_helper.delete_savings_pot(pot_id, current_user.id)

        elif request.form["submit_type"] == "add_money":
            amount_saved = request.form["amount_increased"]

            if validate_number(amount_saved, "amount saved"):
                db_helper.save_money(int(amount_saved), pot_id, current_user.id)

        elif request.form["submit_type"] == "remove_money":

            remove_saved = request.form["amount_decreased"]

            if validate_number(remove_saved, "removed amount"):
                spent_so_far = db_helper.get_total_amount_saved_for_savings_pot(pot_id)
                if validate_amount_to_remove_is_less_than_pot_total(int(remove_saved), spent_so_far):
                    db_helper.save_money(-int(remove_saved), pot_id, current_user.id)

        return redirect(url_for('display_savings_pots'))

    savings_pots = db_helper.get_savings_pots(current_user)

    savings_pot_goal_and_saved = [
        PotTargetAndTotalAmount(saving_pot.name, saving_pot.savings_goal,
                                db_helper.get_total_amount_saved_for_savings_pot(saving_pot.id),
                                saving_pot.id)
        for saving_pot in savings_pots]

    recent_savings_actions = db_helper.get_recent_actions(current_user.id, [action.value for action in SavingsActions])

    return render_template('base_pots.html', title='Savings Pots', is_budget=False,
                           pots=savings_pot_goal_and_saved,
                           recent_pot_actions=recent_savings_actions)


# logic to create a savings pot, using the database helper
@app.route('/savings-pots/create', methods=['GET', 'POST'])
@login_required
def create_savings_pot():
    if request.method == 'POST':
        name = request.form["savingsPotName"]
        goal = request.form["savingsPotGoal"]

        validation_passed = validate_create_or_edit_pot(name, goal)
        if not validation_passed:
            return redirect(url_for('create_savings_pot'))
        db_helper.create_savings_pot(name, goal, current_user.id)
        return redirect(url_for('display_savings_pots'))

    return render_template('create_savings_pot.html', title='Create Savings Pot')


class PotTargetAndTotalAmount:
    def __init__(self, name, target, total_amount, pot_id):
        self.name = name
        self.target = target
        self.total_amount = total_amount
        self.pot_id = pot_id
