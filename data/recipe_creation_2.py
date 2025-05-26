import random
import json

# Ingredient categories
proteins = ["chicken", "beef", "tofu", "salmon", "eggs", "lentils", "black beans"]
dairy = ["cheese", "milk", "yogurt", "coconut milk"]
vegetables = ["spinach", "carrots", "potatoes", "onion", "garlic", "bell pepper", "zucchini", "mushrooms", "tomato", "cucumber", "kale", "broccoli"]
carbs = ["rice", "quinoa", "oats", "bread"]
flavors = ["olive oil", "turmeric", "ginger", "basil", "cilantro", "peanut butter"]

# Dish patterns (chef-inspired titles)
title_templates = [
    ("protein", "dairy", "{} and {} Skillet"),
    ("protein", "vegetable", "{} and {} Stir-Fry"),
    ("protein", "carb", "{} and {} Bowl"),
    ("vegetable", "dairy", "{} and {} Casserole"),
    ("protein", "dairy", "{} with {} Sauce"),
    ("vegetable", "carb", "{} and {} Bake"),
    ("protein", "vegetable", "Grilled {} with {}"),
    ("protein", "vegetable", "Spicy {} and {} Curry"),
    ("vegetable", "dairy", "{} and Creamy {} Soup"),
    ("protein", "carb", "{} Fried {} Bowl")
]

# Helper for macros
def generate_macros():
    protein = round(random.uniform(10, 35), 1)
    fat = round(random.uniform(5, 30), 1)
    carbs = round(random.uniform(15, 60), 1)
    sodium = round(random.uniform(100, 1400), 1)
    calories = round(protein * 4 + fat * 9 + carbs * 4 + random.uniform(-30, 50), 1)
    return calories, {
        "protein": protein,
        "fat": fat,
        "sodium": sodium,
        "carbs": carbs
    }

# Updated recipe generator with final format
def generate_recipe():
    ingredients = []

    # Step 1: Pick a logical combo
    p = random.choice(proteins)
    ingredients.append(p)

    if p in ["tofu", "eggs", "lentils", "black beans"]:
        d = random.choice(dairy)
    else:
        d = random.choice(dairy + flavors)
    ingredients.append(d)

    v = random.choice(vegetables)
    ingredients.append(v)

    c = random.choice(carbs)
    ingredients.append(c)

    f = random.choice(flavors)
    if f not in ingredients:
        ingredients.append(f)

    extra = random.sample([i for i in (proteins + dairy + vegetables + carbs + flavors) if i not in ingredients], k=random.randint(0, 2))
    ingredients.extend(extra)
    ingredients = list(set(ingredients))

    # Step 2: Build title from templates based on core pair
    template = random.choice(title_templates)
    i1 = p if template[0] == "protein" else (v if template[0] == "vegetable" else d)
    i2 = d if template[1] == "dairy" else (v if template[1] == "vegetable" else c)
    title = template[2].format(i1.capitalize(), i2.capitalize())

    # Step 3: Store ingredients with numeric quantities only
    ingredient_quantities = {i: random.randint(30, 250) for i in ingredients}
    calories, macros = generate_macros()

    return {
        "title": title,
        "rating": round(random.uniform(2.5, 5.0), 2),
        "calories": calories,
        "macros": macros,
        "ingredients": ingredient_quantities
    }

# Generate 1000 updated recipes
final_recipes_updated = [generate_recipe() for _ in range(1000)]

# Save to file
output_path_final_updated = "/mnt/data/final_clean_chef_recipes_1000.json"
with open(output_path_final_updated, "w") as f:
    json.dump(final_recipes_updated, f, indent=2)

output_path_final_updated
