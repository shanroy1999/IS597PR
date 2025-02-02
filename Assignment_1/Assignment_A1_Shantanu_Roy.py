import csv
from collections import defaultdict

# Function to read the file
def parse_co2_file(filename):
    data = defaultdict(list)
    with open(filename, 'r') as f:
        # Parse space-delimited file using csv reader function
        reader = csv.reader(f, delimiter=' ', skipinitialspace=True)
        for row in reader:
            # filter rows starting with MLO and BRW to differentiate the data with the comments/meta-data
            if row[0] in ['MLO', 'BRW']:
                # Extract year, co2 value and the quality check flag from each row
                year = int(row[1])
                value = float(row[7])
                qcflag = row[-1]
                # Check for valid data points and store them in the data dictionary
                if qcflag[0] != '*' and value != -999.99:
                    data[year].append(value)
    return data

# Function to calculate maximum Co2 level and mean Co2 level for each year for valid data
def calculate_stats(data):
    stats = {}
    for year, values in data.items():
        if values:
            stats[year] = {
                'MAX_LEVEL': round(max(values), 2),
                'MEAN_LEVEL': round(sum(values) / len(values), 2)
            }
    return stats

# Calculate % change in mean CO2 levels between consecutive years
def calculate_percent_change(stats):
    # sort the years
    years = sorted(stats.keys())
    for i in range(1, len(years)):
        curr_year = years[i]
        prev_year = years[i - 1]
        if prev_year in stats and curr_year in stats:
            prev_mean = stats[prev_year]['MEAN_LEVEL']
            curr_mean = stats[curr_year]['MEAN_LEVEL']
            # calculate % change between current year and previous year
            percent_change = ((curr_mean - prev_mean) / prev_mean) * 100
            stats[curr_year]['%CHANGE'] = round(percent_change, 2)

# Function to generate a report in text file
def generate_report(alaska_stats, hawaii_stats):
    with open('co2_report.txt', 'w') as f:
        # Write the header for the report
        f.write("ALASKA                                HAWAII\n")
        f.write("YEAR MAX_LEVEL MEAN_LEVEL %CHANGE     MAX_LEVEL MEAN_LEVEL %CHANGE\n")

        # Iterate through all years present either in alaska or in hawaii data
        all_years = sorted(set(alaska_stats.keys()) | set(hawaii_stats.keys()))
        for year in all_years:
            ak_data = alaska_stats.get(year, {})
            hi_data = hawaii_stats.get(year, {})

            # retrieve MAX_LEVEL from dictionary -> if it doesn't exist default value as '-'
            # check if MAX_LEVEL is a number -> either float or integer
            # if it is a number => right align the MAX_LEVEL number value as a string in 9-character wide field
            # if not a number => if its '-' or some other string => right align it in 9 character wide field as well
            ak_max = f"{ak_data.get('MAX_LEVEL', '-'):>9}" if isinstance(ak_data.get('MAX_LEVEL'), (
            int, float)) else f"{ak_data.get('MAX_LEVEL', '-'):>9}"
            ak_mean = f"{ak_data.get('MEAN_LEVEL', '-'):>10}" if isinstance(ak_data.get('MEAN_LEVEL'), (
            int, float)) else f"{ak_data.get('MEAN_LEVEL', '-'):>10}"
            ak_change = f"{ak_data.get('%CHANGE', '-'):>7}" if isinstance(ak_data.get('%CHANGE'), (
            int, float)) else f"{ak_data.get('%CHANGE', '-'):>7}"

            hi_max = f"{hi_data.get('MAX_LEVEL', '-'):>9}" if isinstance(hi_data.get('MAX_LEVEL'), (
            int, float)) else f"{hi_data.get('MAX_LEVEL', '-'):>9}"
            hi_mean = f"{hi_data.get('MEAN_LEVEL', '-'):>10}" if isinstance(hi_data.get('MEAN_LEVEL'), (
            int, float)) else f"{hi_data.get('MEAN_LEVEL', '-'):>10}"
            hi_change = f"{hi_data.get('%CHANGE', '-'):>7}" if isinstance(hi_data.get('%CHANGE'), (
            int, float)) else f"{hi_data.get('%CHANGE', '-'):>7}"

            # Write the co2 max value, mean value and % change for each year in the text file
            f.write(f"{year} {ak_max} {ak_mean} {ak_change}     {hi_max} {hi_mean} {hi_change}\n")

        # calculate the mean annual %change by calculating the mean of the "%change" columns for both Hawaii and Alaska
        ak_mean_change = sum(year['%CHANGE'] for year in alaska_stats.values() if '%CHANGE' in year) / len(alaska_stats)
        hi_mean_change = sum(year['%CHANGE'] for year in hawaii_stats.values() if '%CHANGE' in year) / len(hawaii_stats)

        # Write the mean annual percentage change in the text file
        f.write(f"\nMean annual percent change:\n")
        f.write(f"Alaska: {ak_mean_change:.2f}%\n")
        f.write(f"Hawaii: {hi_mean_change:.2f}%\n")


# Main execution
# Parse the two files
alaska_data = parse_co2_file('co2_alaska.txt')
hawaii_data = parse_co2_file('co2_hawaii.txt')

# Calculate the mean and max of the data
alaska_stats = calculate_stats(alaska_data)
hawaii_stats = calculate_stats(hawaii_data)

# Calculate the percentage change in mean CO2 levels in consecutive years
calculate_percent_change(alaska_stats)
calculate_percent_change(hawaii_stats)

# Generate the final report
generate_report(alaska_stats, hawaii_stats)

print("Report generated: co2_report.txt")