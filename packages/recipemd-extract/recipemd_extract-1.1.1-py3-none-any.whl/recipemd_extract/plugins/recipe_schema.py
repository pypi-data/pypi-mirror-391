import scrape_schema_recipe

from recipemd.data import Recipe, Ingredient, RecipeParser


def extract(url, _):
	try:
		json_recipes = scrape_schema_recipe.scrape_url(url, python_objects=True)
	except:
		return None

	if len(json_recipes) == 0:
		return None
	json_recipe = json_recipes[0]

	tags = []
	if "cookingMethod" in json_recipe:
		tags.append(json_recipe["cookingMethod"])
	if "recipeCategory" in json_recipe:
		append_or_extend(tags, json_recipe["recipeCategory"])
	if "recipeCuisine" in json_recipe:
		tags.append(json_recipe["recipeCuisine"])
	if "keywords" in json_recipe:
		kw = json_recipe["keywords"]
		if isinstance(kw, str):
			kw = kw.split(',')
		append_or_extend(tags, kw)

	description_parts = []
	if "description" in json_recipe:
		description_parts.append(json_recipe["description"])
	if "image" in json_recipe:
		if isinstance(json_recipe["image"], list):
			description_parts.append(f'![]({json_recipe["image"][0]}")')
		else:
			description_parts.append(f'![]({json_recipe["image"]}")')

	yields = []
	if "recipeYield" in json_recipe:
		yields.append(RecipeParser.parse_amount(json_recipe["recipeYield"]))

	recipe = Recipe(
		title=json_recipe["name"],
		description="\n\n".join(description_parts),
		tags=tags,
		yields=yields,
		ingredients=[Ingredient(name=ingred) for ingred in json_recipe["recipeIngredient"]],
		instructions=f'{create_instructions(json_recipe["recipeInstructions"])}\n\n{json_recipe["url"]}',
	)

	return recipe


def create_instructions(instructions, level=2):
	if isinstance(instructions, list):
		return "\n\n".join(create_instructions(el, level) for el in instructions)

	if "@type" in instructions:
		instruction_type = instructions["@type"]

		if instruction_type == "HowToSection":
			child_instructions_list = []
			for child_instruction in instructions["itemListElement"]:
				child_instructions_list.append(create_instructions(child_instruction, level=level+1))
			child_instructions_list = "\n\n".join(child_instructions_list)

			return f'{"#"*level} \n\n{child_instructions_list}'

		if instruction_type == "HowToStep":
			return instructions["text"]

	return str(instructions)


def append_or_extend(list_to_add_to, to_add):
	if isinstance(to_add, list):
		list_to_add_to.extend(to_add)
	else:
		list_to_add_to.append(to_add)