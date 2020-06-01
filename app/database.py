# BUDGETS
from datetime import datetime
from random import randrange

from sqlalchemy import desc, func

from app import db
from app.action_types import BudgetActions, SavingsActions
from app.models import Budget, MoneySpent, SavingsPot, MoneySaved, Actions, User


# retrieving user
def get_user(email):
    user = User.query.filter_by(email=email).first()
    return user


# retrieving user's budgets
def get_budgets(user):
    return user.budgets


# colours to use in pie charts
colours = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
           "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
           "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]


# getting information required for pie chart
def get_budget_pie_chart_info(user):
    all_pie_chart_info = []

    for index, budget_row in enumerate(get_budgets(user)):
        label = budget_row.name
        value = get_total_amount_spent_for_budget(budget_row.id)
        colour = colours[index % len(colours)]
        percentage = (value / budget_row.allocation) * 100 if value > 0 else 0
        pie_chart_info = PieChartInfo(label, value, colour, round(percentage))
        all_pie_chart_info.append(pie_chart_info)

    return all_pie_chart_info


# getting average value of budgets against whole budget value
def get_average_for_every_budget(user):
    budget_average_list = []
    for budget in get_budgets(user):
        # Get the average of the amount spent column in the MoneySpent table where the budget_id is equal to budget.id
        # Store the average as a column called average in the result row
        result_row = db.session \
            .query(func.avg(MoneySpent.amount_spent).label("average")) \
            .filter_by(budget_id=budget.id) \
            .first()

        average = result_row.average
        if average is None:
            average = 0

        budget_average = PotAverage(budget.name, average)
        budget_average_list.append(budget_average)
    return budget_average_list


# auxiliary class for finding average of budgets
class PotAverage:
    def __init__(self, name, average):
        self.name = name
        self.average = average


# auxiliary class for constructing pie charts
class PieChartInfo:
    def __init__(self, label, value, colour, percentage):
        self.label = label
        self.value = value
        self.colour = colour
        self.percentage = percentage


# function to create budget
def create_budget(name, allocation, user_id):
    budget = Budget(id=randrange(9999999), name=name, allocation=allocation, user_id=user_id)
    db.session.add(budget)
    db.session.commit()
    add_action(BudgetActions.CREATED_BUDGET.value, name, user_id)


# function to spend money in a budget
def spend_money(amount_spent, budget_id, user_id):
    if amount_spent < 0:
        add_action(BudgetActions.REMOVE_MONEY.value, str(amount_spent), user_id)
    else:
        add_action(BudgetActions.SPENT_MONEY.value, str(amount_spent), user_id)

    money_spent = MoneySpent(amount_spent=amount_spent, budget_id=budget_id, user_id=user_id)
    db.session.add(money_spent)
    db.session.commit()


# function to edit a budget
def edit_budget(budget_id, name, allocation, user_id):
    budget = Budget.query.filter_by(id=budget_id).first()
    budget.name = name
    budget.allocation = allocation
    add_action(BudgetActions.EDITED_BUDGET.value, name, user_id)
    db.session.commit()


# function to delete a budget
def delete_budget(budget_id, user_id):
    budget = Budget.query.filter_by(id=budget_id).first()
    name = budget.name
    add_action(BudgetActions.DELETE_BUDGET.value, name, user_id)
    Budget.query.filter_by(id=budget_id).delete()
    db.session.commit()


# function to remove money spent within a budget
def delete_spent_money(money_spent_id):
    MoneySpent.query.filter_by(id=money_spent_id).delete()
    db.session.commit()


# function to retrieve a budget's allocation
def get_budget_allocation(budget_id):
    return Budget.query.filter_by(id=budget_id).first().allocation


# function to get total amount of money spent within budgets USED
def get_total_amount_spent_for_budget(budget_id):
    all_money_spent_rows = MoneySpent.query.filter_by(budget_id=budget_id)
    return sum([money_spent_row.amount_spent for money_spent_row in all_money_spent_rows])


# function to return total budget allocations
def get_total_budget_allocation(user):
    budgets = user.budgets
    return sum([budget.allocation for budget in budgets])


# function to return sum of spent money across budgets
def get_total_spent(user_id):
    all_money_spent_rows = MoneySpent.query.filter_by(user_id=user_id)
    return sum([money_spent_row.amount_spent for money_spent_row in all_money_spent_rows])


