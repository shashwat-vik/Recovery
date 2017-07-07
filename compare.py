# Python 3.x
# EACH PLACE ID HAS INDEXES OF ROWS WHERE IT OCCURS AS DUPLICATE
# Saved as Python Dictionary : PID = {'place_id':[idx1, idx2,....]}

import csv, sys, json, os, glob
import place_search as ps

ID_UNIVERSE = set()
CLASS_COUNTS = {'A':0, 'B':0, 'C':0}

def read_csv(file_path, fields, rows):
    with open(file_path, 'r') as csvFile:
        reader = csv.DictReader(csvFile, dialect=csv.excel)
        if fields:
            reader.fieldnames.extend(fields)
            del fields[:]
        fields.extend(reader.fieldnames)
        rows.extend(reader)
    print('## FILE:', os.path.basename(file_path))

def write_csv(file_path, fields, rows):
    with open(file_path, 'w') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=fields, lineterminator='\n')
        writer.writerow(dict(zip(fields,fields)))
        for row in rows:
            writer.writerow(row)
    print('## FILE WRITTEN')

# String Clean and Convert to lowercase
def cln(x):
    return x.strip().lower()

# Filter name based on terminating_words.
def filter_name(name, terminating_words):
    for i in terminating_words:
        x = cln(name).find(cln(i))
        if x != -1:
            f_name = cln(name).split(cln(i))[0] + cln(i)
            return cln(f_name)
    return cln(name)

# hit_words are indicators for correct prediction.
# Unique for each row.
def check_hit_words(row, r_fa):
    cols = ['Street Address','VILLAGE_NAME','Locality','Pincode','City']
    for col in cols[:2]:
        x = cln(row[col])
        if x and x in cln(r_fa):
            return True, ('A', col, x)

    # BELOW MAY LEAD TO WIDE RANGE OF HITS
    # HENCE COMPARING ONLY IF ABOVE FAILS
    for col in cols[2:4]:
        x = cln(row[col])
        if x and x in cln(r_fa):
            return True, ('B', col, x)

    for col in cols[4:]:
        x = cln(row[col])
        if x and x in cln(r_fa):
            return True, ('C', col, x)

    return False, None

def analyze(row, address, classes, code1=True, show=False):
    global ID_UNIVERSE
    ascii = lambda x: x.encode('utf-8','ignore').decode('ascii','ignore')
    code, resp = ps.graceful_request(address)
    if code == 201:
        for cidx, cl in enumerate(classes):
            if show: print('ITERATION ',cidx+1)
            for ridx, result in enumerate(resp["results"]):
                if show: print('  ',ridx)
                r_fa = ascii(result["formatted_address"])
                h_flag, h_stat = check_hit_words(row, r_fa)
                if h_flag and h_stat[0] == cl:     # ITERATIONS WITH DECREASING CLASS QUALITY
                    if code1: row['h1_place_id'], row['h1_name'], row['h1_address'] = result["place_id"], result["name"], r_fa
                    if not code1: row['h2_place_id'], row['h2_name'], row['h2_address'] = result["place_id"], result["name"], r_fa

                    if code1: row['h1_category'], row['h1_col'], row['h1_word'] = h_stat[0], h_stat[1], h_stat[2]
                    if not code1: row['h2_category'], row['h2_col'], row['h2_word'] = h_stat[0], h_stat[1], h_stat[2]

                    if result["place_id"] not in ID_UNIVERSE:
                        CLASS_COUNTS[cl] += 1
                    ID_UNIVERSE.add(result["place_id"])

                    print("[{0}] || [{1}] || [{2}]".format(result["place_id"], result["name"], h_stat))
                    return True
    return False

