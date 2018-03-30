from flask import Flask, Request, jsonify, request, make_response
import cloudconvert_api as f
import numpy as np
import pytesseract as pt
app = Flask(__name__)

@app.route("/picture", methods=['POST'])
def call():
    resp = request.files["fileToUpload"].read()
    ext = request.files["fileToUpload"].filename.split('.')[1]
    return make_response(distribute(resp), 200)

def distribute(resp):

    img = "imageToSave.pdf"
    with open(img, "wb") as fh:
        fh.write(resp)
    return main(img)

def splice(text_string):
    text_lst = text_string.split('\n')
    num = get_invoice_num(text_lst)
    total = get_purchase_total(text_lst)
    name = get_vendor_name(text_lst)

    return jsonify({"Invoice Number":num, "Purchases":total, "Vendor Name":name})


def get_invoice_num(text_lst):

     for item in text_lst:
        if 'inv' in item.lower():
            return item.replace('#', '').split(' ')[-1]
        else:
            pass


def get_doc_date(text):

    pass


def get_purchase_total(text_lst):
    lst = []
    for item in text_lst:
        try:
            if int(item[0]):
                lst.append(float(item.replace(',','')))
            else:
                lst.append(float(item.strip(item[0]).replace(',','')))
        except:
            if 'tot' in item.lower():
                lst_text = item.split(' ')
                for obj in lst_text:
                    try:
                        lst.append(float(obj.strip(obj[0]).replace(',','')))
                    except:
                        pass
    if max(lst) == None:
        raise AttributeError('Total Not Found')
    else:
        return max(lst)

def get_vendor_name(text_lst):
    name = ''
    for item in text_lst:
        if 'checks payable' in item.lower():
            name = item.split('to')[1]
        elif 'Thank' in item:
            for word in item.replace("Thank",'').split():
                if word[0].isupper() and len(word) > 4:
                    name += word.strip('.') + ' '
    if name == None:
        raise AttributeError('Name Not Found')
    else:
        return name.strip()

def conversion_call(doc):
    API_KEY = c.API_KEY
    api = cloudconvert.Api(API_KEY)
    # name, ext = filename.split('.')

    process = api.createProcess({
        "inputformat": 'pdf',
        "outputformat": "jpg"
    })

    process.start({
        "wait": 'true',
        "input": "Upload",
        "file": open(doc, 'rb'),
        "filename": doc,
        "outputformat": "jpg",
        "converteroptions": {
            "resize": "6000x9000"
        }
    })
    process.wait()
    pic = process.download(doc)

    return pic

def grab_info(pic= None):
    text = pt.image_to_string(Image.open('../OCR_test_imgs/Helium Photography.jpg'))
    #test case need to set to variable in Image.open arg
    respo = splice(text)
        # conn = ps.connect("dbname= development host=ocrdb.postgres.database.azure.com user=myadmin@ocrdb password=,.Dk39vW0sEJ")
    # curr = conn.cursor()
    # query = "INSERT INTO company VALUES (%s, %s, %s)", (num, total_purchase, name)
    # curr.execute(query)
    # CompanyID, DocumentType, vd_id, Purchase, Appr, Doc_dt = curr.fetchone()
    # pt.Output()
    return respo

def main(doc):
    # pic = conversion_call(doc)
    return grab_info()

# @app.route("/")
@app.route('/test', methods=['POST'])
def test_route():
    return 'kill'

@app.route('/')
def hello_world():
  return 'Hello, World!'

if __name__ == '__main__':
  app.run()
