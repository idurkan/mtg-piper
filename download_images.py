import datetime
import json
import os
import pprint
import requests
import shutil
import string
import sys
import unicodedata

def getCardJsonObject(cards_json_path):
	file_content = open(cards_json_path, 'r').read()
	cards_json = json.loads(file_content)
	return cards_json

def fetch_image(image_url, output_filename):
	response = requests.get(image_url)

	if response.status_code == 200:
		with open(output_filename, 'wb') as outfile:
			for chunk in response.iter_content(1024):
				outfile.write(chunk)

	print('Wrote ' + output_filename + '.')

def make_dir(dir_path):
	if not os.path.exists(dir_path):
		os.makedirs(dir_path)

def get_time_now():
	return datetime.datetime.now().replace(microsecond=0)

def format_card_path(output_dir_path, card):
	return "{0}/{1}_{2}.jpg".format(output_dir_path, card['id'], sanitize_name(card['name']))

# get rid of slashes in card names, etc by whitelisting.
valid_chars = "-_. {0}{1}".format(string.ascii_letters, string.digits)
def sanitize_name(card_name):
	normalized_name = unicodedata.normalize('NFKD', card_name).encode('ascii', 'ignore')
	return "".join(c for c in normalized_name if c in valid_chars)

def main(args):
	if len(args) != 2:
		print("Two arguments please - specify the path of the cards info json file you want images for followed by the output directory path.");
		exit(1)

	input_path = args[0]
	output_dir = args[1]

	# load up JSON from the cards.json file
	all_cards_objects = getCardJsonObject(input_path)
	cards = sorted(list(all_cards_objects.itervalues()), key=(lambda card: card['id']))

	start_time = get_time_now()

	print('Started download at: ' + str(start_time))

	make_dir(output_dir)
	for card in cards:
		fetch_image(card['image_url'], format_card_path(output_dir, card))

	end_time = get_time_now()

	print('Finished download at: ' + str(end_time))
	print('Elapsed time: ' + str(end_time - start_time))

if __name__ == "__main__":
	args = sys.argv[1:]
	main(args)