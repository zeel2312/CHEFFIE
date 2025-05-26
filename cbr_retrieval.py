import json
from typing import List, Dict
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# load recipes
def load_recipes(path = "data/final_clean_chef_recipes_1000.json"):
    with open(path, "r") as f:
        return json.load(f)


def compute_similarity(recipe, user_ingredients: set, target_macros: dict, target_calories: float):
    # recipe_ingredients = set(recipe["ingredients"])
    recipe_ingredients = set(recipe["ingredients"].keys()) # get the ingredients for the recipe, for example, ["chicken", "rice", "broccoli"]
    common_ingredients = user_ingredients & recipe_ingredients # get the common ingredients between the recipe and the user's ingredients
    ingredient_score = len(common_ingredients) / len(recipe_ingredients) if recipe_ingredients else 0 # calculate the ingredient score

    recipe_macros = np.array([
        recipe["macros"].get("protein", 0),
        recipe["macros"].get("fat", 0),
        recipe["macros"].get("carbs", 0)
    ])
    target_macros_array = np.array([target_macros["protein"], target_macros["fat"], target_macros["carbs"]])
    macro_distance = np.linalg.norm(recipe_macros - target_macros_array)

    recipe_calories = recipe.get("calories", 0)
    calorie_distance = abs(recipe_calories - target_calories)

    rating_score = recipe.get("rating", 0) / 5

    return {
        "recipe": recipe,
        "ingredient_score": ingredient_score,
        "macro_distance": macro_distance,
        "calorie_distance": calorie_distance,
        "rating_score": rating_score
    }


def rank_recipes(recipes, user_ingredients, target_macros, target_calories, priority, top_k): # rank the recipes based on the user's preferences
    user_ingredients = set(user_ingredients) # convert the user's ingredients to a set
    scored = [ # loop through each recipe and compute the similarity between the recipe and the user's preferences
        compute_similarity(r, user_ingredients, target_macros, target_calories) # compute_similarity(one recipe at a time, fridge contents, required protein/fat/carbs per meal, required calories per meal)
        for r in recipes
    ]

    if not scored:
        return []

    scaler = MinMaxScaler()

    ingredient_scores = scaler.fit_transform([[s["ingredient_score"]] for s in scored]).flatten()
    macro_scores = scaler.fit_transform([[s["macro_distance"]] for s in scored])
    macro_scores = 1 - macro_scores.flatten()

    calorie_scores = scaler.fit_transform([[s["calorie_distance"]] for s in scored])
    calorie_scores = 1 - calorie_scores.flatten()

    rating_scores = scaler.fit_transform([[s["rating_score"]] for s in scored]).flatten()

    final_scores = (
        0.4 * ingredient_scores +
        0.25 * macro_scores +
        0.25 * calorie_scores +
        0.1 * rating_scores
    )

    for i, s in enumerate(scored):
        s["final_score"] = final_scores[i]
        # Attach adjusted recipe scaled to target_calories
        s["adjusted_recipe"] = adjust_serving_size(s["recipe"], target_macros, target_calories, priority)

    return sorted(scored, key=lambda x: x["final_score"], reverse=True)[:top_k]



def adjust_serving_size(recipe, target_macros, target_calories, priority):
    # Determine what to base the scaling on
    if priority == "calories":
        base_value = recipe.get("calories", 0)
        target_value = target_calories
    elif priority in recipe["macros"]:
        base_value = recipe["macros"].get(priority, 0)
        target_value = target_macros.get(priority, 0)
    else:
        return {
            "error": "Invalid priority selected."
        }

    if base_value == 0:
        return {
            "error": f"Recipe has no {priority} info. Cannot adjust servings."
        }

    servings_needed = target_value / base_value

    # Scale macros
    scaled_macros = {
        macro: round(value * servings_needed, 2)
        for macro, value in recipe["macros"].items()
    }

    # Round off those updated ingredient values to nearest 5g
    def round_to_nearest_five(x):
        return int(5 * round(x/5))

    # Scale ingredients
    scaled_ingredients = {
        ingredient: round_to_nearest_five(amount * servings_needed)
        for ingredient, amount in recipe["ingredients"].items()
    }

    # Return adjusted recipe
    return {
        "title": recipe["title"],
        "ingredients": scaled_ingredients,
        "original_calories_per_serving": recipe.get("calories", 0),
        "servings_needed": round(servings_needed, 2),
        "total_calories": round(servings_needed * recipe.get("calories", 0), 2),
        "adjusted_macros": scaled_macros,
        "rating": recipe.get("rating", None),
        "priority": priority
    }


#used for testing 
def main():
    recipes = load_recipes()

    print("Enter your available ingredients (comma-separated):")
    ingredients_input = input("> ").strip()
    user_ingredients = [i.strip().lower() for i in ingredients_input.split(",")]

    print("Enter your target calories (kcal):")
    target_calories = float(input("> "))
    print("Enter your target protein (g):")
    protein = float(input("> "))
    print("Enter your target fat (g):")
    fat = float(input("> "))
    print("Enter your target carbs (g):")
    carbs = float(input("> "))

    target_macros = {"protein": protein, "fat": fat, "carbs": carbs}

    print("Choose your main priority (calories/protein/fat/carbs):")
    priority = input("> ").strip().lower()

    top_matches = rank_recipes(recipes, user_ingredients, target_macros, target_calories, priority, top_k=5)

    print("\nTop Recipe Matches (Prioritized for {}):\n".format(priority.capitalize()))
    for match in top_matches:
        adjusted = match["adjusted_recipe"]
        print(f"\n{adjusted['title']} (Score: {match['final_score']:.2f})")
        print(f"Priority: {priority.capitalize()}")
        print(f"Servings needed: {adjusted['servings_needed']}")
        print(f"Total calories: {adjusted['total_calories']} kcal")
        print(f"Adjusted macros: {adjusted['adjusted_macros']}")
        print("Adjusted Ingredients:")
        for ingredient, grams in adjusted['ingredients'].items():
            print(f"  - {ingredient}: {grams}g")




if __name__ == "__main__":
    main()
