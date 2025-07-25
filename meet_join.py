from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time
from record import AudioRecorder
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

class JoinGoogleMeet:
    def __init__(self):
        self.mail_address = os.getenv('EMAIL_ID')
        self.password = os.getenv('EMAIL_PASSWORD')
        
        # Updated Chrome options
        opt = Options()
        opt.add_argument('--disable-blink-features=AutomationControlled')
        opt.add_argument('--start-maximized')
        opt.add_argument('--use-fake-ui-for-media-stream')  # Auto-allow mic/camera
        opt.add_experimental_option("excludeSwitches", ["enable-automation"])
        opt.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        })
        
        self.driver = webdriver.Chrome(options=opt)
        self.wait = WebDriverWait(self.driver, 20)

    def safe_click(self, by, selector, max_retries=3):
        """Clicks an element even if obscured by another element"""
        for _ in range(max_retries):
            try:
                element = self.wait.until(EC.element_to_be_clickable((by, selector)))
                
                # Method 1: Scroll into view first
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                
                # Method 2: Use ActionChains to move to element
                ActionChains(self.driver).move_to_element(element).pause(0.5).click().perform()
                
                # Verify click succeeded
                time.sleep(0.5)
                return True
                
            except Exception as e:
                print(f"Click failed (attempt {_+1}): {str(e)}")
                time.sleep(1)
        return False

    def handle_name_prompt(self, name="Rochisnu"):
        """More robust name input handling with multiple fallbacks"""
        name_selectors = [
            "input[aria-label='Your name']",  # Primary selector
            "input[placeholder='Your name']",  # Fallback 1
            "input[type='text'][name='name']"  # Fallback 2
        ]
        
        for selector in name_selectors:
            try:
                name_field = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                
                name_field.clear()
                name_field.send_keys(name)
                
                # Verify name was entered
                if name_field.get_attribute('value') == name:
                    print(f"Entered name: {name}")
                    return True
                    
            except Exception:
                continue
        
        print("Could not find name input field after multiple attempts")
        return False    

    def Glogin(self):
        try:
            self.driver.get('https://accounts.google.com')
            # Improved login flow
            self.wait.until(EC.element_to_be_clickable((By.ID, "identifierId"))).send_keys(self.mail_address)
            self.driver.find_element(By.ID, "identifierNext").click()
            
            # More reliable password entry
            password_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "Passwd"))
            )
            password_field.send_keys(self.password)
            self.driver.find_element(By.ID, "passwordNext").click()
            
            print("Gmail login successful")
        except Exception as e:
            print(f"Login failed: {str(e)}")
            raise

    def join_meeting(self, meet_link, audio_path, duration):
        try:
            self.driver.get(meet_link)
            
            if not self.handle_name_prompt():
                print("Proceeding without name entry")
            # Handle "Ask to join" vs "Join now" flow
            # join_now_xpath = "//span[contains(text(),'Join now') or contains(text(),'Ask to join')]"
            # join_button = self.wait.until(
            #     EC.element_to_be_clickable((By.XPATH, join_now_xpath))
            #)
            join_xpath = '//span[text()="Join now" or text()="Ask to join"]/ancestor::button'
            self.safe_click(By.XPATH, join_xpath)
            
            # Turn off mic/camera before joining
            self.toggle_media("microphone")
            self.toggle_media("camera")
            
            #join_button.click()
            print("Successfully joined meeting")

            AudioRecorder().get_audio(audio_path, duration)
            print("Recording completed...")
            
            
        except Exception as e:
            print(f"Meeting join failed: {str(e)}")
            raise

    def toggle_media(self, device_type):
        """Toggle microphone or camera with robust element finding"""
        try:
            # Updated CSS selector that works for both mic and camera
            selector = f'button[aria-label*="Turn off {device_type}"], button[aria-label*="Turn on {device_type}"]'
            button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            button.click()
            print(f"Toggled {device_type} successfully")
            time.sleep(1)  # Small delay for state change
        except Exception as e:
            print(f"Could not toggle {device_type}: {str(e)}")

def main():
    try:
        temp_dir = os.getcwd()
        audio_path = os.path.join(temp_dir, "output.wav")
        meet_link = os.getenv('MEET_LINK')
        duration=int(os.getenv('RECORDING_DURATION'))
        if not meet_link:
            raise ValueError("MEET_LINK environment variable not set")
            
        bot = JoinGoogleMeet()
        bot.Glogin()
        bot.join_meeting(meet_link,audio_path,duration)
        
        # Keep the meeting running
        input("Press Enter to exit...")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'bot' in locals():
            bot.driver.quit()

if __name__ == '__main__':
    main()