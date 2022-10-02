import sqlite3
import sys


def main():
    global stuff
    meals_id_list = []
    args = sys.argv
    # print(args)
    db_name = args[1]
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    # ================================ #

    if len(args) > 2:

        # FOR FINDING ingridients_id # OK
        args_ing = args[2].replace("--ingredients=", "")
        args_ing = args_ing.split(',')
        # print(args_ing)
        args_ing_id = []

        y = cur.execute(f"SELECT ingredient_name FROM ingredients")
        y = y.fetchall()
        all_ingredients = []
        for i in y:
            all_ingredients.append(i[0])

        for i in args_ing:
            if i not in all_ingredients:
                print("There are no such recipes in the database.")
                exit()
            x = cur.execute(f"SELECT ingredient_id FROM ingredients WHERE ingredient_name = '{i}';")
            x = x.fetchall()[0]
            args_ing_id.append(x[0])

        '''if len(args_ing_id) == 0:
            print('There are no such recipes in the database.')
        else:
            print(f'ingridients_id = {args_ing_id}')'''

        # FOR FINDING recipes_id # OK
        args_recipe_id = []
        if len(args_ing_id) == 1:
            x = cur.execute(f"SELECT recipe_id FROM quantity WHERE ingredient_id = '{args_ing_id[0]}';")
            x = x.fetchall()
            for i in x:
                args_recipe_id.append(i[0])

        elif len(args_ing_id) == 2:
            x = cur.execute(f"""SELECT recipe_id FROM quantity 
                        WHERE ingredient_id = '{args_ing_id[0]}' OR ingredient_id = '{args_ing_id[1]}';""")
            x = x.fetchall()
            for i in x:
                args_recipe_id.append(i[0])
            for i in args_recipe_id:
                counter = (args_recipe_id.count(i))
                if counter < 2:
                    args_recipe_id.remove(i)

        elif len(args_ing_id) == 3:
            x = cur.execute(f"""SELECT recipe_id FROM quantity 
                        WHERE ingredient_id = '{args_ing_id[0]}' 
                        OR ingredient_id = '{args_ing_id[1]}' 
                        OR ingredient_id = '{args_ing_id[2]}';""")

            x = x.fetchall()
            for i in x:
                args_recipe_id.append(i[0])
            for i in args_recipe_id:
                counter = (args_recipe_id.count(i))
                if counter < 3:
                    args_recipe_id.remove(i)

        args_recipe_id = set(args_recipe_id)
        # print(f'recipes_id = {args_recipe_id}')

        args_recip = []  # FOR FINDING recipes_name # OK
        for i in args_recipe_id:
            x = cur.execute(f"SELECT recipe_name FROM recipes WHERE recipe_id = '{i}';")
            x = x.fetchall()[0]
            args_recip.append(x[0])

        # print(f'posible recipes:', *set(args_recip))

        # FOR FINDING meals_id # ==========================
        args_meal = args[3].replace("--meals=", "")
        args_meal = args_meal.split(',')
        args_meal_id = []
        for i in args_meal:
            x = cur.execute(f"SELECT meal_id FROM meals WHERE meal_name = '{i}';")
            x = x.fetchall()[0]
            args_meal_id.append(x[0])

        if len(args_meal_id) == 0:
            i = 2
            # print('There are no such recipes in the database.')

        # print(f'meals_id for {args_meal}= {args_meal_id}')

        # FOR MATCHING recipes_id and meals_id into the serve table#
        # FOR FINDING recipes_name #
        coinciden_answer = []
        for i in args_meal_id:
            y = cur.execute(f"SELECT recipe_id FROM serve WHERE meal_id = '{i}';")
            y = y.fetchall()
            for i in y:
                coinciden_answer.append(i[0])

        solution_answer = args_recipe_id.intersection(coinciden_answer)
        solution = []
        for i in solution_answer:
            x = cur.execute(f"SELECT recipe_name FROM recipes WHERE recipe_id = '{i}';")
            x = x.fetchall()[0]
            solution.append(x[0])

        print(f'Recipes selected for you:', *solution)

    elif len(args) <= 2:

        #   create table "recipes"
        cur.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                recipe_id INTEGER PRIMARY KEY,
                recipe_name TEXT NOT NULL,
                recipe_description TEXT
            );''')

        #   create table "meals"
        cur.execute('''
            CREATE TABLE IF NOT EXISTS meals (
                meal_id INTEGER PRIMARY KEY,
                meal_name TEXT NOT NULL UNIQUE
            );''')

        #   create table "ingredients"
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ingredients (
                ingredient_id INTEGER PRIMARY KEY,
                ingredient_name TEXT NOT NULL UNIQUE
            );''')

        #   create table "measures"
        cur.execute('''
            CREATE TABLE IF NOT EXISTS measures (
                measure_id INTEGER PRIMARY KEY,
                measure_name TEXT UNIQUE
            );''')

        #   Initial DB.
        data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
                "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
                "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}

        #   create table "serve"
        cur.execute(f'''PRAGMA foreign_keys = ON;''')
        cur.execute('''
        CREATE TABLE IF NOT EXISTS serve ( 
        serve_id  INTEGER PRIMARY KEY, 
        meal_id INTEGER NOT NULL,
        recipe_id INTEGER NOT NULL,
        FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),
        FOREIGN KEY(meal_id) REFERENCES meals(meal_id))
        ;''')
        conn.commit()

        #   create table "quantity "
        cur.execute('''
        CREATE TABLE IF NOT EXISTS quantity ( 
        quantity_id INTEGER PRIMARY KEY, 
        
        quantity INTEGER NOT NULL,
        recipe_id INTEGER NOT NULL,
        measure_id INTEGER NOT NULL,
        ingredient_id INTEGER NOT NULL,
        
        
        FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),
        FOREIGN KEY(measure_id) REFERENCES measures(measure_id),
        FOREIGN KEY(ingredient_id) REFERENCES ingredients(ingredient_id))
        ;''')
        conn.commit()

        # ================================= #

        # ================================= #
        #   adding the elements of the variable data to all tables

        for tables in data:
            for columns in data[tables]:
                cur.execute(f"INSERT INTO {tables} ({tables[:-1]}_name) VALUES ('{columns}');")

        conn.commit()
        # ================================= #

        # ================================= #
        #   Data entry section

        print("Pass the empty recipe name to exit.")
        while True:

            recipe_name = input(f"Recipe name: ")

            if len(recipe_name) == 0:
                break

            recipe_description = input(f"Recipe recipe_description: ")

            cur.execute(
                f"INSERT OR IGNORE INTO recipes (recipe_name, recipe_description) VALUES ('{recipe_name}', '{recipe_description}');")
            conn.commit()

            print("1) breakfast  2) brunch  3) lunch  4) supper")
            meals_schedule = input("When the dish can be served:")
            meals_id_list.append(meals_schedule)

            # ================================= #

            ingredients_input = "string just for loop"
            stuff_3 = ["quantity", "measure", "ingredient"]
            stuff_2 = ["quantity", "ingredient"]

            quantity_to_append = {}  # "quantity", "measure", "ingredient" or "quantity", "ingredient"
            while ingredients_input != "":
                ingredients_input = input("Input quantity of ingredient <press enter to stop>: ")  # "1 t sugar"
                if ingredients_input == "":
                    break

                if len(ingredients_input.split()) == 3:
                    stuff = stuff_3
                elif len(ingredients_input.split()) == 2:
                    quantity_to_append["measure"] = 8
                    stuff = stuff_2

                for (i, st) in zip(ingredients_input.split(), stuff):
                    if st == "quantity":
                        quantity_to_append["quantity"] = f"{i}"

                    elif st == "measure":
                        all_recipes = cur.execute(f"SELECT {st}_id FROM {st}s WHERE {st}_name LIKE '%{i}%';").fetchall()
                        # Check if is everything okay?
                        recipes_id_list = [row[0] for row in all_recipes]
                        if len(recipes_id_list) == 1:
                            quantity_to_append["measure"] = recipes_id_list[0]
                        else:
                            print("The measure is not conclusive!")
                            break

                    elif st == "ingredient":
                        print(f"ingredient -> {i}")
                        all_recipes = cur.execute(f"SELECT {st}_id FROM {st}s WHERE {st}_name LIKE '%{i}%';").fetchall()
                        recipes_id_list = [row[0] for row in all_recipes]
                        print(recipes_id_list, "result for ingredient")
                        if len(recipes_id_list) == 1:
                            quantity_to_append["ingredient"] = recipes_id_list[0]
                        else:
                            print("The measure is not conclusive!")
                            break

                find_rec_id = cur.execute(f"SELECT recipe_id FROM recipes").fetchall()
                conn.commit()
                find_rec_id = find_rec_id[-1]

                cur.execute(f"""INSERT INTO quantity (recipe_id, quantity, measure_id, ingredient_id) 
                            VALUES ({find_rec_id[0]}, {quantity_to_append["quantity"]},
                                   {quantity_to_append["measure"]}, {quantity_to_append["ingredient"]});""")
                conn.commit()

        # ================================= #

        # ================================= #

        all_recipes = cur.execute("SELECT * FROM recipes").fetchall()
        recipes_id_list = [row[0] for row in all_recipes]

        #   here is the proces of inserting rows with data to the "serve" table

        meals_id_order = -1
        for recipe_id in recipes_id_list:
            meals_id_order += 1  # this change the index of meals list for every new loop in order to macht the same order of the recipes
            meal_work_list = meals_id_list[meals_id_order].replace(" ", "")
            meal_work_list = list(meal_work_list)
            for meal_id in meal_work_list:
                cur.execute(f"INSERT INTO serve (recipe_id, meal_id) VALUES ({recipe_id}, {meal_id});")
                conn.commit()

        # ================================= #
        # Last check of all tables just in case...

        for i in ["meals", "ingredients", "measures", "recipes", "serve",
                  "quantity"]:  # just a test to see all the table elements
            cur.execute(f"SELECT * FROM {i}")
            print(f'\nthis is the {i} table, {cur.fetchall()}\n')
        # ================================= #
        conn.close()


if __name__ == '__main__':
    main()
