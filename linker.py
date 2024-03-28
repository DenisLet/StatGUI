from playwright.sync_api import sync_playwright
from main_selectors import Selectors
import time

def link_handler(url):
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            context.set_default_timeout(20000)
            page = context.new_page()
            page.goto(url)

            team_home_element = page.query_selector(Selectors.team_home).text_content()
            team_away_element = page.query_selector(Selectors.team_away).text_content()
            league_element = page.query_selector(Selectors.tournament)
            league = league_element.text_content()
            t1_q1 = int(page.query_selector_all(Selectors.home_part[1])[0].inner_text())
            t2_q1 = int(page.query_selector_all(Selectors.away_part[1])[0].inner_text())
            t1_q2 = int(page.query_selector_all(Selectors.home_part[2])[0].inner_text())
            t2_q2 = int(page.query_selector_all(Selectors.away_part[2])[0].inner_text())
            t1_q3 = int(page.query_selector_all(Selectors.home_part[3])[0].inner_text())
            t2_q3 = int(page.query_selector_all(Selectors.away_part[3])[0].inner_text())
            print(team_home_element)
            print(team_away_element)
            print(league)
            print(t1_q1, t2_q1, t1_q2, t2_q2, t1_q3, t2_q3)

            page.click(Selectors.odds_on_bar)
            page.click(Selectors.total_button)

            all_totals = page.query_selector_all(Selectors.coef_box)
            aqurate_total = page.query_selector_all('.ui-table__row')

            ave_tot = []
            for element in aqurate_total:
                inner_text = element.inner_text()
                # Проверяем наличие элемента с атрибутом title, содержащим слово "removed"
                removed_element = element.query_selector('[title*="removed"]')
                if removed_element:
                    inner_text += " (removed)"
                    continue
                ave_tot.append(inner_text)

            avg_total_value = find_average_value(ave_tot)

            page.click(Selectors.handicap_button)
            all_hadicaps = page.query_selector_all(Selectors.coef_box)
            aqurate_handicap = page.query_selector_all('.ui-table__row')

            ave_hand = []
            for element in aqurate_handicap:
                inner_text = element.inner_text()
                # Проверяем наличие элемента с атрибутом title, содержащим слово "removed"
                removed_element = element.query_selector('[title*="removed"]')
                if removed_element:
                    inner_text += " (removed)"
                    continue
                ave_hand.append(inner_text)
            avg_handicap_value = find_average_value(ave_hand)

            print(avg_total_value, avg_handicap_value)

        except Exception as e:
            print("Произошла ошибка при открытии страницы:", e)

    return {
        't1q1': t1_q1, 't2q1': t2_q1, 't1q2': t1_q2, 't2q2': t2_q2, 't1q3': t1_q3, 't2q3': t2_q3,
        'total': avg_total_value,
        'hc': avg_handicap_value
    }



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



link_handler('https://www.basketball24.com/match/6XPfhm6l/#/match-summary/match-summary')