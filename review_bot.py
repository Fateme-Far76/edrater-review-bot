import os
import csv
import time
import json
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

# ========== Configuration ==========
USERNAME = "fati_squib@yahoo.com"
PASSWORD = "Iwillnotlose@2025"
REVIEW_LOG = "reviewed_schools.json"
LOCAL_AI_API_URL = "http://localhost:11434/api/generate"
FALLBACK_COMMENT_FILE = "Fallback_Comments.csv"
PROMPT = "Write a 150 to 250 character positive school review focused on equity and teaching quality."



# ========== AI-Based Comment Generation ==========
def generate_comment(prompt):
    """
    Sends a text prompt to Ollama and retrieves a generated comment.

    Parameters:
        prompt (str): The input text to send to the language model.

    Returns:
        str: The generated response text from the model, or an empty string if no response.
    """
    response = requests.post(
        LOCAL_AI_API_URL,
        json={
            "model": "mistral",                 # The name of the local model being queried
            "prompt": prompt,
            "stream": False,                    # Disable streaming to get full response at once
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 50,
                "max_tokens": 100,
                "stop": ["\n\n"]                # Stops generation when double newline is hit
            }
        }
    )
    result = response.json()
    return result.get("response", "").strip()   # Fallback to empty string if 'response' is missing


# ========== Review Content Generation ==========
def fallback_comments(filename=FALLBACK_COMMENT_FILE):
    """
    Loads fallback comments from a CSV file.

    Parameters:
        filename (str): Name of the CSV file containing fallback comments.

    Returns:
        List[str]: A list of non-empty, stripped comment strings from the file.
    """   
    file_path = os.path.join(os.path.dirname(__file__), filename) 
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        comments = [row[0].strip() for row in reader if row and row[0].strip()]
        return comments

def generate_review():
    """
    Generates a school review with random star ratings and a comment.
    It first tries to generate the comment using the local AI model.
    If that fails, it falls back to a predefined CSV of comments.

    Returns:
        dict: A dictionary containing:
            - academics (int): rating 3-5
            - administrator (int): rating 3-5
            - equity (int): rating 3-5
            - teacher (int): rating 3-5
            - comment (str): AI-generated or fallback comment
            - date (str): ISO-formatted timestamp
    """    
    try:
        comment = generate_comment(PROMPT)
    except Exception as e:
        FALLBACK_COMMENTS = fallback_comments()
        comment = random.choice(FALLBACK_COMMENTS)  # fallback to predefined comments
    return {
        "academics": random.randint(1, 3),
        "administrator": random.randint(1, 3),
        "equity": random.randint(1, 3),
        "teacher": random.randint(1, 3),
        "comment": comment,
        "date": datetime.now().isoformat()
    }
    
    
# ========== JSON Log Handling ==========
def load_log():
    """
    Loads the review log from the JSON file.

    Returns:
        dict: A dictionary of previously reviewed schools and their review data.
    """    
    try:
        with open(REVIEW_LOG, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_log(log):
    """
    Saves the review log to a JSON file after transforming the rating scale.

    The original rating scale used in generation is:
        1 = highest score, 3 = lowest score
    This function converts the ratings to:
        5 = highest score, 4 = middle, 3 = lowest

    Args:
        log (dict): A dictionary where keys are school URLs and values are review dictionaries.
    """
    def convert_rating(rating):
        # Maps 1 → 5, 2 → 4, 3 → 3
        return 6 - rating

    transformed_log = {}
    for url, review in log.items():
        transformed_review = review.copy()
        for key in ["academics", "administrator", "equity", "teacher"]:
            transformed_review[key] = convert_rating(review[key])
        transformed_log[url] = transformed_review
        
    # Write the transformed log to disk as JSON
    with open(REVIEW_LOG, "w") as f:
        json.dump(transformed_log, f, indent=2)

                
# ========== Automated Login ==========        
def login(driver):
    """
    Automates the login process for edrater.com.

    Raises:
        Exception: If cookie banner not found or login fails. also logs screenshot of the failure.
    """
    driver.get("https://edrater.com")
    wait = WebDriverWait(driver, 30)

    # Accept cookies
    try:
        time.sleep(3)
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if "Consent" in btn.text:
                driver.execute_script("arguments[0].click();", btn)
                break
    except Exception as e:
        print("Cookie banner may not have been found or dismissed:", e)

    # Open login modal
    login_icon = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="site-navigation"]/div/div/div/div[2]/div[2]/a')
    ))
    login_icon.click()
    time.sleep(2)

    # Fill in login form
    try:
        username_field = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#listar-login-form > div:nth-child(1) > input")
        ))
        password_field = driver.find_element(By.CSS_SELECTOR, "#listar_user_pass")
        login_button = driver.find_element(By.CSS_SELECTOR, "#listar-login-form > div:nth-child(4) > button")

        username_field.clear()
        username_field.send_keys(USERNAME)

        password_field.clear()
        password_field.send_keys(PASSWORD)

        driver.execute_script("arguments[0].click();", login_button)
        time.sleep(3)

    except Exception as e:
        driver.save_screenshot("login_failed.png")
        print("Login failed:", e)
        raise


