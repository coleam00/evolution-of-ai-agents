# Dietary Restrictions Guide

This guide helps you understand common dietary restrictions and how to filter recipes appropriately.

---

## Quick Reference Table

| User Says | What It Means | API Filter |
|-----------|---------------|------------|
| "vegetarian" | No meat or fish | `diet=vegetarian` |
| "vegan" | No animal products | `diet=vegan` |
| "gluten-free" | No wheat, barley, rye | `intolerances=gluten` |
| "dairy-free" | No milk products | `intolerances=dairy` |
| "keto" / "low-carb" | High fat, very low carb | `diet=ketogenic` |
| "paleo" | No grains, legumes, dairy | `diet=paleo` |
| "nut-free" | No tree nuts or peanuts | `intolerances=tree nut,peanut` |
| "egg-free" | No eggs | `intolerances=egg` |
| "pescatarian" | Vegetarian + fish | `diet=pescetarian` |
| "whole30" | No sugar, grains, legumes, dairy | `diet=whole30` |
| "healthy" | Usually means low calorie | `maxCalories=500` |
| "low sodium" | Reduced salt | Manual filtering |
| "halal" | Islamic dietary laws | Manual filtering |
| "kosher" | Jewish dietary laws | Manual filtering |

---

## Detailed Diet Explanations

### Vegetarian

**Excludes:**
- All meat (beef, pork, lamb, poultry)
- Fish and seafood
- Animal-derived gelatin

**Includes:**
- Eggs (ovo-vegetarian)
- Dairy (lacto-vegetarian)
- Honey
- Plant-based foods

**Common substitutions:**
- Meat → Tofu, tempeh, seitan, legumes
- Gelatin → Agar-agar
- Chicken broth → Vegetable broth

---

### Vegan

**Excludes:**
- All meat and fish
- Dairy (milk, cheese, butter, cream)
- Eggs
- Honey
- Gelatin
- Some sugars (processed with bone char)

**Includes:**
- All plant-based foods
- Plant milks (oat, almond, soy)
- Nutritional yeast

**Common substitutions:**
- Butter → Vegan butter, coconut oil
- Milk → Oat milk, almond milk
- Cheese → Nutritional yeast, vegan cheese
- Eggs → Flax eggs, chia eggs, aquafaba
- Honey → Maple syrup, agave

---

### Gluten-Free

**Excludes:**
- Wheat (bread, pasta, most baked goods)
- Barley
- Rye
- Spelt
- Many sauces (soy sauce contains wheat)
- Beer (unless gluten-free)

**Includes:**
- Rice
- Corn
- Quinoa
- Oats (if certified gluten-free)
- Potatoes
- All meats, fish, dairy, eggs
- Most vegetables and fruits

**Hidden gluten sources:**
- Soy sauce → Use tamari (gluten-free soy sauce)
- Worcestershire sauce
- Some salad dressings
- Imitation crab
- Malt vinegar

**Common substitutions:**
- Pasta → Rice pasta, chickpea pasta
- Flour → Almond flour, rice flour, GF flour blend
- Bread → Gluten-free bread
- Soy sauce → Tamari or coconut aminos

---

### Dairy-Free

**Excludes:**
- Milk
- Cheese
- Butter
- Cream
- Yogurt
- Ice cream
- Whey and casein (hidden in many products)

**Includes:**
- Plant milks
- Coconut cream
- Vegan cheeses
- All meats, fish, eggs

**Hidden dairy sources:**
- Many breads contain milk
- Some chips contain whey
- Margarine may contain dairy
- "Non-dairy" creamer may contain casein

**Common substitutions:**
- Milk → Oat milk, coconut milk, almond milk
- Butter → Olive oil, coconut oil, vegan butter
- Cream → Coconut cream, cashew cream
- Cheese → Nutritional yeast, vegan cheese

---

### Ketogenic (Keto)

**Macronutrient Target:**
- 70-75% fat
- 20-25% protein
- 5-10% carbs (usually <50g/day, strict <20g)

**Excludes:**
- Sugar and sweeteners (except stevia, erythritol)
- Grains (bread, rice, pasta)
- Most fruits (except berries in moderation)
- Starchy vegetables (potatoes, corn)
- Legumes (beans, lentils)

