import io
from playwright.sync_api import sync_playwright
import pandas as pd
from geolocation import getcoords


MAIN_TAB_XPATH = '//a[contains(@href, "https://www.google.com/maps/place")]'

data = None


def get_excel_bytes(data):
    df = pd.DataFrame(data)

    output = io.BytesIO()

    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)

    writer.close()

    return output.getvalue()


def scrape_maps(search_term, city, state, num_items):

    lat, lon = getcoords(f"{city}, {state}")

    URL = f"https://www.google.com/maps/@{lat},{lon},12z?entry=ttu"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        page.goto(URL)

        searchbox = page.locator("#searchboxinput")
        searchbox.click()
        searchbox.fill(f"{search_term} near me")
        page.keyboard.press("Enter")
        page.wait_for_timeout(2000)

        page.hover(MAIN_TAB_XPATH)

        results = page.locator(MAIN_TAB_XPATH).all()

        while len(results) < num_items:
            page.mouse.wheel(0, 1000)
            page.wait_for_timeout(2000)

            results = page.locator(MAIN_TAB_XPATH).all()
            print(len(results))

            if len(results) >= num_items:
                break

        titles = []
        webs = []
        phones = []
        addrs = []

        for result in results:
            result.click()

            page.wait_for_timeout(2000)

            response = page.get_by_role("main").last

            title = address = website = phone = ""

            if response.locator("h1").last.is_visible():
                title = response.locator("h1").last.inner_text()

            if response.locator("[data-item-id='address']").locator(".fontBodyMedium").is_visible():
                address = response.locator(
                    "[data-item-id='address']").locator(".fontBodyMedium").inner_text()

            if response.locator("[data-item-id='authority']").is_visible():
                website = response.locator(
                    "[data-item-id='authority']").get_attribute("href")

            if response.locator("[data-tooltip='Copy phone number']").locator(".fontBodyMedium").is_visible():
                phone = response.locator(
                    "[data-tooltip='Copy phone number']").locator(".fontBodyMedium").inner_text()

            titles.append(title)
            addrs.append(address)
            webs.append(website)
            phones.append(phone)

        data = {
            "Titles": titles,
            "Address": addrs,
            "Website": webs,
            "Phone No.": phones
        }

        browser.close()

    return get_excel_bytes(data=data)
