import time
import json
import os
from typing import Dict, List, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import requests
from bs4 import BeautifulSoup

class WebAutomationController:
    """Advanced web automation controller with Selenium and BeautifulSoup integration"""
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.wait = None
        self.session = requests.Session()
        
    def initialize_driver(self):
        """Initialize Chrome WebDriver with optimized settings"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # Optimization arguments
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--silent')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Performance settings
        chrome_options.add_argument('--memory-pressure-off')
        chrome_options.add_argument('--max_old_space_size=4096')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
            self.wait = WebDriverWait(self.driver, self.timeout)
            return True
        except Exception as e:
            print(f"Failed to initialize WebDriver: {str(e)}")
            return False
    
    def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """Navigate to a specific URL"""
        try:
            if not self.driver:
                if not self.initialize_driver():
                    return {'success': False, 'error': 'Failed to initialize WebDriver'}
            
            self.driver.get(url)
            time.sleep(2)  # Allow page to load
            
            return {
                'success': True,
                'current_url': self.driver.current_url,
                'title': self.driver.title
            }
        except Exception as e:
            return {'success': False, 'error': f'Navigation failed: {str(e)}'}
    
    def fill_form(self, form_data: Dict[str, str], submit: bool = False) -> Dict[str, Any]:
        """Fill form fields with provided data"""
        try:
            filled_fields = []
            failed_fields = []
            
            for field_selector, value in form_data.items():
                try:
                    # Try multiple selector strategies
                    element = None
                    selectors_to_try = [
                        (By.NAME, field_selector),
                        (By.ID, field_selector),
                        (By.CSS_SELECTOR, field_selector),
                        (By.XPATH, f"//input[@placeholder='{field_selector}']"),
                        (By.XPATH, f"//input[@aria-label='{field_selector}']"),
                        (By.XPATH, f"//textarea[@name='{field_selector}']"),
                        (By.XPATH, f"//select[@name='{field_selector}']")
                    ]
                    
                    for by_type, selector in selectors_to_try:
                        try:
                            element = self.wait.until(EC.presence_of_element_located((by_type, selector)))
                            break
                        except:
                            continue
                    
                    if element:
                        # Clear existing text and enter new value
                        element.clear()
                        element.send_keys(value)
                        filled_fields.append(field_selector)
                    else:
                        failed_fields.append(field_selector)
                        
                except Exception as field_error:
                    failed_fields.append(f"{field_selector}: {str(field_error)}")
            
            # Submit form if requested
            if submit:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit'], button:contains('Submit')")
                    submit_button.click()
                    time.sleep(3)  # Wait for submission
                except:
                    # Try pressing Enter on the last filled field
                    if filled_fields:
                        last_element = self.driver.find_element(By.NAME, filled_fields[-1])
                        last_element.send_keys(Keys.RETURN)
            
            return {
                'success': len(filled_fields) > 0,
                'filled_fields': filled_fields,
                'failed_fields': failed_fields,
                'submitted': submit
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Form filling failed: {str(e)}'}
    
    def extract_data(self, selectors: List[str]) -> Dict[str, Any]:
        """Extract data using CSS selectors"""
        try:
            extracted_data = {}
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if elements:
                        # Extract text, attributes, or other data
                        element_data = []
                        for element in elements:
                            data = {
                                'text': element.text.strip(),
                                'tag': element.tag_name,
                                'attributes': {}
                            }
                            
                            # Get common attributes
                            for attr in ['href', 'src', 'alt', 'title', 'class', 'id']:
                                value = element.get_attribute(attr)
                                if value:
                                    data['attributes'][attr] = value
                            
                            element_data.append(data)
                        
                        extracted_data[selector] = element_data
                    else:
                        extracted_data[selector] = []
                        
                except Exception as selector_error:
                    extracted_data[selector] = {'error': str(selector_error)}
            
            return {
                'success': True,
                'data': extracted_data,
                'total_selectors': len(selectors),
                'successful_extractions': len([k for k, v in extracted_data.items() if not isinstance(v, dict) or 'error' not in v])
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Data extraction failed: {str(e)}'}
    
    def perform_click_sequence(self, click_selectors: List[str], wait_between: float = 1.0) -> Dict[str, Any]:
        """Perform a sequence of clicks"""
        try:
            successful_clicks = []
            failed_clicks = []
            
            for selector in click_selectors:
                try:
                    # Wait for element to be clickable
                    element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    
                    # Scroll element into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(0.5)
                    
                    # Click the element
                    element.click()
                    successful_clicks.append(selector)
                    
                    # Wait between clicks
                    time.sleep(wait_between)
                    
                except Exception as click_error:
                    failed_clicks.append(f"{selector}: {str(click_error)}")
            
            return {
                'success': len(successful_clicks) > 0,
                'successful_clicks': successful_clicks,
                'failed_clicks': failed_clicks,
                'total_attempted': len(click_selectors)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Click sequence failed: {str(e)}'}
    
    def upload_files(self, file_input_selector: str, file_paths: List[str]) -> Dict[str, Any]:
        """Upload files to a file input element"""
        try:
            # Find file input element
            file_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, file_input_selector)))
            
            uploaded_files = []
            failed_files = []
            
            for file_path in file_paths:
                try:
                    if os.path.exists(file_path):
                        file_input.send_keys(file_path)
                        uploaded_files.append(file_path)
                    else:
                        failed_files.append(f"{file_path}: File not found")
                except Exception as upload_error:
                    failed_files.append(f"{file_path}: {str(upload_error)}")
            
            return {
                'success': len(uploaded_files) > 0,
                'uploaded_files': uploaded_files,
                'failed_files': failed_files
            }
            
        except Exception as e:
            return {'success': False, 'error': f'File upload failed: {str(e)}'}
    
    def execute_javascript(self, script: str) -> Dict[str, Any]:
        """Execute custom JavaScript code"""
        try:
            result = self.driver.execute_script(script)
            return {
                'success': True,
                'result': result
            }
        except Exception as e:
            return {'success': False, 'error': f'JavaScript execution failed: {str(e)}'}
    
    def take_screenshot(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """Take a screenshot of the current page"""
        try:
            if not filename:
                filename = f"screenshot_{int(time.time())}.png"
            
            self.driver.save_screenshot(filename)
            return {
                'success': True,
                'filename': filename,
                'path': os.path.abspath(filename)
            }
        except Exception as e:
            return {'success': False, 'error': f'Screenshot failed: {str(e)}'}
    
    def get_page_source(self) -> str:
        """Get the current page source"""
        if self.driver:
            return self.driver.page_source
        return ""
    
    def get_current_url(self) -> str:
        """Get the current URL"""
        if self.driver:
            return self.driver.current_url
        return ""
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close()

# Task execution functions
def execute_form_fill_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute form filling task"""
    controller = WebAutomationController(headless=True)
    
    try:
        # Navigate to URL
        nav_result = controller.navigate_to_url(task_data['url'])
        if not nav_result['success']:
            return nav_result
        
        # Fill form
        form_data = task_data.get('form_data', {})
        result = controller.fill_form(form_data, submit=task_data.get('submit', False))
        
        return result
        
    finally:
        controller.close()

