import re
from decimal import Decimal

from recipemd.data import Recipe, Ingredient, Amount


def extract(url,soup):
	if 'seriouseats.com' not in url:
		return

	# title
	title = soup.find('h1',attrs={'class':'title recipe-title'}).text.strip()

	# summary
	summary=''

	summaryPars=soup.find('div',attrs={'class':'recipe-introduction-body'}).find_all('p')

	for par in summaryPars:
		if 'caption' not in par.attrs.get('class',[]):
			summary = summary + par.text + '\n\n'
	summary=summary.strip()

	# servings
	yields = []

	servings = soup.find('span',attrs={'class':'info yield'}).text
	servings_factor = re.compile(r"\d+").findall(servings)
	if servings_factor:
		yields.append(Amount(Decimal(servings_factor[0]), 'servings'))

	# tags
	tags=[]
	for tag in soup.find_all('a',attrs={'class':'tag'}):
		tags.append(tag.text)

	# ingredients
	ingredients=[]

	for ingred in soup.find_all('li',attrs={'class':'ingredient'}):
		ingredients.append(Ingredient(name=ingred.text))

	# instructions
	instructions=''

	for step in soup.find_all('li',attrs={'class':'recipe-procedure'}):
		stepNumber = step.find('div',attrs={'class':'recipe-procedure-number'}).text.strip()
		stepInstr = step.find('div',attrs={'class':'recipe-procedure-text'}).text.strip()

		instructions = instructions + stepNumber + ' ' + stepInstr + '\n'
	instructions=instructions.strip()

	return Recipe(title=title,ingredients=ingredients,instructions=instructions,description=summary,tags=tags,yields=yields)
