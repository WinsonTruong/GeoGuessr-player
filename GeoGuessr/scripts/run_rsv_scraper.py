#run_rsv_scraper.py

from RandomStreetViewParser import * 

rsv = RandomStreetViewParser(driver_path='../utility/chromedriver')

for _ in np.arange(10):
    try:
        rsv.driver.get('https://randomstreetview.com/')
        time.sleep(1)
        rsv.get_address()
        rsv.hide_elements()
        time.sleep(1)
        rsv.screenshot_panoramic()
    except Exception as e:
        print(e)
        pass