# random_street_view.py

import time
import sys
import string
import random
import json
import numpy as np
import pandas as pd
import jsonlines

# import chromedriver_autoinstaller
import pycountry
from geopy.geocoders import Nominatim

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from os import listdir
from os.path import isfile, join
from datetime import date

from io import BytesIO
from PIL import Image
from fake_useragent import UserAgent

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

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

        self.geolocator = Nominatim(user_agent=str(user_agent))

        driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
        self.driver = driver

        # TODO: TECHNICAL DEBT
        iso = pd.read_csv("../data/utility/iso3166.csv")
        self.name_to_iso_alpha2 = dict(zip(iso["name"], iso["alpha-2"]))

        self.rundate = str(date.today()).replace("-", "")

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
        raw_address = self.driver.find_element(By.ID, "address").text
        self.raw_address = raw_address
        self.address = raw_address.replace(",", "")

    def get_gps_from_address(self):
        """
        Take an address from the scraper and return the latitude and longitude

        return ex: TODO
        """
        preprocessed_address = self.address
        try:
            gps = self.geolocator.geocode(preprocessed_address)
            self.latitude = gps.latitude
            self.longitude = gps.longitude
            coordinates = (gps.latitude, gps.longitude)
        except Exception as e:
            # print(f"Cannot find a gps coordinate for {self.address}")
            coordinates = "_UNLABELED"
            self.latitude = None
            self.longitude = None

        self.coordinates = coordinates

    def get_iso_alpha2_from_address(self):
        """
        Take an address from the scraper and return an iso3166 country code
        
        return ex: TODO
        """

        def get_country_from_address(address):
            return address.replace(".jpg", "").split(",")[-1].lstrip().rstrip()

        country = get_country_from_address(self.raw_address)

        try:
            iso_alpha2 = self.name_to_iso_alpha2[country]
        except Exception as e:
            try:
                iso_alpha2 = pycountry.countries.search_fuzzy(country)[0].alpha_2
            except Exception as e:
                iso_alpha2 = "_UNLABELED"
                # print(f"Could not match {country} to a country")

        self.iso_alpha2 = iso_alpha2

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

        def update_metadata(img_filename, metadata_file_path):
            """
            Helper function that updates the metadata file which contains
            class labels 
            """

            img_labels = {
                "file_name": img_filename,
                "country_iso_alpha2": self.iso_alpha2,
                "latitude": self.latitude,
                "longitude": self.longitude,
            }

            # append labels to metadata file
            with jsonlines.open(metadata_file_path, mode="a") as appender:
                appender.write(img_labels)

        # initate
        images = []
        print(
            f"Beginning to scrape images from {self.address} from alpha2 code {self.iso_alpha2} and gps coordinates {self.coordinates}"
        )
        clean_coordinate = (
            str(self.coordinates)
            .replace("(", "")
            .replace(")", "")
            .replace(",", "_")
            .replace(" ", "")
        )

        # repeat: screenshot, save, rotate
        for ss in range(0, num_screenshots):

            # allow for screen to buffer
            time.sleep(2)

            indv_filename = f"{self.rundate}_{self.address}_{ss}_{clean_coordinate}.png"
            if self.iso_alpha2 == "_UNLABELED":
                raw_image_location = f"{save_location}_indv/unlabeled/{indv_filename}"
                update_metadata(
                    img_filename=indv_filename,
                    metadata_file_path=f"{save_location}_indv/unlabeled/metadata.jsonl",
                )
            else:
                raw_image_location = (
                    f"{save_location}_indv/train/{indv_filename}"
                )
                update_metadata(
                    img_filename=indv_filename,
                    metadata_file_path=f"{save_location}_indv/train/metadata.jsonl",
                )

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

        pano_filename = f"{self.rundate}_{self.address}_{clean_coordinate}.jpg"
        if self.iso_alpha2 == "_UNLABELED":
            new_im.save(
                f"{save_location}_pano/unlabeled/{pano_filename}"
            )
            update_metadata(
                img_filename=pano_filename,
                metadata_file_path=f"{save_location}_pano/unlabeled/metadata.jsonl",
            )
        else:            
            new_im.save(f"{save_location}_pano/train/{pano_filename}")
            update_metadata(
                img_filename=pano_filename,
                metadata_file_path=f"{save_location}_pano/train/metadata.jsonl",
            )
