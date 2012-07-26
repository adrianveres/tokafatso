import csv
import dateutil.parser
import hashlib
import os
import random
import shutil

from django.conf import settings

from tokafatso.models import FacsFile, FacsResult, ResultItem, TestCode, TestCodeMapping

def parse_facs_files():
    """
    Function for parsing the recipient folder for FACS data files.
    """

    #Load parser settings
    parser_settings = getattr(settings,'FACS_PARSER_SETTINGS')

    files_to_parse = [parser_settings['facs_source_directory']+f for f in os.listdir(parser_settings['facs_source_directory']) if '.exp' in f]

    for filename in files_to_parse:            

        #Compute MD5 hash
        facs_file = file(filename,'rbU')
        md5hash = hashlib.md5(facs_file.read()).hexdigest()
        facs_file.close()
        
        #Skip file if previously parsed.
        if FacsFile.objects.filter(original_filename=filename,md5hash=md5hash):
            print 'Skipping ', filename
            continue

        #Open file, remove null bytes and prepare csv reader
        facs_file = file(filename, 'rU')
        csv_reader = csv.reader((x.replace('\0', '') for x in facs_file),dialect=csv.excel_tab)

        #Reader header
        csv_header = csv_reader.next()
        facs_file_results = []

        #Parse the file
        for csv_row in csv_reader:
            if csv_row[0]:
                facs_file_results.append(dict(zip(csv_header,csv_row)))

        #Close the file
        facs_file.close()

        #Save the information to database and archive file
        random_ints = ''.join([str(random.randint(0,9)) for n in range(10)])
        archive_filename = parser_settings['facs_archive_directory'] + filename.split('/')[-1][:-4].split('_')[0] + '_' + random_ints + '.exp'
        shutil.move(filename, archive_filename)

        facs_file = FacsFile(
            original_filename = filename,
            md5hash = md5hash,
            archive_filename = archive_filename,
            )
        facs_file.save()

        #Remove empty elements
        for result in facs_file_results:
            for key, data in result.items():
                if data == '.' or not(data):
                    del result[key]

        #Cache test code and interface mappings
        test_codes = []
        for testcode_mapping in TestCodeMapping.objects.filter(interface_name=parser_settings['testcode_interface_name']):
            test_code = testcode_mapping.code
            code = test_code.code
            code_mapping = testcode_mapping.code_mapping

            test_codes.append((code, code_mapping, test_code))

        #Add results to database
        for result in facs_file_results:

            #Parse result date
            result_date = dateutil.parser.parse(result[parser_settings['result_datetime']])
            result_error_code = getattr(result, parser_settings['error_codes'], '')
            result_identifier = result[parser_settings['sample_identifier']]
            result_cytometer = result[parser_settings['cytometer_serial']]

            #Create the dictionnary of result items.
            new_result_item_dict = {}
            for test_code, facs_file_column, test_code_object in test_codes:
                new_result_item_dict[test_code] = ResultItem(
                    test_code = test_code_object,
                    result_item_value = result[facs_file_column],
                    error_code = result_error_code,
                    result_item_datetime = result_date,
                    )

            #Search for possible duplicate result
            is_duplicate = False
            for possible_duplicate in FacsResult.objects.filter(result_identifier=result_identifier):
                if possible_duplicate.get_resultitem_dict() == new_result_item_dict:
                    is_duplicate = True
                    break

            #Save result and result item to data if it is not a duplicate
            if not is_duplicate:
                
                new_result = FacsResult(
                    result_identifier=result_identifier,
                    result_datetime=result_date,
                    origin_facs_file=facs_file,
                    cytometer_serial_number=result_cytometer,
                    )
                    
                new_result.save()
                
                #Add the reference to the result for each item and save it to database.
                for item in new_result_item_dict.values():
                    item.result = new_result
                    item.save()

                new_result.link_to_requisition()
