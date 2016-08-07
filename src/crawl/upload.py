## this script upload the fbo info to the local database 
def clean_string(src):
    return src.replace("'", "\\'")

import MySQLdb
# connect to database
db = MySQLdb.connect(host='127.0.0.1',
                     user='anoia7_sugarhill',
                     passwd='ur28teme',
                     db='anoia7_sugarhill',)
cursor = db.cursor()

count = 0 
# load the data from the tsv file
for line in open('FBOData.2013-11-02.txt'):
    print count 
    count += 1
    split_line = line.split('\t')
    sol_num = split_line[0]
    title = split_line[1]
    agency_name = split_line[2]
    due_date = split_line[3]
    class_code = split_line[4]
    naics_codes = split_line[5].split(' ')
    place_of_performance = split_line[6]
    point_of_contact = split_line[7]
    contract_office = split_line[8]
    state = split_line[9]
    status = split_line[10]
    notice_type = split_line[11]
    source_url = split_line[12] 
    desc_base64 = split_line[13]
    
    # get the naics code ID from the NaicsCode table
    naics_code_ids = [1, 1]
    index = 0
    for naics_code in naics_codes:
        if len(naics_code.strip()) == 0:
            continue

        cursor.execute("SELECT id FROM sugarhill_v1_naicscode WHERE code = '%s'" % naics_code)
        row = cursor.fetchone()
        if row is None:
            raise Exception('naics_code %s is unkonwn' % naics_code)
        naics_code_ids[index] = row[0]
        index += 1
        ##print 'naics code %s, id: %s' % (naics_code, row[0])

    # get the state code ID from the State table
    state_id = 1
    if len(state.strip()) > 0:
        cursor.execute("SELECT id FROM sugarhill_v1_state WHERE name = '%s'" % state)
        row = cursor.fetchone()
        if row is None:
            raise Exception('state %s is unkonwn' % state)
        state_id = row[0]
        ##print 'statee %s, id: %s' % (state, row[0])

    # get the status from the Status table
    status_id = [1, 1, 1]
    index = 0
    if len(status.strip()) > 0:
        cursor.execute("SELECT id FROM sugarhill_v1_status WHERE title = '%s'" % status)
        row = cursor.fetchone()
        if row is not None:
            # status is not N/A
            status_id[index] = row[0]
            index += 1
        ##print 'status %s, id: %s' % (status, row[0])

    # insert the data into the project table
    insert_sql = "INSERT INTO sugarhill_v1_projectb(solicitation_num,title,agency,due_date,class_codes, \
                 naics_code1_id,naics_code2_id,place_of_performance,point_of_contact,contract_office, \
                 state_id,status1_id,status2_id,status3_id,notice_type,source_url,description) \
                 VALUES ('%s', '%s', '%s', '%s', '%s', %d, %d, '%s', '%s', '%s',%d, %d, %d, %d, '%s', '%s', '%s')" % \
        (sol_num, clean_string(title), clean_string(agency_name), due_date, class_code, naics_code_ids[0], naics_code_ids[1], \
             clean_string(place_of_performance), clean_string(point_of_contact), clean_string(contract_office), state_id, status_id[0], status_id[1], status_id[2], \
             notice_type, source_url, desc_base64)

    try:
        # Execute the SQL command
        cursor.execute(insert_sql)
        # Commit your changes in the database
        db.commit()
        print 'succeeded'
    except:
        print insert_sql
        print 'failed'
        # Rollback in case there is any error
        db.rollback()
        break

# close connections
cursor.close()
db.close()


