# libraries
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# class that performs feature analysis on weather data
class weather_data_analysis():
    def __init__(self, file_name, LOCATION):
        self.file_name = file_name
        self.LOCATION = LOCATION
        #self.data_frame = None
        pass

    # handle missing values in the data using time series interpolation
    def time_series_interpolation(self, data_frame):
        # iterate through each column
        weather_columns = data_frame.select_dtypes(include=[np.number]).columns
        for column in weather_columns:
            # get the column's values
            values = data_frame[column].values

            # go through each value
            for i in range(len(values)):
                # check if the current value is NaN or null
                if (np.isnan(values[i])):
                    # find the previous existing value
                    previous_index = i - 1
                    while (previous_index >= 0 and np.isnan(values[previous_index])):
                        previous_index = previous_index - 1

                    # find the next existing value
                    next_index = i + 1
                    while (next_index < len(values) and np.isnan(values[next_index])):
                        next_index = next_index + 1

                    # handling edge cases
                    if (previous_index < 0):    # if we are at the first element
                        # check if the next index is not out of bounds
                        if (next_index < len(values)):
                            values[i] = values[next_index]
                        # set the current value to 0 otherwise
                        else:
                            values[i] = 0
                    # check if the next index is out out of bounds
                    elif (next_index >= len(values)):
                            values[i] = values[previous_index]
                    # perform time-series interpolation otherwise
                    else:
                        y1 = values[previous_index]
                        y2 = values[next_index]
                        t1 = previous_index
                        t2 = next_index
                        t_current = i

                        slope = (y2 - y1) / (t2 - t1)
                        values[i] = y1 + slope * (t_current - t1)
            
            # update the column's values
            data_frame[column] = values
        
        return data_frame

    # grab the data from CSV file and handle the data
    def grab_and_handle_data(self):
        # read in the CSV file
        data_frame = pd.read_csv(self.file_name)
        
        # combine Date and Time columns into a single column as an integer timestamp
        data_frame['DateTime'] = pd.to_datetime(data_frame['Date (YYYY-MM-DD)'] + ' ' + data_frame['Time (HH:MM:SS)'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

        # remove unneeded columns
        columns_to_drop = ['Date (YYYY-MM-DD)', 'Time (HH:MM:SS)', 'Location', 'Coordinates', 'Temperature Apparent (F)','Wind Gust (mph)', 'Pressure at Surface Level (inHg)', 'Rain Intensity (in/hr)', 'Freezing Rain Intensity (in/hr)', 'Snow Intensity (in/hr)', 'Sleet Intensity (in/hr)', 'Rain Accumulation (in)', 'Snow Accumulation (in)', 'Snow Accumulation LWE (in of LWE)', 'Snow Depth (in)', 'Sleet Accumulation (in)', 'Sleet Accumulation LWE (in of LWE)', 'Ice Accumulation (in)', 'Ice Accumulation LWE (in of LWE)', 'Cloud Base (mi)', 'Cloud Ceiling (mi)', 'UV Health Concern', 'Evapotranspiration (in)', 'EZ Heat Stress Index']
        columns_to_drop.append('Thunderstorm Probability (%)')
        data_frame.drop(columns_to_drop, axis=1, inplace=True)
        
        # moving DateTime column to the front
        column = data_frame.pop('DateTime')
        data_frame.insert(0, 'DateTime', column)
        
        # set DateTime as the index
        data_frame = data_frame.set_index('DateTime')

        # reindex the data frame based on the DateTime column
        full_range = pd.date_range(start=data_frame.index.min(), end=data_frame.index.max(), freq='h')
        data_frame = data_frame.reindex(full_range)

        # perform time series interpolation on the data frame to handle the missing data values
        data_frame = self.time_series_interpolation(data_frame)

        # convert the DateTime column to numeric and remove the column as the index
        data_frame = data_frame.reset_index().rename(columns={'index': 'DateTime'})
        data_frame['DateTime'] = pd.to_numeric(pd.to_datetime(data_frame['DateTime']).astype('int64'))

        #print(data_frame)
        #print(data_frame.dtypes)
        #print(data_frame.isnull().any())
        #print("\n")
        #print(data_frame.isnull().sum())
        #print("\n")
        #print(data_frame.columns[data_frame.isnull().any()].to_list())
        #print("\n")
        #print(data_frame)
        #print("\n")
        
        return data_frame
    
    # create correlation matrix for the weather data
    def create_correlation_matrix(self, data_frame):
        matrix = data_frame.corr()
        plt.figure(figsize=(10,8))
        sns.heatmap(matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
        plt.title(f"Correlation Matrix Heatmap for {self.LOCATION}")
        plt.show()
        pass

    pass