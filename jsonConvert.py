from db_interface import DB_Interface

import json
import datetime

class DB_Converter(DB_Interface):
    def __init__(self):
        DB_Interface.__init__(self)
        self.converted = []
        self.batch = []
        self.batch_size = 100

    def proc(self):        
        # Get relevant data.
        self.session.execute(f"select urls.id, urlDate, urlType, username from urls inner join deviants on urls.deviant_id = deviants.id where urls.hasBeenExtracted = false limit {self.batch_size};")

        # Process stuff.

        result_list = self.session.fetchall()
        
        for row in result_list:
            print(f"Updating url id: {row[0]}")
            self.session.execute(f"update urls set hasBeenExtracted = true where urls.id = {row[0]};")
            self.db_connection.commit()
            
            dd = dict(zip(("time", "SubmissionType", "Submitter", "Submissions"),
                           (conv_stamp(row[1]), row[2], row[3], 1)))
            self.converted.append(dd)

        # Return a list of data dictionaries.
        return self.converted

def conv_stamp(stamp):
    ''' Convert timestamp to iso compliant timestamp '''
    stamp_str = stamp.strftime('%Y-%m-%d') + "T00:00:00Z"
    return (stamp_str)
    
def main():
    db = DB_Converter()
    data = db.proc()

    ingestFd = open("./ingest/ingest.0.json", "a+")

    for entry in data:
        json.dump(entry, ingestFd)

if __name__ == "__main__":
    main()

    # select urlDate, urlType, username from urls inner join deviants on urls.deviant_id = deviants.id;
