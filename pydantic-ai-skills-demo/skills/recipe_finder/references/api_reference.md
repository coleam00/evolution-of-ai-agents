# Recipe API Reference

This skill uses two free recipe APIs: TheMealDB (simpler, unlimited) and Spoonacular (more powerful, limited free tier).

---

# TheMealDB API

Completely free, no signup required. Good for basic recipe searches.

## Base URL

```
https://www.themealdb.com/api/json/v1/1
```

Note: Use `1` as the API key for the free tier.

---

## Search Endpoints

### Search by Name

**GET** `/search.php?s={query}`

Search recipes by name.

```
https://www.themealdb.com/api/json/v1/1/search.php?s=chicken
```

### Search by First Letter

**GET** `/search.php?f={letter}`

Get all recipes starting with a letter.

```
https://www.themealdb.com/api/json/v1/1/search.php?f=c
```

### Lookup by ID

**GET** `/lookup.php?i={id}`

Get full recipe details by ID.

```
https://www.themealdb.com/api/json/v1/1/lookup.php?i=52772
```

### Random Recipe

**GET** `/random.php`

Get a single random recipe.

```
https://www.themealdb.com/api/json/v1/1/random.php
```

---

## Filter Endpoints

### Filter by Ingredient

**GET** `/filter.php?i={ingredient}`

Find recipes containing a specific ingredient.

```
https://www.themealdb.com/api/json/v1/1/filter.php?i=chicken_breast
```

**Note:** Returns only id, name, and thumbnail. Use lookup for full details.

### Filter by Category

**GET** `/filter.php?c={category}`

Filter by meal category.

```
https://www.themealdb.com/api/json/v1/1/filter.php?c=Seafood
```

Categories: Beef, Breakfast, Chicken, Dessert, Goat, Lamb, Miscellaneous, Pasta, Pork, Seafood, Side, Starter, Vegan, Vegetarian

### Filter by Area/Cuisine

**GET** `/filter.php?a={area}`

Filter by cuisine/country.

```
https://www.themealdb.com/api/json/v1/1/filter.php?a=Italian
```

Areas: American, British, Canadian, Chinese, Croatian, Dutch, Egyptian, Filipino, French, Greek, Indian, Irish, Italian, Jamaican, Japanese, Kenyan, Malaysian, Mexican, Moroccan, Polish, Portuguese, Russian, Spanish, Thai, Tunisian, Turkish, Unknown, Vietnamese

---

## List Endpoints

### List All Categories

**GET** `/categories.php`

Get all meal categories with descriptions.

### List Category Names

**GET** `/list.php?c=list`

Get just category names.

### List All Areas

**GET** `/list.php?a=list`

Get all cuisine areas.

### List All Ingredients

**GET** `/list.php?i=list`

Get all available ingredients.

---

## Response Format

### Full Recipe Object

```json
{
  "meals": [
    {
      "idMeal": "52772",
      "strMeal": "Teriyaki Chicken Casserole",
      "strCategory": "Chicken",
      "strArea": "Japanese",
      "strInstructions": "Preheat oven to 350...",
      "strMealThumb": "https://www.themealdb.com/images/media/meals/wvpsxx1468256321.jpg",
      "strYoutube": "https://www.youtube.com/watch?v=4aZr5hZXP_s",
      "strIngredient1": "soy sauce",
      "strIngredient2": "water",
      "strIngredient3": "brown sugar",
      "strMeasure1": "3/4 cup",
      "strMeasure2": "1/2 cup",
      "strMeasure3": "1/4 cup",
      "strSource": "https://example.com/recipe",
      "strTags": "Meat,Casserole"
    }
  ]
}
```

**Note:** Ingredients and measures are in separate numbered fields (strIngredient1-20, strMeasure1-20). Empty ingredients should be ignored.

---

# Spoonacular API

More powerful with nutrition data and dietary filters. Free tier: 150 points/day.

## Base URL

```
https://api.spoonacular.com
```

## Authentication

All requests require `apiKey` parameter:
```
?apiKey=YOUR_API_KEY
```

---

## Recipe Search

### Complex Search

**GET** `/recipes/complexSearch`

Powerful search with many filters.

| Parameter | Description |
|-----------|-------------|
| `query` | Search keywords |
| `cuisine` | Cuisine type(s) |
| `diet` | Diet type |
| `intolerances` | Allergies/intolerances |
| `type` | Meal type (main course, dessert, etc.) |
| `maxReadyTime` | Max prep+cook time in minutes |
| `minCalories` / `maxCalories` | Calorie range |
| `number` | Number of results (1-100) |
| `offset` | Pagination offset |
| `addRecipeNutrition` | Include nutrition (costs more points) |

**Example:**
```
https://api.spoonacular.com/recipes/complexSearch?query=pasta&diet=vegetarian&maxReadyTime=30&number=5&apiKey=KEY
```

