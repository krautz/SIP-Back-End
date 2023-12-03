#!/bin/bash

# start virtual environment
printf "####################################\n"
printf "#  ACTIVATING VIRTUAL ENVIRONMENT  #\n"
printf "####################################\n"
source env/bin/activate

# ensure dependencies are up to date
printf "####################################\n"
printf "#     INSTALLING DEPENDENCIES      #\n"
printf "####################################\n"
pip install -r requirements.txt

printf "\n\nProvide how many times a prive retrieval failure should be retrieved\n"
read retry_amount

printf "\n\nProvide folder path where all spreadsheets should be updated\n"
read spreadsheet_files_path
for file in $(ls $spreadsheet_files_path/*)
do
    # get file path without extension
    file_split="${file//.xlsx/}"

    # extract only file name
    filename="${file_split//\// }"
    filename=($filename)
    filename="${filename[${#filename[@]}-1]}"

    printf "####################################\n"
    printf "     UPDATING $filename\n"
    printf "####################################\n"
    python scripts/update_prices_spreadsheet.py $file_split
    for _ in $(seq 1 $retry_amount)
    do
        python scripts/retry_api_errors_spreadsheet.py $file_split
    done
done

# exit virutal environment
printf "####################################\n"
printf "# DEACTIVATING VIRTUAL ENVIRONMENT #\n"
printf "####################################\n"
deactivate