# ========== Review Submission ==========
def submit_review(driver, review, school_url):
    """
    Submits a school review on the edrater.com listing page.

    Args:
        driver (WebDriver): The active Selenium driver instance.
        review (dict): Dictionary containing review fields and ratings.

    Raises:
        Exception: If any step fails, it logs screenshots and HTML dumps for debugging.
    """
    driver.get(school_url)
    if driver.execute_script("return document.getElementById('wpadminbar') !== null;"):
        driver.execute_script("document.getElementById('wpadminbar').style.display = 'none';")
    time.sleep(3)

    try:
        # Scroll to bottom to trigger the "Write a Review" button rendering
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Click "Write a Review"
        review_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.listar-write-review-button-wrapper a"))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", review_button)
        review_button.click()
        time.sleep(3)

        # === Fill in Star Ratings ===
        categories = ["academics", "administrator", "equity", "teacher"]
        star_groups = driver.find_elements(By.CSS_SELECTOR, "#listar-submit-ratings > div > div")

        for i, category in enumerate(categories):
            # Try multiple selectors
            stars = (
                star_groups[i].find_elements(By.CSS_SELECTOR, "i.fa.fa-star") or
                star_groups[i].find_elements(By.CSS_SELECTOR, "span.star") or
                star_groups[i].find_elements(By.TAG_NAME, "i")
            )

            if stars:
                driver.execute_script("arguments[0].click();", stars[review[category] - 1])


        # === Fill in Comment ===
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "comment"))
            )

            comment_textareas = driver.find_elements(By.ID, "comment")

            success = False
            for idx, textarea in enumerate(comment_textareas):
                try:
                    driver.execute_script("arguments[0].value = arguments[1];", textarea, review["comment"])
                    success = True
                    break
                except Exception as js_e:
                    print(f"JS fallback also failed on textarea #{idx+1}")

            if not success:
                raise Exception("All attempts to fill the comment box failed.")

        except Exception as e:
            raise Exception("Failed to locate or fill the comment box") from e


        # === Submit the Review ===
        try:
            submit_btn = driver.find_element(By.CSS_SELECTOR, "#commentform > p.form-submit input[type='submit']")
            driver.execute_script("arguments[0].click();", submit_btn)
            time.sleep(2)
        except Exception as e:
            raise Exception("Failed to submit review properly") from e

    except Exception as e:
        raise e

# ========== Batch Execution ==========
def run_for_urls(url_list):
    """
    Processes a batch of school listing URLs for review submission.

    Workflow:
    - Loads previously reviewed schools from JSON log.
    - Launches Chrome.
    - Iterates through each URL in the list:
        • Skips if already reviewed.
        • Logs in to edrater.com.
        • Generates review using AI or fallback.
        • Submits the review.
        • Logs the review in local file to avoid duplication.

    Args:
        url_list (list): List of school listing URLs to process.
    """
    reviewed = load_log()
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    
    try:
        login(driver)
        
        for url in url_list:
            if url in reviewed:
                print(f"Already reviewed: {url}")
                continue
            
            try:
                review = generate_review()
                submit_review(driver, review, school_url=url)
                reviewed[url] = review
                save_log(reviewed)
            except Exception as e:
                print(f"Error for {url}: {e}")
    finally:
        driver.quit()
        print("All done")


# ========== Main Execution ==========
if __name__ == "__main__":
    run_for_urls(["https://edrater.com/listing/whitman-college/"])

