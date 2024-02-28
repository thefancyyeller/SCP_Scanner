import requests
from bs4 import BeautifulSoup
import re
import webbrowser
import os

class SessionData:
    def __init__(self):
        self.current_scp = -1
        self.min_upvotes = -1

# Returns the URL for a given SCP
def get_scp_url(scp_number: int):
    base_url = 'https://scp-wiki.wikidot.com/scp-'
    num_string = str(scp_number)
    while(len(num_string) < 3):
        num_string = "0"+num_string
    return base_url + num_string

def get_scp_ratings(scp_num):
    url = get_scp_url(scp_num)
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        
        # Extract the rating
        soup = BeautifulSoup(response.content, 'html.parser')
        rating_element = soup.find('span', class_='rate-points')
        if rating_element:
            rating_string = rating_element.text.strip()
            regex = r'\d+$'
            result = re.search(regex, rating_string)
            if(not result):
                print(f"Error: could not find digits in the string " + rating_string)
                return None
            return int(result.group())
        else:
            return None

    except requests.RequestException as e:
        print(f"An error occurred, {e.strerror}")
        return None

def scp_interactive():
    print("Welcome to the SCP Scanner! Follow the prompts to begin filtering and reading SCP entries (A feature not offered by the website)")
    old_data = os.path.exists("./save_data.txt")
    user_session_data = None # Holds the current session data

    # Attempt to read previous session data
    if(old_data):
        print("Opening saved data from previous session")
        save_file = open("./save_data.txt", "r")
        try:
            # Read the last sessions SCP
            current_session = SessionData()
            for line in save_file:
                line = line.strip()
                line_text = line.split(' ')
                if(len(line_text) != 2):
                    raise("Error! Invalid number of items in save file")
                label = line_text[0]
                if(label == "last_scp"):
                    current_session.current_scp = int(line_text[1])
                elif(label == "min_upvotes"):
                    current_session.min_upvotes = int(line_text[1])
                else:
                    raise(f"Error! Unexpected entry {line}")
            user_session_data = current_session
            save_file.close()
        except Exception as e:
            print("Failed to read session data. ", e)
            save_file.close()
            input("Press enter to overwrite the existing save file.\t")
    
    # Make a new session if one was not found
    if(user_session_data == None):
        print("Creating a new session!")
        user_session_data = SessionData()
        # Get the starting SCP number
        while True:
            resp = input("What scp number would you like to start with?\t")
            try:
                user_session_data.current_scp = int(resp) - 1 # This is because we start 1 in front of the current SCP
                break
            except ValueError:
                print(f"Invalid scp number {resp}")
        # Get the minimum upvotes
        while True:
            resp = input("What is the minimum amount of upvotes you prefer?\t")
            try:
                user_session_data.min_upvotes = int(resp)
                break
            except ValueError:
                print(f"Invalid number {resp}")
    
    print(f"Starting session. Starting at SCP {user_session_data.current_scp + 1}, Minimum upvotes = {user_session_data.min_upvotes}")

    # Now that we have valid parameters, begin the main program...
    while True:
        user_session_data.current_scp += 1 # Get the current SCP number
        if(user_session_data.current_scp == 1):
            input("WARNING! There is no SCP #1. Press any key to continue to SCP #2...\t")
            continue
        print(f"Scanning SCP #{user_session_data.current_scp}")
        rating = get_scp_ratings(user_session_data.current_scp)
        # Handle if we didnt get anything
        if(rating == None):
            resp = input(f"Failed to get rating of SCP #{user_session_data.current_scp} ({get_scp_url(user_session_data.current_scp)}). Press enter to retry or ctrl + C to stop program. ")
            user_session_data.current_scp -= 1
            continue
        # Handle too low of a rating
        if(rating < user_session_data.min_upvotes):
            print(f"\tSkipping... (Upvotes found: {rating} Required Minumum: {user_session_data.min_upvotes})")
            continue
        # Handle finding suitable SCP
        print(f"Found SCP #{user_session_data.current_scp} ({rating} upvotes). Press enter open in browser")
        input()
        update_save_file(user_session_data)
        webbrowser.open_new_tab(get_scp_url(user_session_data.current_scp))



def update_save_file(data: SessionData):
    save_file = open("./save_data.txt", 'w')
    save_file.write(f"last_scp {data.current_scp}\nmin_upvotes {data.min_upvotes}")
    save_file.close()

# This line is what kicks the whole thing off
scp_interactive()