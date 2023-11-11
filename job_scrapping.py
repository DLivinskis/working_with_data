import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
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
    # below part is about extracting all information from webpage
    partial_class_title = "vacancy-item__title"  # here we are defining classes that we want to seach for
    partial_class_salary = "vacancy-item__salary-label"
    desired_class_company = "vacancy-item__body"
    desired_class_locations = "vacancy-item__locations"
    desired_class_expiration = "vacancy-item__info-secondary"
    desired_class_job_link = "vacancy-item"

    elements_job_title = soup.find_all('span', class_=lambda value: value and partial_class_title in value)  # <span class="jsx-3024910437 vacancy-item__title">Loģistikas asistents/-e</span> -> value = jsx-3024910437 vacancy-item__title; and we check if inside of value there is string that we want to find
    list_of_job_titles = []  # this part is extracting everythin with the classes from above and creating empty lists for each column
    elements_job_salary = soup.find_all('span', class_=lambda value: value and partial_class_salary in value)
    list_of_job_salary = []
    elements_companies_div = soup.find_all('div', class_=desired_class_company)
    list_of_companies = []
    elements_locations = soup.find_all('div', class_=desired_class_locations)
    list_of_locations = []
    elements_expiration = soup.find_all('div', class_=desired_class_expiration)
    list_of_expirations = []
    elements_job_link = soup.find_all('a', class_=desired_class_job_link)
    list_of_job_links = []

    for job_title in elements_job_title:  # here we are populating lists created in the previous step
        list_of_job_titles.append(job_title.text)

    for job_salary in elements_job_salary:
        list_of_job_salary.append(job_salary.text)

    for element in elements_companies_div:
        name = element.find('a')
        list_of_companies.append(name.text)

    for location in elements_locations:
        list_of_locations.append(location.text)

    for expiration in elements_expiration:
        name = expiration.find("span", class_='vacancy-item__expiry')
        list_of_expirations.append(name.text)

    for job_link in elements_job_link:
        name = "cv.lv" + job_link.get("href")
        list_of_job_links.append(name)

    # below part is for creating matrix out of lists from the above part
    # Using list comprehension to create a matrix
    matrix = [[title, salary, company, location, expiration, link] for
              title, salary, company, location, expiration, link in
              zip(list_of_job_titles, list_of_job_salary, list_of_companies, list_of_locations, list_of_expirations,
                  list_of_job_links)]

    # below part is transforming our matrix into pandas dataframe and renames indexes to columns
    df = pd.DataFrame(matrix)
    new_column_names = ['Job Title', 'Salary', 'Company', 'Location', 'Expiration Date', 'URL']
    df.columns = new_column_names
    current_timestamp = datetime.now()
    df['snapshot_date'] = current_timestamp
    return df

def write_output_to_excel(df):
    df.to_excel('jobs.xlsx', index=False)

def write_output_to_postgresql(df):
    db_url = "postgresql://dmitrijsl:020399@localhost:5432/scrapping_storage"
    engine = create_engine(db_url)
    table_name = 'jobs'

    df.to_sql(table_name, engine, if_exists='append', index=False)

soup_for_number_of_jobs = getting_soup_object_for_scrapping(url)
number_of_jobs = find_number_of_jobs(soup_for_number_of_jobs)
url_for_scrapping = f"https://cv.lv/lv/search?limit={number_of_jobs}&offset=0&fuzzy=true&suitableForRefugees=false&isHourlySalary=false&isRemoteWork=false&isQuickApply=false"
soup_for_final_table = getting_soup_object_for_scrapping(url_for_scrapping)
df = creating_file_with_jobs(soup_for_final_table)
# write_output_to_excel(df)
write_output_to_postgresql(df)












