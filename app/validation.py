from flask import flash


def validate_create_or_edit_pot(name, target):
    validation_passed = True

    if len(name) < 1:
        flash("The name must be at least 1 character in length")
        validation_passed = False

    validate_target_passed = validate_number(target, "Target")
    if not validate_target_passed:
        validation_passed = False

    return validation_passed


def validate_number(number, number_name):
    validation_passed = True
    try:
        number = int(number)
        if number <= 0:
            flash(f"You cannot have a {number_name} of 0 or less")
            validation_passed = False
    except ValueError:
        flash(f"{number_name} is not a number")
        validation_passed = False

    return validation_passed


def validate_amount_to_remove_is_less_than_pot_total(amount_to_remove, spent_so_far):
    # if the amount_to_remove is > spent so far then validation has failed
    validation_passed = True
    if amount_to_remove > spent_so_far:
        flash("Amount to remove must be less than current amount")
        validation_passed = False

    return validation_passed
