# random_street_view.py

import time
import sys
import string
import random
import json
import numpy as np
import pandas as pd

# import chromedriver_autoinstaller

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from io import BytesIO
from PIL import Image
from fake_useragent import UserAgent


class RandomStreetViewParser:
    """
    Parser for randomstreetview.com
    """

    def __init__(self, driver_path, width=1024, height=768):
        """
        Create the random user agent driver
        """
        options = Options()
        options.add_argument(f"window-size={width},{height}")
        ua = UserAgent()
        user_agent = ua.random
        options.add_argument(f"user-agent={user_agent}")

        driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
        self.driver = driver

    # def go_fullscreen(self):
    #     """
    #     Go fullscreen for a simple way to remove the UI and go panoramic
    #     """
    #     self.driver.find_element(By.XPATH, "//*[@id='pano']/div/div[8]/button").click()

    def hide_elements(self):
        js_script = """\
        document.getElementById('minimaximize').setAttribute("hidden","");
        document.getElementById('intro').setAttribute("hidden","");
        document.getElementById('intro_bg1').setAttribute("hidden","");
        document.getElementById('intro_bg2').setAttribute("hidden","");
        document.getElementById('intro_bg3').setAttribute("hidden","");
        document.getElementById('intro_bg4').setAttribute("hidden","");
        document.getElementById('map_canvas').setAttribute("hidden","");
        document.getElementById('address').setAttribute("hidden","");
        document.getElementById('adnotice').setAttribute("hidden","");
        document.getElementById('ad').setAttribute("hidden","");
        document.getElementById('controls').setAttribute("hidden","");
        document.getElementById('share').setAttribute("hidden","");
        document.getElementById('ad').setAttribute("hidden","");
        
        elements = document.getElementsByTagName('button');
        
        for (element of elements) {
        element.setAttribute("hidden","");
        } 
        """
        self.driver.execute_script(js_script)

    def get_address(self):
        """
        Find the named address of the image from randomstreetview.com
        """
        self.address = self.driver.find_element(By.ID, "address").text

    def rotate_canvas(self):
        """
        Drag and click the <gm-style> elem a few times to rotate the screen ~90 degrees.
        Credit: https://github.com/healeycodes
        """
        main = self.driver.find_element(By.CLASS_NAME, "gm-style")
        for _ in range(0, 3):
            action = webdriver.common.action_chains.ActionChains(self.driver)
            
            # drag and click along the top to avoid hitting Google UI arrows
            action.move_to_element_with_offset(main, 250, 100).click_and_hold(
                main
            ).move_by_offset(250, 0).release(main).perform()

    def screenshot_panoramic(self, save_location="../data/rsv", num_screenshots=3):
        """
        Take a screenshot of the streetview canvas.
        """
        # initate
        images = []
        print(f"Beginning to scrape a panoramic from {self.address}")

        # repeat: screenshot, save, rotate
        for ss in range(0, num_screenshots):

            # allow for screen to buffer
            time.sleep(1)
            raw_image_location = f"{save_location}/raw/{self.address}_{ss}.png"

            # screenshot
            with open(raw_image_location, "xb") as f:
                canvas = WebDriverWait(self.driver, 1).until(
                    EC.element_to_be_clickable((By.TAG_NAME, "canvas"))
                )

                image_data = BytesIO(canvas.screenshot_as_png)
                image = Image.open(image_data)
                width, height = image.size
                # remove the left and bottom UI elements
                cropped_image = image.crop((0, 0, width, height - 75))
                cropped_image.save(f)

            images.append(Image.open(raw_image_location))

            if ss == num_screenshots - 1:
                break
            else:
                self.rotate_canvas()

        # combine images to panoramic
        widths, heights = zip(*(i.size for i in images))
        total_width = sum(widths)
        max_height = max(heights)
        new_im = Image.new("RGB", (total_width, max_height))
        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]
        new_im.save(
            # f"../data/rsv/panoramic/{raw_address}.jpg"
            f"{save_location}/panoramic/{self.address}.jpg"
        )
