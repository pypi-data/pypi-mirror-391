#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import codecs
import sys
import argparse
from argparse import RawTextHelpFormatter
from recipemd.data import RecipeSerializer,Recipe
import importlib
import os


def extract(url, debug=False):
	try:
		page = requests.get(url)
	except Exception:
		print('No valid URL', file=sys.stderr)
		sys.exit(1)
	soup = BeautifulSoup(page.text, "html5lib")

	pluginFilelist=os.listdir(os.path.dirname(os.path.realpath(__file__))+'/plugins')
	errors = []

	for pluginFile in pluginFilelist:
		if(pluginFile.endswith('.py') and pluginFile != "__init__.py"):
			pluginName='.'+pluginFile[:-3]

			try:
				plugin=importlib.import_module(pluginName,'recipemd_extract.plugins')
				recipe=plugin.extract(url,soup)
				if isinstance(recipe,Recipe):
					return recipe
			except Exception as e:
				if debug:
					raise e
				else:
					errors.append('In plugin "' + pluginName + '": Error parsing recipe: ' + str(e))
	return "\n".join(errors)

def writeRecipe(recipe, file=None):
	if file:
		filename = file.name
	else:
		joinedTitle = '_'.join(recipe.title.lower().split())
		filename = ''.join(c for c in joinedTitle if (c.isalnum() or c in '._')) + '.md'
		file = codecs.open(filename, 'w', encoding="utf-8")
	with file:
		file.write(RecipeSerializer().serialize(recipe))
	return filename


def main():
	parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
	parser.add_argument('url', help='URL of the recipe')
	parser.add_argument('file', help='the file to write to',nargs='?',default=None, type=argparse.FileType('w', encoding='UTF-8'))
	parser.add_argument('--debug',action='store_true', help='enables debug mode')
	args = parser.parse_args()
	url = args.url
	file = args.file

	recipe=extract(url,args.debug)

	if isinstance(recipe,Recipe):
		result = writeRecipe(recipe, file)
		print('Recipe written to ' + result)
	else:
		print(recipe, file=sys.stderr)
		print ('Could not extract recipe')


if __name__ == "__main__":
	main()
