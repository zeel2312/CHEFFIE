from flask import Flask, render_template, request
from meal_planner import load_fridge, save_fridge, build_meal_plan, complete_meal_plan_with_llm
from cbr_retrieval import load_recipes
import json

app = Flask(__name__)
recipes = load_recipes()

@app.route("/", methods=["GET", "POST"])
def home():
    fridge = load_fridge()
    selected_meals = []
    pending_meals = []
    missing_ingredients = {}
    proposed_meals = []
    preferences = {}

    if request.method == "POST":
        action = request.form.get("action")

        # ---------- save_fridge ONLY ---------------------------------
        if action == "save_fridge":
            updated_fridge = {}
            for key, val in request.form.items():
                if key.startswith("fridge_"):
                    ingredient = key.replace("fridge_", "").lower()
                    try:
                        grams = float(val)
                        if grams > 0:
                            updated_fridge[ingredient] = grams
                    except ValueError:
                        pass
            save_fridge(updated_fridge)  # Save fridge contents only in this action
            fridge = updated_fridge  # Update fridge data in memory
            return render_template("home.html", fridge=fridge, preferences=preferences,
                                   selected_meals=selected_meals, pending_meals=pending_meals,
                                   missing_ingredients=missing_ingredients, proposed_meals=proposed_meals)

        # ---------- plan_meals ---------------------------------------
        elif action == "plan_meals":
            # Process preferences from form and pass them back to frontend
            days = int(request.form["days"])
            meals_per_day = int(request.form["meals_per_day"])
            calories = float(request.form["calories"])
            protein = float(request.form["protein"])
            fat = float(request.form["fat"])
            carbs = float(request.form["carbs"])
            priority = request.form["priority"].strip().lower()

            preferences = {
                "days": days,
                "meals_per_day": meals_per_day,
                "target_calories_per_day": calories,
                "target_macros_per_day": {
                    "protein": protein,
                    "fat": fat,
                    "carbs": carbs
                },
                "priority": priority
            }

            # Build meal plan using the existing fridge data
            selected_meals, pending_meals, missing_ingredients = build_meal_plan(recipes, fridge, preferences)
            
            save_fridge(fridge)

            total_needed = days * meals_per_day
            if len(selected_meals) < total_needed:
                meals_needed = total_needed - len(selected_meals)
                proposed_meals = complete_meal_plan_with_llm(
                    preferences,
                    fridge,
                    selected_meals,
                    missing_ingredients,
                    meals_needed
                )

            # Pass preferences and selected meals back to the frontend so the form is not reset
            return render_template(
                "home.html",
                fridge=fridge,
                preferences=preferences,  # Ensure preferences are passed for form data
                selected_meals=selected_meals,
                pending_meals=pending_meals,
                missing_ingredients=missing_ingredients,
                proposed_meals=proposed_meals
            )

    # If no form submission, render page with empty preferences (first load)
    return render_template("home.html", fridge=fridge, preferences=preferences)


if __name__ == "__main__":
    app.run(debug=True)
