'''
Python script to fetch election results for 'General Election to Parliamentary Constituencies June-2024'.

This script updates the data every 5 seconds and sorts it based on the number of seats won.

Author: Atul S
Created Date: June 6, 2024
'''

import sys
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.box import ROUNDED


# Base url for request
URL = "https://results.eci.gov.in/PcResultGenJune2024/index.htm"


def make_request_and_make_soup(url: str) -> BeautifulSoup:
    '''make api request and return result'''

    html_page = requests.get(url)

    print(html_page.content, file=open('main.html', 'w'))

    soup = BeautifulSoup(html_page.content, features="html.parser")
    return soup


def filter_and_clean_data(soup: BeautifulSoup) -> tuple[list, dict]:
    '''extracts, filters and clean data for table consumption'''

    table = soup.find('table', attrs={"class": "table"})

    table_header = table.find('thead').find_all("th")
    table_header = [header.string for header in table_header]

    table_body = table.find('tbody').find_all("tr", attrs={"class": "tr"})
    table_data = [row.find_all('td') for row in table_body]

    table_data_cleaned = []

    for rows in table_data:
        data_cleaned = {}
        for index, row in enumerate(rows):
            if row.a:
                data_cleaned.update(
                    {table_header[index]: str(row.a.string).strip()})
            else:
                data_cleaned.update(
                    {table_header[index]: str(row.string).strip()})
        table_data_cleaned.append(data_cleaned)

    sorted(table_data_cleaned, key=lambda x: x['Won'], reverse=True)

    return table_header, table_data_cleaned


def create_table_from_data_and_display_result(header: str, table_header: list, table_data_cleaned: dict) -> Table:
    '''create tables form given data and return table object'''
    table = Table(title=header, box=ROUNDED, safe_box=True,
                  show_lines=True, header_style="bold yellow")

    for header in table_header:
        if header == "Party":
            table.add_column(header)
        elif header == 'Won':
            table.add_column(header, style="green")
        elif header == "Leading":
            table.add_column(header, style="magenta")
        elif header == 'Total':
            table.add_column(header, style="green")
        else:
            pass

    for row in table_data_cleaned:
        table.add_row(*row.values())

    return table


def main():
    try:
        console = Console()
        with Live(console=console, refresh_per_second=5) as live:
            while True:
                try:
                    # create soup
                    soup = make_request_and_make_soup(URL)

                    # get main table header
                    header = soup.h5.string

                    # get table column header and cleaned data
                    table_header, table_data_cleaned = filter_and_clean_data(
                        soup)

                    # get table object
                    table = create_table_from_data_and_display_result(
                        header, table_header, table_data_cleaned)

                    # print table every 5 second and update inplace
                    live.update(table)

                except Exception as e:
                    print(f"Got Error - {e}")
                    sys.exit()

    except KeyboardInterrupt:
        print(f"Exiting ...")
        sys.exit()


if __name__ == "__main__":
    main()
