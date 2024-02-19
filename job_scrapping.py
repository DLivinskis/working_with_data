import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
import json
import psycopg2

url = "https://cv.lv/lv/search?limit=20&offset=0&fuzzy=true&suitableForRefugees=false&isHourlySalary=false&isRemoteWork=false&isQuickApply=false"
def find_number_of_jobs(soup):
    numbers = [] #Create an empty list as otherwise function does not work
    specific_text = "Meklēšanas rezultāti" #part of the text that I want to find inside of span; typically full value looks like this: "Meklēšanas rezultāti (2275):"
    spans = soup.find_all('span') #find all span elements
    for span in spans: # iterate through all span elements
        if specific_text in span.text: # if inside of a span element there is text from variable specific_text execute the below code
            number = re.findall(r'\d+\.\d+|\d+', span.text) #extract numbers out of the span element
            numbers += number #add to the list the result
            number_to_return = numbers[0] #return first object from the list; For some reason there werew 2 identical span elements, so I am taking the first one
    return number_to_return


def getting_soup_object_for_scrapping(url):
    response = requests.get(url)
    response.raise_for_status()  # Check for HTTP request errors
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def creating_file_with_jobs(soup):
    job_title_list = []
    job_locations_list = []
    job_expiration_list = []
    job_salary_list = []
    employer_list = []
    job_link_list = []
    class_to_find = "vacancy-item"
    found_elements = soup.find_all('a', class_=class_to_find)
    for element in found_elements:
        job_title = element.find(class_='vacancy-item__title')
        job_title_list.append(job_title.get_text())
        job_location = element.find(class_='vacancy-item__locations')
        job_locations_list.append(job_location.get_text())
        job_expiration = element.find(class_='vacancy-item__expiry')
        job_expiration_list.append(job_expiration.get_text())
        try:
            job_salary = element.find(class_='vacancy-item__salary-label')
            job_salary_list.append(job_salary.get_text())
        except:
            job_salary_list.append('no salary')
        employer = element.find(class_='vacancy-item__column')
        employer_list.append(employer.get_text())
        href = element.get('href')
        job_link = 'cv.lv' + href
        job_link_list.append(job_link)

    matrix = [[title, salary, company, location, expiration, link] for title, salary, company, location, expiration,
                                                                       link in
              zip(job_title_list, job_salary_list, employer_list, job_locations_list, job_expiration_list,
                  job_link_list)]

    df = pd.DataFrame(matrix)
    new_column_names = ['Job Title', 'Salary', 'Company', 'Location', 'Expiration Date', 'URL']
    df.columns = new_column_names
    current_timestamp = datetime.now()
    df['snapshot_date'] = current_timestamp
    return df

def write_output_to_excel(df):
    df.to_excel('jobs.xlsx', index=False)

def write_output_to_postgresql(df,table_name):
    with open(r'W:\Coding\PythonProjects\Main_Python_Project\link_to_db.json') as f:
        # Load JSON data
        data = json.load(f)
    db_url = data['link_to_db']
    engine = create_engine(db_url)
    df.to_sql(table_name, engine, if_exists='append', index=False)

soup_for_number_of_jobs = getting_soup_object_for_scrapping(url)
number_of_jobs = find_number_of_jobs(soup_for_number_of_jobs)
url_for_scrapping = f"https://cv.lv/lv/search?limit={number_of_jobs}&offset=0&fuzzy=true&suitableForRefugees=false&isHourlySalary=false&isRemoteWork=false&isQuickApply=false"
soup_for_final_table = getting_soup_object_for_scrapping(url_for_scrapping)
df = creating_file_with_jobs(soup_for_final_table)
# write_output_to_excel(df)

table_name = 'jobs'
write_output_to_postgresql(df,table_name)
print('job vacancies are written to the database')












