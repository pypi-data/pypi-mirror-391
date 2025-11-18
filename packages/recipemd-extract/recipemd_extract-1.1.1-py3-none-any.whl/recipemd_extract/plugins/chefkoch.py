from decimal import Decimal

from recipemd.data import RecipeParser, Recipe, Ingredient, Amount


def extract(url,soup):
	if 'chefkoch.de' not in url:
		return

	# title
	title = soup.find('h1', attrs={'class': 'page-title'}).text
	if title == 'Fehler: Seite nicht gefunden' or title == 'Fehler: Rezept nicht gefunden':
		raise ValueError('No recipe found, check URL')
	# summary
	summaryTag = soup.find('div', attrs={'class': 'summary'})
	summary = summaryTag.text if summaryTag else None
	# servings
	servings= soup.find('input', attrs={'id':'divisor'}).attrs['value']
	yields=[Amount(Decimal(servings), f'Portion{"en" if int(servings) > 1 else ""}')]

	# tags
	tags=[]
	tagcloud=soup.find('ul', attrs={'class':'tagcloud'})
	for tag in tagcloud.find_all('a'):
		tags.append(tag.text)
	# ingredients
	table = soup.find('table', attrs={'class': 'incredients'})
	rows = table.find_all('tr')

	ingreds=[]
	for row in rows:
		cols = row.find_all('td')
		cols = [s.text.strip() for s in cols]
		amount = RecipeParser.parse_amount(cols[0])
		ingreds.append(Ingredient(name=cols[1],amount=amount))
	# instructions
	instruct = soup.find('div', attrs={'id': 'rezept-zubereitung'}).text  # only get text
	instruct = instruct.strip()  # remove leadin and ending whitespace
	# write to file
	return Recipe(title=title, ingredients=ingreds, instructions=instruct, description=summary, tags=tags, yields=yields)
