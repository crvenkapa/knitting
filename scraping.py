#!/usr/bin/python
import requests
import bs4
import pdb
import csv
import os
import re

from config import user_name, passwrd

def login_ravelry(user_name, passwrd):
	# Takes user name and password and returns session.
	
	s = requests.Session()

	login_info = {'user[login]': user_name, 'user[password]': passwrd}
	url = 'https://www.ravelry.com/account/login'

	s.post(url, data = login_info)
	
	return s
	
def get_patterns_list(s):
	# session = s

	patterns = s.get('http://www.ravelry.com/patterns/knitting/popular')

	soup = bs4.BeautifulSoup(patterns.text)

	categories_div = soup.find('div', {'class':'categories grid_3'})

	sub_categories = categories_div('ul')[0]('ul')

	categories = []

	for cat in sub_categories:
		categories.extend([(link.find('a').get('href'), link.find('a').text) 
			for link in cat('li')])
		
		
		
	for ad, cat_name in categories:
		with open('data/' + ad.replace('/patterns/knitting/popular/', '') + '.csv', 'w') as fh:
			csvwriter = csv.writer(fh)
			csvwriter.writerow(['name', 'url'])
			for p in range(1,6):
				url = "http://www.ravelry.com{0}?page={1}".format(ad, p)
				#pdb.set_trace()
				cat_page = s.get(url)
				if cat_page.status_code == 200:
					soup_cat = bs4.BeautifulSoup(cat_page.text)
					patterns = soup_cat.find_all('div', {'class':'pattern_name'})
					for pat in patterns:
						csvwriter.writerow([pat.find('a').text.encode('UTF-8'), 
							pat.find('a').get('href')])

def get_projects_queues(soup):
	L = soup.find('div', {'class':'pattern_people summary_box_people'})
	m = re.findall("([0-9]+) pro", L.find('a').text)
	n_projects = m[0] if m else '0'
	m = re.findall("in (.*) queue", L.text)
	n_queues = m[0] if m else '0';
	return (n_projects, n_queues)

def get_ratings(soup, s):
	premagic = soup.find('div', {'class':'pattern_summary'}).find('div', {'class':'average'})
	if premagic == None:
		return ([0]*5, [0]*10)
	premagic = premagic.find('a').get('onclick')
	magic = re.findall("\((.*)\)", premagic)[0]
	stats = s.get('http://www.ravelry.com/patterns/library/' + magic + '/statistics')
	soup_stats = bs4.BeautifulSoup(stats.text)
	L = soup_stats.find_all('td')[2::3]
	L = [r.text.lstrip().replace(' user', '').rstrip('s\n') for r in L]
	stars = []
	for i in range(5):
		if L[i] == '':
			stars.append(0)
		else:
			stars.append(int(L[i]))
	difficulty = []
	for i in range(5,15):
		if L[i] == '':
			difficulty.append(0)
		else:
			difficulty.append(int(L[i]))
	return (stars, difficulty)
	


def scraping(s):
	files = os.listdir('data')
	for f in files:
		with open(os.path.join('data',f), 'r') as fh:
			with open(os.path.join('data',os.path.splitext(f)[0]+'_stats.csv'), 'w') as fh2:
				csvreader = csv.DictReader(fh)
				csvwriter = csv.writer(fh2)
				csvwriter.writerow(['name', 'url', 'number of projects', 'number of queues', 
					'star rating from one to five', 'difficulty rating from one to ten'])
				for d in csvreader:
					project = s.get(d['url'])
					soup_project = bs4.BeautifulSoup(project.text)
					c = get_projects_queues(soup_project)
					e = get_ratings(soup_project, s)
					csvwriter.writerow([d['name'], d['url'], c[0], c[1],
						';'.join(map(str, e[0])), ';'.join(map(str, e[1]))])
							

if __name__ == "__main__":
	s = login_ravelry(user_name, passwrd)
	get_patterns_list(s)	
	scraping(s)				
				
	
	
	
