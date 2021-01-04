from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import PySimpleGUI as sg
import threading
import os

# initial data
# chrome browser driver
browser = webdriver.Chrome(ChromeDriverManager().install())
# scroll indicator
scroll = True
SCROLL_PAUSE_TIME = 2  # depends on your internet speed
# Public Strings
csv_file_data = ""
view_data = ""
hashtag = ""
# Regex
url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
phone_regex = "[(][\d]{3}[)][ ]?[\d]{3}-[\d]{4}"
email_regex = r'[\w\.-]+@[\w\.-]+'

# drawing the layout
file_list_column = [
    [
        sg.Text("Instagram Hashtag"),
        sg.In(size=(25, 1), key="-Hashtag-", default_text="travel"),
        sg.Button("Search", button_color=("white", "blue"), size=(6, 1)),
        sg.Button("Stop Scrolling", button_color=("white", "red"), size=(15, 1)),
        sg.Button("Export to CSV file", button_color=("white", "green"), size=(15, 1)),

    ],
    [
        sg.Multiline(disabled=True,
                     size=(30, 30), key="-Logs LIST-"
                     ),
        sg.Multiline(disabled=True,
                     size=(30, 30), key="-Data LIST-"
                     ),
    ],
]

# ----- Full layout -----
layout = [
    [
        sg.Column(file_list_column),

    ]
]
window = sg.Window("Instagram Hashtag Search", layout)


def main():
    while True:
        event, values = window.read()
        if event in (None, 'Exit'):
            break
        if event == 'Search':
            global hashtag
            hashtag = values["-Hashtag-"]
            clear_data()
            try:
                print('Starting thread to do long work...')
                threading.Thread(target=do_your_job, args=(hashtag,), daemon=True).start()
            except Exception as e:
                print(
                    'Error starting work thread.')

        elif event == 'Stop Scrolling':
            global scroll
            scroll = False

        elif event == 'Export to CSV file':
            threading.Thread(target=save_to_csv_file, args=(csv_file_data,), daemon=False).start()

        if event == "Exit" or event == sg.WIN_CLOSED:
            break


def do_your_job(hashtag):
    posts = []
    emails = []
    urls = []
    phone_numbers = []
    bio = ""
    browser.get('https://www.instagram.com/explore/tags/' + hashtag)

    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")

    while scroll:
        # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height or scroll == False:
            break
        last_height = new_height

    links = browser.find_elements_by_tag_name("a")
    for link in links:
        post = link.get_attribute("href")
        if '/p/' in post:
            posts.append(post)

    print(posts)
    update_log_view("Total posts found : " + str(+len(posts)))
    browser.stop_client()
    for post in posts:
        browser.get(post)
        profile_url = browser.find_element_by_tag_name("a").get_attribute("href")
        update_log_view("Now loading data for :" + profile_url)
        browser.stop_client()
        browser.get(profile_url)
        try:
            bio = browser.find_element_by_class_name("-vDIg").text
        except:
            print("An exception occurred")

        process_data(bio, urls, emails, phone_numbers, profile_url)


def process_data(bio, urls, emails, phone_numbers, profile_url):
    single_csv_record = profile_url
    display_user_data = "User: " + profile_url + "\n"
    print(bio)
    url_match = re.findall(url_regex, bio)
    if url_match:
        while '"' in urls:
            urls.remove("")
        display_user_data += "Urls in Bio : " + str(url_match)
        single_csv_record += "," + str(url_match)
        urls.append(url_match)

    phone_match = re.findall(phone_regex, bio)
    if phone_match:
        display_user_data += "Phone Numbers in Bio : " + str(phone_match)
        single_csv_record += "," + str(phone_match)
        phone_numbers.append(phone_match)

    email_match = re.findall(email_regex, bio)
    if email_match:
        display_user_data += "Emails in Bio : " + str(phone_match)
        single_csv_record += "," + str(email_match) + "\n"
        emails.append(email_match)

    update_log_view(display_user_data)
    if single_csv_record is not profile_url:
        global csv_file_data
        csv_file_data += single_csv_record + "\n"
        update_all_data_view("Data found :" + single_csv_record + "\n")


def update_log_view(new_data):
    window['-Logs LIST-'].update(new_data)


def update_all_data_view(appendData):
    global view_data
    view_data += appendData + "\n"
    window['-Data LIST-'].update(view_data)


def save_to_csv_file(data):
    username = os.getlogin()  # Fetch username
    file = open(f'C:\\Users\\{username}\\Desktop\\Instagram users #{hashtag} .csv', 'w', encoding="utf-8")
    file.write(data)
    file.close()


def clear_data():
    global csv_file_data
    csv_file_data = ""
    global view_data
    view_data = ""
    global scroll
    scroll = True


if __name__ == "__main__":
    main()
