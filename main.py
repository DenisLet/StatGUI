from playwright.sync_api import sync_playwright
from main_selectors import Selectors
import time

urls = [
        'https://www.basketball24.com/match/f1W9oqwn/#/match-summary/match-summary'
        ]




# Декоратор для засечения времени выполнения функции
def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time of {func.__name__}: {execution_time} seconds")
        return result
    return wrapper



@timer
def find_average_value(coefline):
    k = None
    value = None
    min_diff = 100
    for case in coefline:
        current_total = case.split()[0]
        k1, k2 = list(map(float, case.split()[1:3]))
        diff = abs(k1 - k2)
        if diff < min_diff:
            min_diff = diff
            value = current_total
    print(f"The total/handicap with the smallest diff is: {value}")
    return float(value)

# Декорируем функцию handler() для засечения времени её выполнения
@timer
def handler(url):
    page.goto(url)

    team_home_element = page.query_selector(Selectors.team_home).text_content()
    team_away_element = page.query_selector(Selectors.team_away).text_content()
    league_element = page.query_selector(Selectors.tournament)
    league = league_element.text_content()
    t1_q1 = int(page.query_selector_all(Selectors.home_part[1])[0].inner_text())
    t2_q1 = int(page.query_selector_all(Selectors.away_part[1])[0].inner_text())
    t1_q2 = int(page.query_selector_all(Selectors.home_part[2])[0].inner_text())
    t2_q2 = int(page.query_selector_all(Selectors.away_part[2])[0].inner_text())
    try:
        t1_q3 = int(page.query_selector_all(Selectors.home_part[3])[0].inner_text())
        t2_q3 = int(page.query_selector_all(Selectors.away_part[3])[0].inner_text())
    except:
        t1_q3, t2_q3 = 0, 0
    print(team_home_element)
    print(team_away_element)
    print(league)
    print(t1_q1, t2_q1, t1_q2, t2_q2, t1_q3, t2_q3)



@timer
def get_total():
    page.click(Selectors.odds_on_bar)
    page.click(Selectors.total_button)

    aqurate_total = page.query_selector_all('.ui-table__row')
    print(aqurate_total)


    ave_tot = []
    for element in aqurate_total:
        inner_text = element.inner_text()
        # Проверяем наличие элемента с атрибутом title, содержащим слово "removed"
        removed_element = element.query_selector('[title*="removed"]')

        if removed_element:
            continue
        ave_tot.append(inner_text)

    avg_total_value = find_average_value(ave_tot)
    print('Avg total: ', avg_total_value)

@timer
def get_hc():
    page.click(Selectors.handicap_button)

    aqurate_handicap = page.query_selector_all('.ui-table__row')

    ave_hand = []
    for element in aqurate_handicap:
        inner_text = element.inner_text()
        # Проверяем наличие элемента с атрибутом title, содержащим слово "removed"
        removed_element = element.query_selector('[title*="removed"]')
        if removed_element:
            continue
        ave_hand.append(inner_text)
    avg_handicap_value = find_average_value(ave_hand)

    print(avg_handicap_value)

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    empty_page = context.new_page()

    for url in urls:
        handler(url)
        get_total()
        get_hc()