import csv, os, glob

def read_csv(file_path,fields,rows):
    with open(file_path, 'r') as csvFile:
        reader = csv.DictReader(csvFile, dialect=csv.excel)
        fields.extend(reader.fieldnames)
        rows.extend(reader)
    print('## FILE :',os.path.basename(file_path))

def write_csv(file_path,fields,rows):
    keys = list(rows[0].keys())
    N = len(rows)
    for i in range(N):
        for key in keys:
            if key not in fields:
                rows[i].pop(key)

    with open(file_path, 'w') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=fields, lineterminator='\n')
        writer.writerow(dict(zip(fields,fields)))
        for row in rows:
            writer.writerow(row)
    print('## FILE WRITTEN')

req_fields = ['City','SCHOOL_CODE','AC_YEAR','Name','Locality','Street Address','VILLAGE_NAME','State','Pincode']

if __name__ == '__main__':
    file_paths = glob.glob('input/*Karnat*.csv')
    for file_path in file_paths:
        fields, rows = [], []
        read_csv(file_path, fields, rows)
        #get_duplicates(rows)
        #print(len(rows))
        write_csv(file_path, req_fields, rows)
