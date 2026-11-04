
def generate_recommendation(skin_type, concerns, sensitivity):

    morning_routine = [
        "Gentle cleanser",
        "Moisturiser",
        "Broad-spectrum SPF 30 or higher sunscreen"
    ]

    night_routine = [
        "Gentle cleanser",
        "Moisturiser"
    ]

    ingredients = []
    notes = []

    # Skin-type based suggestions
    if skin_type == "Oily":
        ingredients.append("Niacinamide")
        notes.append("Consider lightweight, non-comedogenic products.")

    elif skin_type == "Dry":
        ingredients.append("Hyaluronic acid")
        notes.append("Choose moisturisers that support your skin barrier.")

    elif skin_type == "Combination":
        ingredients.append("Niacinamide")
        notes.append("Use lightweight products and adjust moisturiser to different areas.")

    elif skin_type == "Normal":
        ingredients.append("Hyaluronic acid")
        notes.append("Focus on maintaining hydration and sun protection.")

    # Concern-based suggestions
    if "Acne" in concerns:
        ingredients.append("Salicylic acid")
        notes.append("Salicylic acid may help with clogged pores. Introduce it gradually.")

    if "Dullness" in concerns:
        ingredients.append("Vitamin C")
        notes.append("Vitamin C may help improve the appearance of dull skin.")

    if "Dark Spots" in concerns:
        ingredients.append("Niacinamide")
        notes.append("Consistent sunscreen use is important when addressing dark spots.")

    if "Blackheads" in concerns:
        ingredients.append("Salicylic acid")
        notes.append("Salicylic acid may help unclog pores.")

    # Remove duplicate ingredients
    ingredients = list(dict.fromkeys(ingredients))

    # Sensitive-skin adjustments
    if sensitivity == "Yes":

        ingredients = [
            ingredient for ingredient in ingredients
            if ingredient not in ["Salicylic acid", "Vitamin C"]
        ]

        notes.append(
            "Since you selected sensitive skin, introduce new products carefully. "
            "Patch test first and consider fragrance-free products."
        )

    return {
        "morning_routine": morning_routine,
        "night_routine": night_routine,
        "ingredients": ingredients,
        "notes": notes
    }