def execute_data_extraction_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute data extraction task"""
    controller = WebAutomationController(headless=True)
    
    try:
        # Navigate to URL
        nav_result = controller.navigate_to_url(task_data['url'])
        if not nav_result['success']:
            return nav_result
        
        # Extract data
        selectors = task_data.get('selectors', [])
        result = controller.extract_data(selectors)
        
        return result
        
    finally:
        controller.close()

def execute_click_automation_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute click automation task"""
    controller = WebAutomationController(headless=True)
    
    try:
        # Navigate to URL
        nav_result = controller.navigate_to_url(task_data['url'])
        if not nav_result['success']:
            return nav_result
        
        # Perform clicks
        click_sequence = task_data.get('click_sequence', [])
        result = controller.perform_click_sequence(click_sequence)
        
        return result
        
    finally:
        controller.close()

def execute_file_upload_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute file upload task"""
    controller = WebAutomationController(headless=True)
    
    try:
        # Navigate to URL
        nav_result = controller.navigate_to_url(task_data['url'])
        if not nav_result['success']:
            return nav_result
        
        # Upload files
        file_selector = task_data.get('file_selector', 'input[type="file"]')
        files = task_data.get('files', [])
        result = controller.upload_files(file_selector, files)
        
        return result
        
    finally:
        controller.close()