# SAVINGS POTS

# returning savings pots of user
def get_savings_pots(user):
    return user.savings_pots


# returning information for constructing pie chart of savings pot pie chart
def get_savings_pie_chart_info(user):
    all_pie_chart_info = []

    for index, savings_row in enumerate(get_savings_pots(user)):
        label = savings_row.name
        value = get_total_amount_saved_for_savings_pot(savings_row.id)
        colour = colours[(index + 5) % len(colours)]
        percentage = (value / savings_row.savings_goal) * 100 if value > 0 else 0

        pie_chart_info = PieChartInfo(label, value, colour, round(percentage))
        all_pie_chart_info.append(pie_chart_info)

    return all_pie_chart_info


# returning average of all savings pots
def get_average_for_every_savings_pot(user):
    savings_average_list = []
    for saving in get_savings_pots(user):
        # Get the average of the amount spent column in the MoneySaved table
        # where the saving_pot_id is equal to saving.id
        # Store the average as a column called average in the result row
        result_row = db.session \
            .query(func.avg(MoneySaved.amount_saved).label("average")) \
            .filter_by(savings_pot_id=saving.id) \
            .first()

        average = result_row.average
        if average is None:
            average = 0

        savings_average = PotAverage(saving.name, average)
        savings_average_list.append(savings_average)
    return savings_average_list


# function to create a savings pot
def create_savings_pot(savings_pot_name, savings_goal, user_id):
    savings_pot = SavingsPot(id=randrange(9999999), name=savings_pot_name, savings_goal=savings_goal, user_id=user_id)
    add_action(SavingsActions.CREATED_SAVINGS_POT.value, savings_pot_name, user_id)
    db.session.add(savings_pot)
    db.session.commit()


# function to edit a savings pot
def edit_savings_pot(pot_id, name, savings_goal, user_id):
    savings_pot = SavingsPot.query.filter_by(id=pot_id).first()
    savings_pot.name = name
    savings_pot.savings_goal = savings_goal
    add_action(SavingsActions.EDITED_SAVINGS_POT.value, name, user_id)
    db.session.commit()


# function to add saved money to a savings pot
def save_money(amount_saved, savings_pot_id, user_id):
    if amount_saved < 0:
        add_action(SavingsActions.REMOVE_SAVED_MONEY.value, str(amount_saved), user_id)
    else:
        add_action(SavingsActions.SAVED_MONEY.value, str(amount_saved), user_id)

    money_saved = MoneySaved(amount_saved=amount_saved, savings_pot_id=savings_pot_id, user_id=user_id)
    db.session.add(money_saved)
    db.session.commit()


# function to delete a savings pot
def delete_savings_pot(savings_pot_id, user_id):
    savings_pot = SavingsPot.query.filter_by(id=savings_pot_id).first()
    name = savings_pot.name
    add_action(SavingsActions.DELETED_SAVINGS_POT.value, name, user_id)

    SavingsPot.query.filter_by(id=savings_pot_id).delete()
    db.session.commit()


# function to return a savings pot goal
def get_savings_pot_goal(savings_pot_id):
    return SavingsPot.query.filter_by(id=savings_pot_id).first().savings_goal


# function to get total amount saved for savings pot
def get_total_amount_saved_for_savings_pot(savings_pot_id):
    all_money_saved_rows = MoneySaved.query.filter_by(savings_pot_id=savings_pot_id)
    return sum([money_saved_row.amount_saved for money_saved_row in all_money_saved_rows])


# function to return total amount saved for savings pots
def get_total_saved(user_id):
    all_money_saved_rows = MoneySaved.query.filter_by(user_id=user_id)
    return sum([money_saved_row.amount_saved for money_saved_row in all_money_saved_rows])


# ACTIONS

# function to add action
def add_action(action_type, action_value, user_id):
    action = Actions(action_type=action_type, action_value=action_value, user_id=user_id, time=datetime.now())
    db.session.add(action)
    db.session.commit()


# function to only return most recent 3 actions
def get_recent_actions(user_id, action_types, number_of_actions=3):
    recent_action_rows = Actions.query \
        .filter_by(user_id=user_id) \
        .filter(Actions.action_type.in_(action_types)) \
        .order_by(desc(Actions.time)) \
        .limit(number_of_actions) \
        .all()

    return recent_action_rows
