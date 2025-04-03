from robocorp.tasks import task
from RPA.HTTP import HTTP
from RPA.JSON import JSON
from RPA.Tables import Tables
from robocorp import workitems

http=HTTP()
json=JSON()
table=Tables()

TRAFFIC_JSON_FILE_PATH = "output/traffic.json"
# JSON data keys
COUNTRY_KEY = "SpatialDim"
YEAR_KEY = "TimeDim"
RATE_KEY = "NumericValue"
GENDER_KEY = "Dim1"


@task
def produce_traffic_data():
    """
    Inhuman Insurance, Inc. Artificial Intelligence System automation.
    Produces traffic data work items.
    """
    http.download(
        url="https://github.com/robocorp/inhuman-insurance-inc/raw/main/RS_198.json",
        target_file="output/traffic.json",
        overwrite=True,
    )
    traffic_data = load_traffic_data_as_table()
    filtered_data = filter_and_sort_traffic_data(traffic_data)
    filtered_data = get_latest_data_by_country(filtered_data)
    payloads = create_work_item_payloads(filtered_data)
    save_work_item_payloads(payloads)


def load_traffic_data_as_table():
    json_data = json.load_json_from_file(TRAFFIC_JSON_FILE_PATH)
    table_from_json = table.create_table(json_data["value"])
    return table_from_json

def filter_and_sort_traffic_data(data):
    rate_key = "NumericValue"
    max_rate = 5.0
    gender_key = "Dim1"
    both_genders = "BTSX"
    year_key = "TimeDim"
    table.filter_table_by_column(data, rate_key, "<", max_rate)
    table.filter_table_by_column(data, gender_key, "==", both_genders)
    table.sort_table_by_column(data, year_key, False)
    return data


def get_latest_data_by_country(data):
    data = table.group_table_by_column(data, COUNTRY_KEY)
    latest_data_by_country = []
    for group in data:
        first_row = table.pop_table_row(group)
        latest_data_by_country.append(first_row)
    return latest_data_by_country

def create_work_item_payloads(traffic_data):
    payloads = []
    for row in traffic_data:
        payload = dict(
            country=row[COUNTRY_KEY],
            year=row[YEAR_KEY],
            rate=row[RATE_KEY],
        )
        payloads.append(payload)
    return payloads

def save_work_item_payloads(payloads):
    for payload in payloads:
        variables = dict(traffic_data=payload)
        workitems.outputs.create(variables)
