colors = ["color1" , "color2", "color3"]

budgets = ["a", "b", "c", "d", "e"]


for index, budget in enumerate(budgets):
    color = colors[index % len(colors)]
    print(color)
