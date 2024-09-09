# Package
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time


# Main
def main():
	# Path to your ChromeDriver
	chrome_driver_path = '/Users/anthony_ning/Downloads/chromedriver_mac_arm64/chromedriver'

	# Set up Chrome options
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.179 Safari/537.36")
	chrome_options.add_argument('--headless')  # Run in headless mode (without a GUI)
	chrome_options.add_argument('--disable-gpu')
	chrome_options.add_argument('--window-size=1920x1080')
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--disable-dev-shm-usage')

	# Create a new Chrome session
	service = Service(chrome_driver_path)
	driver = webdriver.Chrome(service=service, options=chrome_options)

	try:
		# Navigate to the webpage that requires CAPTCHA solving
		url = 'https://tradingeconomics.com/calendar'
		driver.get(url)

		# # Scroll down to load more events (this step is optional, depending on the page structure)
		# # Get the initial scroll height
		# last_height = driver.execute_script("return document.body.scrollHeight")
		#
		# while True:
		# 	# Scroll down to the bottom of the page
		# 	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		#
		# 	# Wait for new content to load
		# 	time.sleep(15)
		#
		# 	# Get the new scroll height after loading
		# 	new_height = driver.execute_script("return document.body.scrollHeight")
		#
		# 	# Check if the scroll height has changed (i.e., new content has been loaded)
		# 	if new_height == last_height:
		# 		# If the scroll height hasn't changed, break the loop
		# 		break
		#
		# 	# Update the last height to the new height
		# 	last_height = new_height

		# Get the source from the website
		page_source = driver.page_source

		# Use Beautiful Soup to find all headers and content/info
		soup = BeautifulSoup(page_source, 'html.parser')
		items = soup.find_all(['thead', 'tbody'])

		# Countries collected
		countries = ['united states', 'euro area', 'germany', 'united kingdom', 'india', 'china', 'japan']

		# Web-scrape data
		data = []
		switch = True

		for item in items[1:]:

			# Header
			if item.find_all('th') and switch:
				headers = item.find_all('th')
				i = 0
				for header in headers:
					header = header.text.strip()
					if header != '' and i == 0:
						data.append(header)
						data.append('Country')
						data.append('Event')
						i = 1
					elif header != '' and i != 0:
						data.append(header)
					else:
						continue
				switch = False

			# Ignore the hidden header
			elif item.find_all('th') and not switch:
				switch = True
				continue

			# Content/Info
			else:
				if item.find_all('tr', {'data-country': countries}):
					sub_items = item.find_all('tr', {'data-country': countries})

					for sub_item in sub_items:

						# Time
						if sub_item.find('td').span.text.strip() != '':
							time_ = sub_item.find('td').span.text.strip()
						else:
							time_ = 'NA'
						data.append(time_)

						# Country
						country_item = sub_item.find(class_='calendar-item').find_all('td')[1].text.strip()
						data.append(country_item)

						# Event
						if sub_item.find(class_='calendar-event'):
							event = sub_item.find(class_='calendar-event').text.strip()
						elif sub_item.find_all('td')[4].span.text.strip() != '':
							event = sub_item.find_all('td')[4].span.text.strip()
						else:
							event = 'NA'
						data.append(event)

						# Event Info (Numbers)
						numbers = sub_item.find_all(
							class_=['calendar-item calendar-item-positive', 'calendar-item calendar-item-negative'])
						for number in numbers:
							# Is available to span
							if number.span:
								if number.span.text.strip() != '':
									info = number.span.text.strip()
								else:
									info = 'NA'
							# Is not available to span
							else:
								if number.text.strip() != '':
									info = number.text.strip()
								else:
									info = 'NA'
							data.append(info)

	finally:
		# Clean up and close the browser session
		driver.quit()
		out_file(data, 'Econ_DailyData.csv')


# Writing data to csv file
def out_file(data_import, filename):
	print('\n===============================================')
	print(f'Writing predictions to --> {filename}')
	with open(filename, 'w') as f:
		for i in range(len(data_import)):
			if (i+1) % 7 != 0:
				f.write(data_import[i]+',')
			else:
				f.write(data_import[i]+'\n')
	print('===============================================')


if __name__ == '__main__':
	main()
