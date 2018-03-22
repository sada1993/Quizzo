#Base code forked from jakemor

# import libs
print("Loading libraries...")
import io, os, urllib, requests, re, webbrowser, json

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
from subprocess import call

# import Bsoup
from bs4 import BeautifulSoup
print("Done")

class colors:
    blue = '\033[94m'
    red   = "\033[1;31m"
    green = '\033[0;32m'
    end = '\033[0m'
    bold = '\033[1m'


def get_screenshot(img_name):

	""" 
		Grabs a screenshot of the question. To mirror your iphone on your computer open quicktime and initiate a screen recording on your mac
	"""

	print("grabbing screenshot...")
	call(["screencapture","-R", "430,167,400,370", img_name]) # live
	call(["sips","-Z","350", img_name])

def run_ocr(img_name):
	
	"""
		Runs OCR on the grabbed screenshot

	"""

	print("running OCR...")
	client = vision.ImageAnnotatorClient()

	file_name = os.path.join( os.path.dirname(__file__), img_name)

	with io.open(file_name, 'rb') as image_file:
	    content = image_file.read()

	image = types.Image(content=content)

	response = client.text_detection(image=image)
	texts = response.text_annotations

	all_text = texts[0].description.strip()

	lines = all_text.split("\n")

	ans_1 = lines[-3].lower().encode('utf-8')
	ans_2 = lines[-2].lower().encode('utf-8')
	ans_3 = lines[-1].lower().encode('utf-8')

	del lines[-1]
	del lines[-1]
	del lines[-1]

	question = u" ".join([line.strip() for line in lines]).encode('utf-8')

	reverse = True

	return { 
		"question": question.decode("utf-8"),
		"ans_1": ans_1.decode("utf-8"),
		"ans_2": ans_2.decode("utf-8"),
		"ans_3": ans_3.decode("utf-8"),
	}

def google(q_list, num):

	"""
		given a list of queries, this function Google's them as a concatenated string.
		input: q_list - question
		num: number of webpages to consider when googling results
		
	"""

	params = {"q":" ".join(q_list), "num":num}
	url_params = urllib.parse.urlencode(params)
	google_url = "https://www.google.com/search?" + url_params
	r = requests.get(google_url)

	soup = BeautifulSoup(r.text)
	spans = soup.find_all('span', {'class' : 'st'})

	text = u" ".join([span.get_text() for span in spans]).lower().encode('utf-8').strip()

	return text.decode("utf-8")

def rank_answers(question_block):

	"""
		Ranks answers based on how many times they show up in google's top 50 results. 
		
		If the word " not " is in the question is reverses them. 
		If theres a tie breaker it google the questions with the answers

	"""


	print("rankings answers...")
	
	question = question_block["question"]
	ans_1 = question_block["ans_1"]
	ans_2 = question_block["ans_2"]
	ans_3 = question_block["ans_3"]

	print("Question = ",question)

	reverse = True

	if question.lower().find(" not ") != -1:
		print("reversing results...")
		reverse = False

	text = google([question], 50)

	results = []

	results.append({"ans": ans_1, "count": text.count(ans_1)})
	results.append({"ans": ans_2, "count": text.count(ans_2)})
	results.append({"ans": ans_3, "count": text.count(ans_3)})

	sorted_results = []

	sorted_results.append({"ans": ans_1, "count": text.count(ans_1)})
	sorted_results.append({"ans": ans_2, "count": text.count(ans_2)})
	sorted_results.append({"ans": ans_3, "count": text.count(ans_3)})

	sorted_results.sort(key=lambda x: x["count"], reverse=reverse)

	# if there's a tie redo with answers in q

	if (sorted_results[0]["count"] == sorted_results[1]["count"]):
		# build url, get html
		print("running tiebreaker...")

		text = google([question, ans_1, ans_2, ans_3], 50)

		results = []

		results.append({"ans": ans_1, "count": text.count(ans_1)})
		results.append({"ans": ans_2, "count": text.count(ans_2)})
		results.append({"ans": ans_3, "count": text.count(ans_3)})

	return results

def print_question_block(question_block):

	""" 
		Prints the q to the terminal

	"""


	print("\n")
	print("Q: ", question_block["question"])
	print("1: ", question_block["ans_1"])
	print("2: ", question_block["ans_2"])
	print("3: ", question_block["ans_3"])
	print("\n")

	

def save_question_block(question_block):

	""" 
		saves the q to a file

	"""

	question = question_block["question"].replace(",", "").replace("\"", "").replace("\'", "")
	ans_1 = question_block["ans_1"].replace(",", "").replace("\"", "").replace("\'", "")
	ans_2 = question_block["ans_2"].replace(",", "").replace("\"", "").replace("\'", "")
	ans_3 = question_block["ans_3"].replace(",", "").replace("\"", "").replace("\'", "")

	with open('questions.csv', 'a') as file:
		file.write("\t".join([question,ans_1,ans_2,ans_3 + "\n"]))
		file.close()

def print_results(results):

	""" 
		Prints the results

	"""

	print("\n")

	small = min(results, key= lambda x: x["count"])
	large = max(results, key= lambda x: x["count"])

	for (i,r) in enumerate(results):
		text = "%s - %s" % (r["ans"], r["count"])

		

		if r["ans"] == large["ans"]:
			print(colors.green + text + colors.end)
		elif r["ans"] == small["ans"]:
			print(colors.red + text + colors.end)
		else:
			print(text)

	print("\n")

def execute_program():
	get_screenshot("q.png")
	question_block = run_ocr("q.png")
	print_question_block(question_block)
	#save_question_block(question_block)
	results = rank_answers(question_block)
	print_results(results)	
	print("-----------------")

def main():

	print("Starting Program!")
	print("Type n for new computation.\n Type q to quit the program \n")
	while True:
		user_input = input("Enter input: ")
		if user_input == "n":
			execute_program()
		else:
			print("Quitting program")
			break
		


if __name__ == "__main__":
    
    main()

