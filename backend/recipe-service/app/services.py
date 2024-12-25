def validate_recipe_data(data):
    required_fields = ['title', 'description', 'ingredients', 'instructions']
    for field in required_fields:
        if field not in data:
            return False, f"'{field}' is required."
    return True, None