def recover1(rows, terminating_words):
    classes = ['A', 'B', 'C']
    for idx, row in enumerate(rows):
        ##########
        f_name = filter_name(row['Name'], terminating_words)
        address_1 = f_name + ', ' + cln(row['State'])
        address_2 = f_name + ', ' + cln(row['City'])
        ##########
        found = False
        print('# %s :'%idx, row['Name'], '-->', address_1)
        print('# %s :'%idx, row['Name'], '-->', address_2)

        found = analyze(row, address_1, ['A'])                          # ADD_1, CLASS A
        if not found: found = analyze(row, address_2, ['A'])            # ADD_2, CLASS A
        if not found: found = analyze(row, address_2, ['A', 'B'])       # ADD_2, CLASS A, B
        if not found: found = analyze(row, address_1, ['A', 'B'])       # ADD_1, CLASS A, B
        if not found: found = analyze(row, address_2, ['A', 'B', 'C'])  # ADD_2, CLASS A, B, C
        if not found: found = analyze(row, address_1, ['A', 'B', 'C'])  # ADD_1, CLASS A, B, C
        print()

def recover2(rows, terminating_words):
    classes = ['A', 'B', 'C']
    for idx, row in enumerate(rows):
        ##########
        f_name = filter_name(row['Name'], terminating_words)
        address_1 = f_name + ', ' + cln(row['State'])
        address_2 = f_name + ', ' + cln(row['Locality'])
        ##########
        found = False
        print('# %s :'%idx, row['Name'], '-->', address_1)
        print('# %s :'%idx, row['Name'], '-->', address_2)

        found = analyze(row, address_1, ['A'])                          # ADD_1, CLASS A
        if not found: found = analyze(row, address_2, ['A'], False)            # ADD_2, CLASS A
        if not found: found = analyze(row, address_2, ['A', 'B'], False)       # ADD_2, CLASS A, B
        if not found: found = analyze(row, address_1, ['A', 'B'], False)       # ADD_1, CLASS A, B
        if not found: found = analyze(row, address_2, ['A', 'B', 'C'], False)  # ADD_2, CLASS A, B, C
        if not found: found = analyze(row, address_1, ['A', 'B', 'C'], False)  # ADD_1, CLASS A, B, C
        print()

# SHOULD BE IN PRIORITY ORDER
# KEEP SHORT ABBREVIATIONS AFTER ALL THE FULL NAMES OF ITS TYPE ARE ENSURED
terminating_words = ['HIGHSCHOOL', 'SCHOOL', 'SCH', 'COLLEGE', 'VIDYALAE', 'VIDYALAY', 'VIDYALAYA', 'VIDYAMANDIR', 'VID.',
'MANDIR', 'CONVENT', 'SHALA', 'NIKETAN', 'ACADEMY', 'SHIKSHALAYA', 'PATHSALA', 'VIDYAPITH', ',', '(']

if __name__ == '__main__':
    file_path = glob.glob('COMP_INPUT/*Maharashtra*.csv')[0]

    try:
        ps.update_file_name(os.path.basename(file_path))    # MANDATORY
        ps.CACHE_LOAD()                                     # MANDATORY

        ########################################
        fields, rows = ['STATUS','h1_place_id', 'h1_category', 'h1_col', 'h1_word', 'h1_name', 'h1_address', '', '', 'h2_place_id', 'h2_category', 'h2_col', 'h2_word', 'h2_name', 'h2_address'], []
        read_csv(file_path, fields, rows)
        rows = rows[:1000]
        recover1(rows, terminating_words)

        ID_UNIVERSE = set()
        CLASS_COUNTS = {'A':0, 'B':0, 'C':0}

        recover2(rows, terminating_words)

        for row in rows:
            if row['h1_place_id'] != row['h2_place_id']: row['STATUS'] = 'DIFFERENT'
            #else: row['STATUS'] = 'SAME'
        write_csv('COMP_OUTPUT/__'+os.path.basename(file_path), fields, rows)
        ########################################
    except KeyboardInterrupt:
        pass
    finally:
        print('\nTOTAL UNIQUE ID:', len(ID_UNIVERSE))
        print('CLASS COUNTS', CLASS_COUNTS)
        ps.CACHE_SAVE()     # MANDATORY
