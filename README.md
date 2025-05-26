# MealPlanner – AI-Augmented Meal Planning with CBR and RAG

MealPlanner is an intelligent system that assists users in planning meals tailored to their dietary goals and available ingredients. By combining **Case-Based Reasoning (CBR)** with **Retrieval Augmented Generation (RAG)**, MealPlanner suggests personalized daily meal plans, manages inventory from a virtual fridge, and proposes additional meals based on what's missing.


## Description

MealPlanner uses a hybrid approach of knowledge-based AI. It first employs a **CBR system** that retrieves and adjusts past recipes based on user preferences and ingredient availability. If the fridge does not contain enough items to generate a complete plan, a **language model** steps in to suggest feasible alternatives using the remaining fridge data and missing ingredients.

This makes MealPlanner ideal for users aiming to follow specific nutritional goals (e.g., calories, protein, fat, carbs) while reducing food waste by maximizing existing inventory usage.


## Getting Started

### Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

Running the Project: (Locally)

```bash
python3 run.py
```

To use the web application:

```bash
python3 app.py
```

## Fridge Configuration

Two versions of fridge data are available in a single file in the `data` folder:

- `fridge_contents.txt`

To switch modes, copy the desired content into `fridge.json`.  
The meal planner will trigger **LLM generation** only if the fridge cannot support a full meal plan.


## Features

- **CBR-Based Recipe Retrieval**: Matches meals based on nutritional goals and ingredient overlap.
- **Inventory-Aware Planning**: Dynamically uses and updates a virtual fridge.
- **LLM-Augmented Completion**: Proposes meals if CBR system can’t complete the plan.
- **Nutritional Customization**: Users can define daily targets for calories, protein, carbs, and fat.
- **Web and CLI Interface**: Choose between a full web app or a terminal-based workflow.
- **Expandable Dataset**: Based on the Epicurious dataset, easily modifiable for future integration.


## Structure

- `run.py`: Command-line interface to interact with the meal planner.
- `app.py`: Flask-based web interface.
- `meal_planner.py`: Core logic for meal planning and CBR workflow.
- `llm.py`: Handles prompt building and OpenAI API interaction for missing meal generation.
- `cbr_retrieval.py`: Implements similarity logic based on ingredient overlap and nutritional scoring.
- `data/`: Contains `final_clean_chef_recipes_1000.json` and `fridge.json`.


## CBR Similarity Mechanism

Our CBR system computes similarity based on:

- **Ingredient Overlap Score**
- **Nutritional Distance Score** (per meal)
- **Weighted Priority Factor** (user-chosen: e.g., calories, protein)


## Dataset

**Epicurious Recipes Dataset from Kaggle**  
🔗 [https://www.kaggle.com/datasets/hugodarwood/epirecipes](https://www.kaggle.com/datasets/hugodarwood/epirecipes)

Includes:
- Ingredients
- Cook method
- Macros: calories, protein, fat, carbs


## Demo and Documentation

- **Demo Video**: [Click here](https://drive.google.com/file/d/1Acmx_ON8sGzilV3mxxIvBzyuEIgFigeJ/view?usp=sharing)
- **Presentation Slides**: [Click here](https://docs.google.com/presentation/d/1ZhnyHg9e4dXaVpO7WTLs-NFzUPl71Nl-tLwQyo2i_8o/edit?usp=sharing)
