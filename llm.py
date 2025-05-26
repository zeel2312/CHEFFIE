import json
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

#openrouter key
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

def build_llm_prompt(preferences, fridge, selected_meals, missing_ingredients, meals_needed):
    prompt = f"""
You are Chefie, a highly adaptive AI meal planning assistant.

Your job is to help users build personalized, realistic meal plans based on:
- Available fridge ingredients
- Their nutrition goals
- Their preferences for number of meals and days

You are creative but practical: you prefer realistic meal suggestions that are achievable with the current pantry, and you adjust flexibly when ingredients are limited.

The user wants {preferences['days']} days of meals, with {preferences['meals_per_day']} meals per day.

Their daily nutrition targets are:
- Calories: {preferences['target_calories_per_day']} kcal
- Protein: {preferences['target_macros_per_day']['protein']} g
- Fat: {preferences['target_macros_per_day']['fat']} g
- Carbs: {preferences['target_macros_per_day']['carbs']} g

Meals already selected:
{chr(10).join([f"- {meal['meal_title']}" for meal in selected_meals])}

Available ingredients in the fridge (grams):
{json.dumps(fridge, indent=2)}

Missing ingredients (estimated to fulfill planned meals):
{json.dumps(missing_ingredients, indent=2)}

Currently, {len(selected_meals)} meals have been selected, but {meals_needed} more are needed.

You must now:
- Creatively propose {meals_needed} new meals using as much of the available ingredients as possible.
- Adjust and flexibly create simple, plausible meals.
- Do NOT hallucinate ingredients that aren't listed as available.
- Stay close to the user's calorie and macro goals if possible.

For each proposed meal, include:
- A meal title
- A dictionary of ingredients and amounts in grams
- An estimated nutrition breakdown (calories, protein, fat, carbs)

⚠️ Important:
Respond ONLY with a valid JSON array in this exact format:
[
  {{
    "meal_title": "Example Meal Title",
    "ingredients": {{
      "ingredient 1": grams,
      "ingredient 2": grams
    }},
    "estimated_nutrition": {{
      "calories": number,
      "protein": number,
      "fat": number,
      "carbs": number
    }}
  }},
  ...
]

Do not add any extra text, explanation, greetings, or notes. Only respond with pure JSON.
"""
    return prompt


def call_llm_for_meal_completion(preferences, fridge, selected_meals, missing_ingredients, meals_needed):
    if OPENROUTER_API_KEY is None:
        raise ValueError("OPENROUTER_API_KEY environment variable not set.")

    prompt = build_llm_prompt(preferences, fridge, selected_meals, missing_ingredients, meals_needed)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "qwen/qwen-2.5-72b-instruct:free",
        "messages": [
            {"role": "system", "content": "You are a helpful meal planning assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print("Error contacting LLM:", response.text)
        return None