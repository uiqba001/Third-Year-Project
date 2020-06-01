$(document).ready(function() {
    $(".form-button").click(function(e) {
        var form = $(this).closest(".validation-form");
        if (form) {
            form.validate({
                rules: {
                    password: {
                        minlength: 6,
                    },
                     pot_amount: {
                        number: true,
                        min: 1
                    },
                    amount_decreased: {
                        number: true,
                        min: 1
                    },
                    amount_increased: {
                        number: true,
                        min: 1
                    },
                    budgetAllocation: {
                        number: true,
                        min: 1
                    },
                    savingsPotGoal: {
                        number: true,
                        min: 1
                    }
                }
            });
        }
    });
});
