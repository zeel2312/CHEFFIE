# run.py

import json
from collections import defaultdict
from cbr_retrieval import load_recipes, rank_recipes
from llm import call_llm_for_meal_completion

def load_fridge(path="data/fridge.json"):
    with open(path, "r") as f:
        return json.load(f)

def save_fridge(fridge, path="data/fridge.json"):
    with open(path, "w") as f:
        json.dump(fridge, f, indent=2)

def get_user_preferences():
    print("How many days of meals do you want?")
    days = int(input("> "))

    print("How many meals per day?")
    meals_per_day = int(input("> "))

    print("Enter your target calories per day (kcal):")
    target_calories_per_day = float(input("> "))

    print("Enter your target protein per day (g):")
    protein_per_day = float(input("> "))

    print("Enter your target fat per day (g):")
    fat_per_day = float(input("> "))

    print("Enter your target carbs per day (g):")
    carbs_per_day = float(input("> "))

    print("Choose your main priority (calories/protein/fat/carbs):")
    priority = input("> ").strip().lower()

    return {
        "days": days,
        "meals_per_day": meals_per_day,
        "target_calories_per_day": target_calories_per_day,
        "target_macros_per_day": {
            "protein": protein_per_day,
            "fat": fat_per_day,
            "carbs": carbs_per_day
        },
        "priority": priority
    }

def has_enough_ingredients(adjusted_ingredients, fridge):
    for ingredient, required_amount in adjusted_ingredients.items():
        if ingredient not in fridge or fridge[ingredient] < required_amount:
            return False
    return True

def use_ingredients(adjusted_ingredients, fridge):
    for ingredient, used_amount in adjusted_ingredients.items():
        if ingredient in fridge:
            fridge[ingredient] -= used_amount
            if fridge[ingredient] <= 0:
                fridge[ingredient] = 0

def calculate_missing_ingredients(adjusted_ingredients, fridge):
    missing = {}
    for ingredient, required_amount in adjusted_ingredients.items():
        available = fridge.get(ingredient, 0)
        if available < required_amount:
            missing[ingredient] = required_amount - available
    return missing

def build_meal_plan(recipes, fridge, preferences):
    days = preferences["days"]
    meals_per_day = preferences["meals_per_day"]
    total_meals = days * meals_per_day

    target_calories_per_meal = preferences["target_calories_per_day"] / meals_per_day
    target_macros_per_meal = {
        macro: amount / meals_per_day
        for macro, amount in preferences["target_macros_per_day"].items()
    }
    priority = preferences["priority"]

    user_ingredients = list(fridge.keys())

    top_matches = rank_recipes(
        recipes,
        user_ingredients,
        target_macros_per_meal,
        target_calories_per_meal,
        priority,
        top_k=total_meals * 3  # Oversample to have options
    )

    selected_meals = []
    pending_meals = []
    missing_ingredients_list = defaultdict(float)

    for match in top_matches:
        adjusted = match["adjusted_recipe"]
        
        if has_enough_ingredients(adjusted["ingredients"], fridge):
            selected_meals.append(match)
            use_ingredients(adjusted["ingredients"], fridge)
        else:
            pending_meals.append(match)
            missing = calculate_missing_ingredients(adjusted["ingredients"], fridge)
            for ing, amount in missing.items():
                missing_ingredients_list[ing] += amount

    return selected_meals, pending_meals, missing_ingredients_list

def print_meal_plan(selected_meals, pending_meals, missing_ingredients, preferences):
    days = preferences["days"]
    meals_per_day = preferences["meals_per_day"]
    priority = preferences["priority"]

    total_needed = days * meals_per_day

    print("\n   Meals Generated with Current Ingredients:\n")
    for idx, match in enumerate(selected_meals):
        adjusted = match["adjusted_recipe"]
        print(f"Meal {idx+1}: {adjusted['title']} (Score: {match['final_score']:.2f})")
        print(f"  - Servings: {adjusted['servings_needed']}")
        print(f"  - Calories: {adjusted['total_calories']} kcal")
        print(f"  - Macros: {adjusted['adjusted_macros']}\n")

    if len(selected_meals) < total_needed:
        print("\n   Not enough meals could be made. Missing ingredients:\n")
        for ing, amount in missing_ingredients.items():
            print(f"  - {ing}: {round(amount, 2)}g needed")

        print("\n🛒 Meals Possible After Shopping:\n")
        for idx, match in enumerate(pending_meals[:(total_needed - len(selected_meals))]):
            adjusted = match["adjusted_recipe"]
            print(f"Meal {idx+1}: {adjusted['title']} (Score: {match['final_score']:.2f})")
            print(f"  - Servings: {adjusted['servings_needed']}")
            print(f"  - Calories: {adjusted['total_calories']} kcal")
            print(f"  - Macros: {adjusted['adjusted_macros']}\n")

def main():
    recipes = load_recipes()
    fridge = load_fridge()
    preferences = get_user_preferences()

    selected_meals, pending_meals, missing_ingredients = build_meal_plan(recipes, fridge, preferences)

    print_meal_plan(selected_meals, pending_meals, missing_ingredients, preferences)
    save_fridge(fridge)

    # If not enough meals, call LLM to complete
    total_meals_needed = preferences["days"] * preferences["meals_per_day"]
    if len(selected_meals) < total_meals_needed:
        meals_needed = total_meals_needed - len(selected_meals)

        llm_response = call_llm_for_meal_completion(
                                                    
            preferences,
            fridge,
            selected_meals,
            missing_ingredients,
            meals_needed
        )

  
        print("\nOh no! looks like there's a mismatch between your ingredients and what we can make.")
        print("\nAssistant Chefie's Proposed Meals Based on Your Ingredients:\n")

        if llm_response:
            try:
                proposed_meals = json.loads(llm_response)
                print("\nOh no! looks like there's a mismatch between your ingredients and what we can make.")
                print("\nAssistant Chefie's Proposed Meals Based on Your Ingredients:\n")
                for i, meal in enumerate(proposed_meals):
                    print(f"\nMeal {i+1}: {meal['meal_title']}")
                    print("Ingredients:")
                    for ingredient, grams in meal["ingredients"].items():
                        print(f"  - {ingredient.capitalize()}: {grams}g")
                    print("Estimated Nutrition:")
                    print(f"  Calories: {meal['estimated_nutrition'].get('calories', 'N/A')} kcal")
                    print(f"  Protein: {meal['estimated_nutrition'].get('protein', 'N/A')} g")
                    print(f"  Fat: {meal['estimated_nutrition'].get('fat', 'N/A')} g")
                    print(f"  Carbs: {meal['estimated_nutrition'].get('carbs', 'N/A')} g")

            except json.JSONDecodeError:
                print("Failed to parse LLM response as JSON.")
        
if __name__ == "__main__":
    main()