import psycopg2
import sys
import os

# Script is expecting host and password as environment variables.
# Store the host and password for dev, stage, and prod as:
# Dev: FECDB_HOST_DEV, FECDB_PW_DEV
# Stage: FECDB_HOST_STAGE, FECDB_PW_STAGE
# Prod: FECDB_HOST_PROD, FECDB_PW_PROD
# Script is expecting target database (dev, stage, prod) as an argument

host = os.environ['FECDB_HOST_{}'.format(sys.argv[1].upper())]
password = os.environ['FECDB_PW_{}'.format(sys.argv[1].upper())]

print("Looking for ao_docs folder...")
if os.path.isdir('ao_docs'):
    print("Found it!")
else:
    print("Not found. Creating folder...")
    os.mkdir("ao_docs")
    print("Folder created.")

print("connecting to {} db...".format(sys.argv[1]))
fecdb = psycopg2.connect(database='fec',
                        user='fec',
                        password=password,
                        host=host,
                        port='5432')
print("connected!")

cursor = fecdb.cursor()
cursor.execute("select count(*) from document;")
docrows = cursor.fetchone()

print("There are {} documents to save.".format(str(docrows[0])))

print("Querying...")
cursor.execute("select document_id, fileimage from document;")

print("Fetching and saving files...")
for doc in cursor.fetchall(): 
    (document_id, fileimage) = doc
    filename = str(document_id)+".pdf"

    print("Saving {}...".format(filename))
    with open("ao_docs/{}".format(filename), 'wb') as f:
        f.write(fileimage)
    print("done!")
print("All files saved.")

fecdb.close()