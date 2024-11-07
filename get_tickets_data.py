from bs4 import BeautifulSoup
from selenium import webdriver
import time


def get_tickets_data(driver, dep_code, dest_code, date):
    url = f"https://booking.uz.gov.ua/search-trips/{dep_code}/{dest_code}/list?startDate={date}"
    driver.get(url)
    time.sleep(20)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    main_page_content = soup.find("main")
    tickets = main_page_content.find("ul", class_="grid").contents

    result = []

    for ticket in tickets:
        try:
            ticket_data = ticket.find_all("h3")
            time_start = ticket_data[0].text
            time_finish = ticket_data[1].text
            places_info = ticket.find_all("div", class_="text-DarkGrey")
            if len(places_info) == 2:
                result.append(f"{time_start}-{time_finish}; {places_info[0].text} по {ticket_data[3].text}; {places_info[1].text} по {ticket_data[4].text}")
            elif len(places_info) == 1:
                result.append(f"{time_start}-{time_finish}; {places_info[0].text} по {ticket_data[3].text};")
        except IndexError:
            print("Неочікуванна відповідь!")
    return url, result


if __name__ == '__main__':
    driver = webdriver.Firefox()
    data = get_tickets_data(driver, "2200001", "2204001", "2024-11-15")
    driver.close()
    print(data)