**Includes:**
- Meat and fatty fish
- Eggs
- Cheese and cream
- Nuts and seeds
- Low-carb vegetables (leafy greens, broccoli)
- Healthy oils (olive, coconut, avocado)
- Avocados

**Keto-friendly recipes typically feature:**
- High fat content
- Moderate protein
- Very low net carbs
- Cauliflower as rice/potato substitute

---

### Paleo

**Philosophy:** Eat like our ancestors (hunter-gatherers)

**Excludes:**
- Grains (wheat, rice, oats)
- Legumes (beans, lentils, peanuts)
- Dairy
- Refined sugar
- Processed foods
- Vegetable oils (canola, soybean)

**Includes:**
- Meat (preferably grass-fed)
- Fish and seafood
- Eggs
- Vegetables
- Fruits
- Nuts and seeds
- Healthy fats (olive oil, coconut oil, avocado)

**Common substitutions:**
- Pasta → Zucchini noodles, spaghetti squash
- Rice → Cauliflower rice
- Flour → Almond flour, coconut flour
- Sugar → Honey, maple syrup (in moderation)

---

### Low FODMAP

**For:** People with IBS or digestive issues

**FODMAP stands for:** Fermentable Oligosaccharides, Disaccharides, Monosaccharides, and Polyols

**High FODMAP foods to avoid:**
- Onions and garlic
- Wheat
- Many fruits (apples, pears, watermelon)
- Dairy with lactose
- Legumes
- Some sweeteners (honey, high fructose corn syrup)

**Low FODMAP alternatives:**
- Garlic-infused oil (instead of garlic)
- Green parts of scallions
- Lactose-free dairy
- Gluten-free grains

---

## Food Allergies vs. Intolerances

### Allergies (Immune Response)
- Can be life-threatening
- Complete avoidance required
- Common: peanuts, tree nuts, shellfish, fish, eggs, milk, wheat, soy

### Intolerances (Digestive Issues)
- Uncomfortable but not dangerous
- Small amounts may be tolerable
- Common: lactose, gluten, FODMAPs

**When user mentions an allergy**, treat it seriously and ensure complete exclusion.

---

## The "Big 8" Food Allergens

These account for 90% of food allergies:

1. **Milk** - Use `intolerances=dairy`
2. **Eggs** - Use `intolerances=egg`
3. **Fish** - Use `intolerances=seafood`
4. **Shellfish** - Use `intolerances=shellfish`
5. **Tree Nuts** - Use `intolerances=tree nut`
6. **Peanuts** - Use `intolerances=peanut`
7. **Wheat** - Use `intolerances=wheat`
8. **Soybeans** - Use `intolerances=soy`

---

## Combining Restrictions

Users often have multiple restrictions. Combine filters:

**Vegan + Gluten-Free:**
```
diet=vegan&intolerances=gluten
```

**Keto + Dairy-Free:**
```
diet=ketogenic&intolerances=dairy
```

**Multiple Allergies:**
```
intolerances=peanut,tree nut,dairy
```

---

## Tips for Recipe Recommendations

1. **Always clarify** if restrictions are preferences vs. allergies
2. **Check all ingredients** - hidden allergens are common
3. **Offer substitutions** when a recipe almost fits
4. **Note cross-contamination** risks for severe allergies
5. **Respect cultural/religious diets** (halal, kosher) even if not in API

---

## Common Substitution Cheat Sheet

| Original | Substitution |
|----------|--------------|
| Butter | Olive oil, coconut oil, vegan butter |
| Milk | Oat milk, almond milk, coconut milk |
| Eggs (binding) | Flax egg, chia egg, banana |
| Eggs (leavening) | Aquafaba, baking soda + vinegar |
| Flour | Almond flour, oat flour, GF blend |
| Pasta | Zucchini noodles, rice noodles |
| Rice | Cauliflower rice, quinoa |
| Sugar | Maple syrup, honey, stevia |
| Soy sauce | Tamari, coconut aminos |
| Cream | Coconut cream, cashew cream |
