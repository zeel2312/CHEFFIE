# meal_planner.py

import os
import time
import json
from collections import defaultdict
from cbr_retrieval import load_recipes, rank_recipes
from llm import call_llm_for_meal_completion

# Fridge Management
def load_fridge(path="data/fridge.json"):
    with open(path, "r") as f:
        return json.load(f)

def save_fridge(fridge, path="data/fridge.json"):
    # print("Saving fridge to:", os.path.abspath(path))
    with open(path, "w") as f:
        json.dump(fridge, f, indent=2)
    # Immediately read back and print
    with open(path, "r") as f:
        print("File contents after save:", f.read())

# Ingredient Checking
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

# Meal Planning
def build_meal_plan(recipes, fridge, preferences):
    days = preferences["days"] # number of days # for example, 3 days
    meals_per_day = preferences["meals_per_day"] # number of meals per day # for example, 2 meals per day
    total_meals = days * meals_per_day # total number of meals # for example, 3 days * 2 meals per day = 6 meals

    target_calories_per_meal = preferences["target_calories_per_day"] / meals_per_day # target calories per meal # for example, 1500 calories / 2 meals per day = 750 calories per meal
    target_macros_per_meal = {
        macro: amount / meals_per_day # target macros per meal # for example, 100g protein / 2 meals per day = 50g protein per meal
        for macro, amount in preferences["target_macros_per_day"].items()
    }
    priority = preferences["priority"] # priority of the meal plan (calories/protein/fat/carbs) # for example, "calories"

    user_ingredients = list(fridge.keys()) # list of ingredients in the fridge # for example, ["chicken", "rice", "broccoli"]
    
    # with all the information, we can now rank the recipes
    # we will use the rank_recipes function to rank the recipes

    top_matches = rank_recipes(
        recipes, # we will use the database of recipes to retrieve the relevant recipes
        user_ingredients, # we will use the user_ingredients parameter to target the ingredients in the fridge
        target_macros_per_meal, # we will use the target_macros_per_meal parameter to target the macros per meal
        target_calories_per_meal, # we will use the target_calories_per_meal parameter to target the calories per meal
        priority, # we will use the priority parameter to prioritize the recipes
        top_k=total_meals * 3 # we will use the top_k parameter to limit the number of recipes to return
    )

    selected_meals = []
    pending_meals = []
    missing_ingredients_list = defaultdict(float)

    for match in top_matches:
        adjusted = match["adjusted_recipe"]

        if has_enough_ingredients(adjusted["ingredients"], fridge):
            selected_meals.append({
                "meal_title": adjusted["title"],
                "ingredients": adjusted["ingredients"],
                "estimated_nutrition": adjusted["adjusted_macros"]
            })
            use_ingredients(adjusted["ingredients"], fridge)
        else:
            pending_meals.append(match)
            missing = calculate_missing_ingredients(adjusted["ingredients"], fridge)
            for ing, amount in missing.items():
                missing_ingredients_list[ing] += amount

    return selected_meals, pending_meals, missing_ingredients_list

# LLM xtension 
def complete_meal_plan_with_llm(preferences, fridge, selected_meals, missing_ingredients, meals_needed):
    llm_response = call_llm_for_meal_completion(
        preferences,
        fridge,
        selected_meals,
        missing_ingredients,
        meals_needed
    )
    
    if not llm_response:
        return []

    try:
        proposed_meals = json.loads(llm_response)

        # ---- NEW: burn ingredients ----
        for meal in proposed_meals:
            use_ingredients(meal["ingredients"], fridge)
        save_fridge(fridge)
        # --------------------------------

        return proposed_meals

    except json.JSONDecodeError:
        print("Failed to parse LLM response as JSON.")
        return []