# This section lists packages to be imported
from os import listdir
import pandas as pd
import openpyxl as op
from datetime import datetime

# This section asks for an input for the (1) the directory of the template file; (2) the directory of the file to save under; (3) the path with all the excel files that data will be extracted from.
wb_list = []
final_wb_directory = input("Please enter the directory of the file you would like to use as the template:")
final_wb_directory_save = input("Please enter the directory with the file name you would like to save changes to:")
path = input("Please enter the directory of the folder you would like to add:")
path = path + "/" # Adding an extra slash to show that this is a folder

# This section extracts the individual paths of all the files within the folder that the excel files are in
dir_list = listdir(path)
for i in range(len(dir_list)):
    dir_list[i] = path + dir_list[i]

# This section removes DS STORE hidden file if it exists (Useless metadata file found on most computer systems)
ds_store_path = path + ".DS_Store"
if ds_store_path in dir_list:
    dir_list.remove(ds_store_path)

# This section shows you the excel file paths that have been extracted
wb_list = dir_list
print("\nThe workbooks you have added are:")
print(wb_list)

# This section defines lists to copy data into
Portfolio_name_list = []
Security_ID_list = []
Type_list = []
Security_Name_list = []
Quantity_list = []
Cost_price = []
Currency_list = []
Exchange_list = []
New_Security_ID_list = []
Date_list = []

# This section creates lists of all the lists so that iteration through all of them takes less lines of code. The second list narrows down the first list of lists into one that contains solely the data to be moved into the final file for storage.
Concatenated_lists = [Portfolio_name_list, Type_list, Security_ID_list, Security_Name_list, Quantity_list, Cost_price, Currency_list, Exchange_list, Date_list]
Concatenated_lists2 = [Portfolio_name_list, New_Security_ID_list, Security_Name_list, Quantity_list, Cost_price, Date_list]

for i in wb_list:
    # This section reads each excel file one by one using pandas
    print(i)
    wb_fixinc = pd.read_excel(i)
    print("\nSuccessfully opened file {}".format(i))
    print(wb_fixinc)

    # This section transfers data from specific columns in the sheet to the set of lists
    Portfolio_name_list.extend(wb_fixinc[wb_fixinc.columns[0]].values.tolist())
    Security_ID_list.extend(wb_fixinc[wb_fixinc.columns[43]].values.tolist())
    Type_list.extend(wb_fixinc[wb_fixinc.columns[3]].values.tolist())
    Security_Name_list.extend(wb_fixinc[wb_fixinc.columns[5]].values.tolist())
    Quantity_list.extend(wb_fixinc[wb_fixinc.columns[6]].values.tolist())
    Cost_price.extend(wb_fixinc[wb_fixinc.columns[13]].values.tolist())
    Currency_list.extend(wb_fixinc[wb_fixinc.columns[12]].values.tolist())
    Exchange_list.extend(wb_fixinc[wb_fixinc.columns[17]].values.tolist())
    Date_list.extend(wb_fixinc[wb_fixinc.columns[2]].values.tolist())

# This section sets the values of the Date list to be datetime objects for easier manipulation
for i in range(len(Date_list)):
    Date_list[i] = pd.to_datetime(Date_list[i])

# This section searches for the first date that is not stored as "nan", not a number, and stores this as the value for the GreatestDate
# Why is this done? This is performed to ensure that the record date for all entries in the final excel file is the latest one found in all of the sheets, which requires comparing the date values of each sheet. We start here with the first date object that is detected that is not a "nan" value
for i in range(len(Date_list)):
    if str(Date_list[i]) != "nan":
        Greatestdate = datetime.strptime(str(Date_list[i]), "%Y-%m-%d %H:%M:%S")
        break

# This line compares the datetime object in the whole list to the GreatestDate variable containing the latest date detected so far to check if the date in this sheet is later than the date in the GreatestDate variable, and sets the GreatestDate variable to be the one in this sheet if it is found to be later than that stored in the GreatestDate variable
for i in range(len(Date_list)):
    if str(Date_list[i]) != "nan":
        if datetime.strptime(str(Date_list[i]), "%Y-%m-%d %H:%M:%S") > Greatestdate:
            Greatestdate = datetime.strptime(str(Date_list[i]), "%Y-%m-%d %H:%M:%S")

# This section sets all the values of the final list that will be used as the record date to be that of the GreatestDate value
for i in range(len(Date_list)):
    Date_list[i] = Greatestdate.strftime("%d-%m-%Y")

# This section adds Currency tickers for cases where the security ID is empty (To follow Bloomberg ticker convention)
for i in range(len(Security_Name_list)):
    if str(Security_ID_list[i]) == "nan":
        if "USD" in Currency_list[i]:
            New_Security_ID_list.append("USD Curncy")
        else:
            New_Security_ID_list.append(Currency_list[i] + "USD Curncy")
    else:
        New_Security_ID_list.append(Security_ID_list[i])

# This section sets the cost price to be that of the exchange value if the Type is found to be "Cash" in the type list
for i in range(len(Type_list)):
    if Type_list[i] == "Cash":
        Cost_price[i] = Exchange_list[i]

# This section opens the template workbook and finds a sheet of name "template" within it
final_wb = op.load_workbook(final_wb_directory)
final_sheet = final_wb.get_sheet_by_name("template")

# This section transfers data from the final lists into the final template file and saving using directory given to save to
for i in Concatenated_lists2:
    for j in range(8, len(i)+8):
        if i == Portfolio_name_list:
            final_sheet["Q" + str(j)] = i[j-8]
        if i == New_Security_ID_list:
            final_sheet["C" + str(j)] = i[j-8]
        if i == Security_Name_list:
            final_sheet["A" + str(j)] = i[j-8]
        if i == Quantity_list:
            final_sheet["O" + str(j)] = i[j-8]
        if i == Cost_price:
            final_sheet["P" + str(j)] = i[j-8]
        if i == Date_list:
            final_sheet["D" + str(j)] = i[j-8]

# This line saves the output
final_wb.save(final_wb_directory_save)