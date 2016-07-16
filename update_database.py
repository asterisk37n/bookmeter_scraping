from amazon_api import AmazonAPI
from database import Database
from flaskapp import loadkey

db = Database()
db.connect(debug=True)
aws_access_id, aws_secret_key = loadkey('/home/ec2-user/.aws/credentials/rootkey.csv')
api = AmazonAPI(aws_access_id, aws_secret_key, 'asterisk37n-22')
show_isbns=[]
visible_books = []
query_isbns=[]
isbns = db.get_isbn_iter()
print(isbns)
for isbn in show_isbns:
    if db.isnew(isbn):
        visible_books.append(db.select_book_dict(isbn))
    else:
        query_isbns.append(isbn)
        if len(query_isbns) == 10:
            result = api.query_to_list_of_dicts(*query_isbns)
            visible_books.extend(result)
            db.insert_row(result)
            query_isbns=[]
        else:
              pass
else:
    if query_isbns:
        result = api.query_to_list_of_dicts(*query_isbns)
        visible_books.extend(result)
        db.insert_row(result)
db.commit()
db.close()

