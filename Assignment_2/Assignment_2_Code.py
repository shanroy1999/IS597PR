import datetime

# Class to represent individual storm records
class StormRecord:
    # Wind speed thresholds for categorizing storms
    CATEGORY_THRESHOLDS = {
        1: (64, 82),
        2: (83, 95),
        3: (96, 112),
        4: (113, 136),
        5: (137, float('inf'))
    }

    def __init__(self, line):
        # Process only lines that have a valid date format
        if line[:8].isdigit():
            date = line[:8]  # Extract the date
            time = line[9:13].strip().zfill(4)  # Extract and format the time to 4 characters
            datetime_str = (date + time)[:12]  # Ensure the datetime string has exactly 12 characters

            # Attempt to convert the string to a datetime object
            try:
                self.datetime = datetime.datetime.strptime(datetime_str, '%Y%m%d%H%M')
            except ValueError:
                # Default to 00:00 if the time is invalid
                self.datetime = datetime.datetime.strptime(date + '0000', '%Y%m%d%H%M')

            # Extract wind speed and pressure, handling missing data
            self.wind_speed = int(line[38:41].strip()) if line[38:41].strip() != '-999' else 0
            self.pressure = int(line[43:47].strip()) if line[43:47].strip() != '-999' else float('inf')
            self.landfall = 'L' in line[13:15]  # Check if the record indicates landfall

            # Extract latitude and handle invalid data gracefully
            try:
                lat_value = line[23:27].strip()
                self.latitude = float(lat_value[:-1]) * (-1 if 'S' in lat_value else 1)
            except ValueError:
                self.latitude = 0.0  # Default latitude if parsing fails
        else:
            # Default values for non-date lines
            self.datetime = None
            self.wind_speed = 0
            self.pressure = float('inf')
            self.landfall = False
            self.latitude = 0.0

    # Determine the category of the storm based on wind speed
    def get_category(self):
        for cat, (min_wind, max_wind) in self.CATEGORY_THRESHOLDS.items():
            if min_wind <= self.wind_speed <= max_wind:
                return cat
        return 0

# Class to represent a complete storm
class Storm:
    def __init__(self, storm_id, name):
        self.id = storm_id
        self.name = name if name != 'UNNAMED' else ''
        self.records = []  # List to hold all records associated with the storm

    def add_record(self, record):
        # Only add records with valid datetime
        if record.datetime:
            self.records.append(record)

    # Analyze the storm data to generate summary statistics
    def analyze(self):
        if not self.records:
            return None

        start, end = self.records[0].datetime, self.records[-1].datetime
        duration = end - start
        max_wind = max(r.wind_speed for r in self.records)

        # Determine minimum pressure, if available
        valid_pressures = [r.pressure for r in self.records if r.pressure != float('inf')]
        min_pressure = min(valid_pressures) if valid_pressures else 'N/A'

        # Count landfalls at Category 1 or higher
        landfalls = sum(1 for r in self.records if r.landfall and r.get_category() >= 1)

        # Check if the storm originated and stayed within the tropics
        originated_within_tropics = abs(self.records[0].latitude) <= 23.436
        stayed_within_tropics = all(abs(r.latitude) <= 23.436 for r in self.records)

        # Determine the peak category of the storm
        peak_category = max(r.get_category() for r in self.records)

        # Return the summary statistics
        return {
            'summary': f"{self.id} {self.name} Duration: {duration.days} days {duration.seconds//3600} hours, Max Wind: {max_wind} knots, Min Pressure: {min_pressure} mb, Landfalls: {landfalls}",
            'year': start.year,
            'peak_category': peak_category,
            'originated_within_tropics': originated_within_tropics,
            'stayed_within_tropics': stayed_within_tropics
        }

# Class to process HURDAT files and generate reports
class HURDATProcessor:
    def __init__(self, filenames):
        self.filenames = filenames
        self.storms = []  # List to store analyzed storm data

    # Process the input files and extract storm data
    def process_files(self):
        for filename in self.filenames:
            with open(filename, 'r') as file:
                current_storm = None

                for line in file:
                    if line.startswith(('AL', 'EP', 'CP')):  # Identify storm headers
                        if current_storm:
                            analysis = current_storm.analyze()
                            if analysis:
                                self.storms.append(analysis)
                        storm_id, name = line[:8].strip(), line[9:29].strip()
                        current_storm = Storm(storm_id, name)
                    else:
                        current_storm.add_record(StormRecord(line))

                # Process the last storm in the file
                if current_storm:
                    analysis = current_storm.analyze()
                    if analysis:
                        self.storms.append(analysis)

    # Generate output file with summary statistics
    def generate_output(self, output_file='output.txt'):
        yearly_summary = {}
        originated_tropics = stayed_tropics = 0
        total_storms = len(self.storms)

        # Aggregate yearly statistics
        for storm in self.storms:
            year = storm['year']
            yearly_summary.setdefault(year, {'Storms': 0, 'Cat1': 0, 'Cat2': 0, 'Cat3': 0, 'Cat4': 0, 'Cat5': 0})
            yearly_summary[year]['Storms'] += 1
            if storm['peak_category']:
                yearly_summary[year][f'Cat{storm['peak_category']}'] += 1

            originated_tropics += storm['originated_within_tropics']
            stayed_tropics += storm['stayed_within_tropics']

        # Write output to file
        with open(output_file, 'w') as out_file:
            for storm in self.storms:
                out_file.write(storm['summary'] + '\n')

            # Write annual statistics
            out_file.write("\nYear    Storms  Cat1  Cat2  Cat3  Cat4  Cat5\n")
            for year in range(min(yearly_summary), max(yearly_summary) + 1):
                data = yearly_summary.get(year, {'Storms': 0, 'Cat1': 0, 'Cat2': 0, 'Cat3': 0, 'Cat4': 0, 'Cat5': 0})
                out_file.write(f"{year:<8}{data['Storms']:<8}{data['Cat1']:<6}{data['Cat2']:<6}{data['Cat3']:<6}{data['Cat4']:<6}{data['Cat5']:<6}\n")

            # Write tropical origin and stay statistics
            out_file.write(f"\nPercentage of storms that ORIGINATED within the Tropics: {originated_tropics / total_storms * 100:.2f}%\n")
            out_file.write(f"Percentage of storms that STAYED ENTIRELY within the Tropics: {stayed_tropics / total_storms * 100:.2f}%\n")

# Main program execution
if __name__ == "__main__":
    processor = HURDATProcessor(['hurdat2_atlantic.txt', 'hurdat2_pacific.txt'])
    processor.process_files()
    processor.generate_output()