### Search by Ingredients

**GET** `/recipes/findByIngredients`

Find recipes using specific ingredients.

| Parameter | Description |
|-----------|-------------|
| `ingredients` | Comma-separated ingredients |
| `number` | Number of results |
| `ranking` | 1=maximize used, 2=minimize missing |
| `ignorePantry` | Ignore common pantry items |

**Example:**
```
https://api.spoonacular.com/recipes/findByIngredients?ingredients=chicken,garlic,onion&number=5&apiKey=KEY
```

### Random Recipes

**GET** `/recipes/random`

Get random recipes.

| Parameter | Description |
|-----------|-------------|
| `number` | How many recipes |
| `tags` | Filter tags (vegetarian, dessert, etc.) |

**Example:**
```
https://api.spoonacular.com/recipes/random?number=1&tags=vegetarian,main+course&apiKey=KEY
```

---

## Recipe Details

### Get Recipe Information

**GET** `/recipes/{id}/information`

Get full recipe details including nutrition.

| Parameter | Description |
|-----------|-------------|
| `includeNutrition` | Include detailed nutrition |

**Example:**
```
https://api.spoonacular.com/recipes/716429/information?includeNutrition=true&apiKey=KEY
```

### Get Similar Recipes

**GET** `/recipes/{id}/similar`

Find recipes similar to a given one.

```
https://api.spoonacular.com/recipes/716429/similar?number=5&apiKey=KEY
```

---

## Nutrition Endpoints

### Nutrition by ID

**GET** `/recipes/{id}/nutritionWidget.json`

Get nutrition breakdown for a recipe.

```
https://api.spoonacular.com/recipes/716429/nutritionWidget.json?apiKey=KEY
```

### Analyze Recipe

**POST** `/recipes/analyze`

Analyze a recipe's nutrition from ingredients.

```json
{
  "title": "Spaghetti Carbonara",
  "servings": 4,
  "ingredients": [
    "400g spaghetti",
    "200g pancetta",
    "4 egg yolks",
    "100g parmesan"
  ]
}
```

---

## Diet & Intolerance Values

### Diets

| Value | Description |
|-------|-------------|
| `gluten free` | No gluten |
| `ketogenic` | Keto diet (high fat, low carb) |
| `vegetarian` | No meat |
| `lacto-vegetarian` | Vegetarian + dairy |
| `ovo-vegetarian` | Vegetarian + eggs |
| `vegan` | No animal products |
| `pescetarian` | Vegetarian + fish |
| `paleo` | Paleo diet |
| `primal` | Primal diet |
| `low fodmap` | Low FODMAP |
| `whole30` | Whole30 diet |

### Intolerances

| Value | Description |
|-------|-------------|
| `dairy` | No milk products |
| `egg` | No eggs |
| `gluten` | No gluten |
| `grain` | No grains |
| `peanut` | No peanuts |
| `seafood` | No seafood |
| `sesame` | No sesame |
| `shellfish` | No shellfish |
| `soy` | No soy |
| `sulfite` | No sulfites |
| `tree nut` | No tree nuts |
| `wheat` | No wheat |

---

## Cuisine Types

african, american, british, cajun, caribbean, chinese, eastern european, european, french, german, greek, indian, irish, italian, japanese, jewish, korean, latin american, mediterranean, mexican, middle eastern, nordic, southern, spanish, thai, vietnamese

---

## Meal Types

| Type | Description |
|------|-------------|
| `main course` | Entrees |
| `side dish` | Side dishes |
| `dessert` | Desserts |
| `appetizer` | Starters |
| `salad` | Salads |
| `bread` | Breads |
| `breakfast` | Breakfast items |
| `soup` | Soups |
| `beverage` | Drinks |
| `sauce` | Sauces |
| `marinade` | Marinades |
| `fingerfood` | Finger foods |
| `snack` | Snacks |
| `drink` | Drinks |

---

## Point Costs (Free Tier)

The free tier has 150 points/day. Approximate costs:

| Endpoint | Points |
|----------|--------|
| complexSearch | 1 |
| findByIngredients | 1 |
| random | 1 |
| Recipe information | 1 |
| Nutrition widget | 1 |
| Analyze recipe | 1.5 |

**Tip:** Use TheMealDB for basic searches to save Spoonacular points for nutrition queries.

---

## Error Responses

| Code | Meaning |
|------|---------|
| 200 | Success |
| 401 | Invalid API key |
| 402 | Payment required (over quota) |
| 404 | Not found |
| 429 | Rate limit exceeded |

---

## Building Recipe Image URLs

### TheMealDB
Images are included in responses as `strMealThumb`.

### Spoonacular
Build image URLs:
```
https://spoonacular.com/recipeImages/{id}-312x231.jpg
```

Sizes: 90x90, 240x150, 312x231, 480x360, 556x370, 636x393
