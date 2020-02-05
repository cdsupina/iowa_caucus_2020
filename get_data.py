from bs4 import BeautifulSoup
import csv
import xml.etree.ElementTree
import locale

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

CANDIDATES_START_IDX = 2
CANDIDATES_END_IDX = 41
CANDIDATES_OFFSET = 3

COUNTIES_START_IDX = 20
COUNTIES_END_IDX = 432
COUNTIES_OFFSET = 4

PRECINCTS_START_IDX = 88
#PRECINCTS_END_IDX = 58267
PRECINCTS_OFFSET = 43

DATA_ROW_START_IDX = 89
DATA_ROW_END_IDX = 41
DATA_ROW_OFFSET = 43
#data row count equal to the number of precincts

CANDIDATE_DATA_OFFSETS = {
    "Bennet": 0,
    "Biden": 3,
    "Bloomberg": 6,
    "Buttigieg": 9,
    "Delaney": 12,
    "Gabbard": 15,
    "Klobuchar": 18,
    "Patrick": 21,
    "Sanders": 24,
    "Steyer": 27,
    "Warren": 30,
    "Yang": 33,
    "Other": 36,
    "Uncommitted": 39,
}


def remove_tags(tag):
    return ''.join(xml.etree.ElementTree.fromstring(str(tag)).itertext())


def get_candidates(data):
    return [remove_tags(data[i]) for i in range(CANDIDATES_START_IDX, CANDIDATES_END_IDX + 1, CANDIDATES_OFFSET)]


def get_counties(data):
    return [remove_tags(data[i]) for i in range(COUNTIES_START_IDX, COUNTIES_END_IDX + 1, COUNTIES_OFFSET)]


def get_precincts(data):
    return [remove_tags(data[i]) for i in range(PRECINCTS_START_IDX, len(data), PRECINCTS_OFFSET)]


def generate_candidate_csv(candidate, counties, precincts, li_data):
    candidate_data_offset = CANDIDATE_DATA_OFFSETS[candidate]

    # generate data
    row_data = []
    row_data.append(["County", "Precinct", "First Expression", "Final Expression", "SDE"])
    precinct_idx = 0

    for county in counties:
        current_row = [county]

        while True:
            current_row.append(precincts[precinct_idx])
            data_point_start = (precinct_idx * 43) + (89 + candidate_data_offset)
            for data_point_idx in range(data_point_start, data_point_start + 3):
                current_row.append(remove_tags(li_data[data_point_idx]))
            print(current_row)
            row_data.append(current_row)

            precinct_idx += 1

            if precincts[precinct_idx - 1] == "Total":
                break

            current_row = [""]

    with open(candidate.lower() + ".csv", 'w') as f:
        writer = csv.writer(f)
        writer.writerows(row_data)


def generate_totals_csv(counties, precincts, li_data):
    row_data = []
    row_data.append(["County", "Precinct", "First Expression", "Final Expression", "SDE"])
    precinct_idx = 0

    for county in counties:
        current_row = [county]

        while True:
            current_row.append(precincts[precinct_idx])
            first_align_total = 0
            final_align_total = 0
            sde_total = 0
            for offset in CANDIDATE_DATA_OFFSETS.values():
                data_point_start = (precinct_idx * 43) + (89 + offset)

                first_align_total += locale.atoi(remove_tags(li_data[data_point_start]))
                final_align_total += locale.atoi(remove_tags(li_data[data_point_start + 1]))
                sde_total += locale.atof(remove_tags(li_data[data_point_start + 2]))
            current_row.append(first_align_total)
            current_row.append(final_align_total)
            current_row.append(sde_total)

            print(current_row)
            row_data.append(current_row)

            precinct_idx += 1

            if precincts[precinct_idx - 1] == "Total":
                break

            current_row = [""]

    with open("totals.csv", 'w') as f:
        writer = csv.writer(f)
        writer.writerows(row_data)

if __name__ == "__main__":

    html = open("https _results.thecaucuses.org_.html").read()
    soup = BeautifulSoup(html, features="html.parser")
    li_data = soup.findAll("li")
    div_data = soup.find_all("div")

    candidates = get_candidates(li_data)
    counties = get_counties(div_data)
    precincts = get_precincts(li_data)
    print(len(precincts))

    for candidate in candidates:
        generate_candidate_csv(candidate, counties, precincts, li_data)
    generate_totals_csv(counties, precincts, li_data)

