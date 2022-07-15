import pandas as pd
from configparser import ConfigParser
import numpy as np
import math
import configparser

# This function is not used 
def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

# Read the base templates
def readBaseTemplates(configFileName):
    
    # Read config.ini file
    config = configparser.ConfigParser()
    config.read(configFileName)
    
    # get the path of the template folder from the config file
    folder = config.get('TEMPLATE', 'folder')
    nameTemplateFile = config.get('TEMPLATE', 'nameTemplateFile')
    fileNameRead = folder + nameTemplateFile
    
    # Read the base template
    baseTemplate = pd.read_csv(fileNameRead)

    # transform column names into lowcase to make them case insensitive
    baseTemplate.columns = baseTemplate.columns.str.lower() 
    
    return baseTemplate

def createNewFile(configFileName, baseTemplate):
    
    # Read config.ini file
    config = configparser.ConfigParser()
    config.read(configFileName)
    
    # get the rows to select from template 
    template_rows = config.get('TEMPLATE', 'columns')
    template_rows_lower = [s.lower().replace(' ', '') for s in template_rows.split(',')]
    
    # make the subset from the template file
    baseTemplate_subset = baseTemplate[template_rows_lower]
    
    # add the new colmns to the template
    new_columns = config.options('NEW_COLUMNS')
    number = len(template_rows_lower) # for the dataframe positionof new columns
    for new_column in new_columns:

        if new_column == 'sampling_identifier':
            # add the text 'sampling' fo the new column if it is 'season_Of_sampling'
            baseTemplate_subset.insert(number, new_column, 'sampling-' + config.get('NEW_COLUMNS', new_column))

        else:
            baseTemplate_subset.insert(number, new_column, config.get('NEW_COLUMNS', new_column))
        number += 1
        
    # create the rows for the number of measurements that are going to be taken from each row
    timesRepeatRow = len(config.get('NEW_FILE_CONFIG', 'Sample_ID').split(','))
    baseTemplate_subset_rep = baseTemplate_subset.loc[baseTemplate_subset.index.repeat(timesRepeatRow)]
    
    # get the rows to select from template 
    plots_file = config.get('NEW_FILE_CONFIG', 'Sample_ID')
    plots = [s.lower().replace(' ', '') for s in plots_file.split(',')]

    #columns_row = int(config.get('NEW_FILE_CONFIG', 'columnsPerRow'))
    baseTemplate_subset_rep['sample_name'] = plots * int(len(baseTemplate_subset_rep)/len(plots))

    # move the'Sample_ID' column to the fist position of the data frame
    col = baseTemplate_subset_rep.pop('sample_name')
    baseTemplate_subset_rep.insert(0, col.name, col)
    
    # get the rows to select from template 
    template_rows = config.get('TEMPLATE', 'columns')
    template_rows_lower = [s.lower().replace(' ', '') for s in template_rows.split(',')]
    
    # get the rows to select from template 
    plots_file = config.get('NEW_FILE_CONFIG', 'Sample_ID')
    plots = [s.lower().replace(' ', '') for s in plots_file.split(',')]

    #columns_row = int(config.get('NEW_FILE_CONFIG', 'columnsPerRow'))
    baseTemplate_subset_rep['sample_name'] = plots * int(len(baseTemplate_subset_rep)/len(plots))

    # move the'Sample_ID' column to the fist position of the data frame
    col = baseTemplate_subset_rep.pop('sample_name')
    baseTemplate_subset_rep.insert(0, col.name, col)

    # create the plot ID base on the value of other columns
    a = baseTemplate_subset_rep['plot'].astype(str)
    b = baseTemplate_subset_rep['sample_name']
    c = baseTemplate_subset_rep['experiment']
    d = baseTemplate_subset_rep['environment']
    e = baseTemplate_subset_rep['season']
    f = baseTemplate_subset_rep['measurment']
    g = baseTemplate_subset_rep['sampling_identifier']
    baseTemplate_subset_rep["id_sample"] = a + '_' + b + '_' + c + '_' + d + '_' + e + '_' + f + '_' + g

    # move the'id_plot' column to the fist position of the data frame
    col = baseTemplate_subset_rep.pop('id_sample')
    baseTemplate_subset_rep.insert(0, col.name, col)
    
    # reset dataframe index
    baseTemplate_subset_rep = baseTemplate_subset_rep.reset_index(drop=True)
    measurment = config.get('NEW_COLUMNS', 'measurment')

    #extract elements from config file to the new file name
    measurment = config.get('NEW_COLUMNS', 'measurment')
    sampling_identifier = config.get('NEW_COLUMNS', 'sampling_identifier')
    experiment = config.get('NEW_COLUMNS', 'experiment')
    environment = config.get('NEW_COLUMNS', 'environment')
    season = config.get('NEW_COLUMNS', 'season')

    # get the path of the template folder from the config file
    folder = config.get('TEMPLATE', 'folder')
    # create the name of the file
    nameNewFile = folder + measurment + '_' + sampling_identifier + '_' + experiment + '_' + environment + '_' + season + '.csv'
    
    # export file into csv
    baseTemplate_subset_rep.to_csv(nameNewFile, index=False)