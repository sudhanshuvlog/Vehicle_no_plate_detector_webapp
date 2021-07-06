from flask import Flask , render_template, flash, request, redirect, url_for,session
import os
import cv2
import pytesseract as tess
#tess.pytesseract.tesseract_cmd= (r"C:Program Files\Tesseract-OCR\tesseract") #install the tesseract.exe first
from PIL import Image
import requests
import xmltodict
import json
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = 'images'
app=Flask("webapp1",static_url_path='/static')
app.secret_key = "1234"#DOne this beacause an error was apperaring about not having a key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
no_plate_detction="haarcascade_russian_plate_number.xml" #this is the train model of harscascade to detect no_plate 
 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def home_page():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'car_image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['car_image']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            print("Image saved!!")
            print(file.filename)
            filename = secure_filename(file.filename)
            filename="car.jpg" #doing this so that everytime their will be same name of file otherwise user's given file name will came
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #text=no_plate_finder()
    return render_template('index.html')           

@app.route('/output', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'car_image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['car_image']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            print("Image saved!!")
            print(file.filename)
            filename = secure_filename(file.filename)
            file_extension=file_extension_finder(filename)
            #print(file_extension)
            filename="car."+file_extension #doing this so that everytime their will be same name of file otherwise user's given file name will came
            #print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            vechile_number=no_plate_and_ocr_finder(filename)
            print(vechile_number)
            if vechile_number=="No vechile Plate Found":
                print("No vechile Plate Found")
                return  render_template('output.html',error="No vechile Plate Found")
            else:
                vechile_clean_number=cleaning_vechile_number(vechile_number)
                #print(vechile_clean_number)
                vechile_details=Vechile_info_finder(vechile_clean_number)
                '''vechile_details={'Description': 'HERO HONDA PASSION PRO CAST - DISC BRAKE- ELECTRIC START',
                'RegistrationYear': '2010',
                'CarMake': {'CurrentTextValue': 'HERO HONDA'},
                'CarModel': {'CurrentTextValue': 'PASSION PRO'},
                'Variant': 'CAST - DISC BRAKE- ELECTRIC START',
                'EngineSize': {'CurrentTextValue': '100'},
                'MakeDescription': {'CurrentTextValue': 'HERO HONDA'},
                'ModelDescription': {'CurrentTextValue': 'PASSION PRO'},
                'NumberOfSeats': {'CurrentTextValue': '2'},
                'VechileIdentificationNumber': 'MBLHA10AHAGM03219',
                'EngineNumber': '03110',
                'FuelType': {'CurrentTextValue': 'Petrol'},
                'RegistrationDate': '18/12/2010',
                'Owner': '',
                'Fitness': '',
                'Insurance': '',
                'PUCC': '',
                'VehicleType': 'M-CYCLE/SCOOTER(2WN)',
                'Location': 'RTO, ALLAHABAD',
                'ImageUrl': 'http://www.carregistrationapi.in/image.aspx/@SEVSTyBIT05EQSBQQVNTSU9OIFBSTyBDQVNUIC0gRElTQyBCUkFLRS0gRUxFQ1RSSUMgU1RBUlQ='}
                '''
                Description=vechile_details['Description']
                RegistrationYear=vechile_details['RegistrationYear']
                CarMake=vechile_details['CarMake']['CurrentTextValue']
                CarModel=vechile_details['CarModel']['CurrentTextValue']
                MakeDescription=vechile_details['MakeDescription']['CurrentTextValue']
                FuelType=vechile_details['FuelType']['CurrentTextValue']
                Owner=vechile_details['Owner']
                VehicleType=vechile_details['VehicleType']
                Location=vechile_details['Location']
                ImageUrl=vechile_details['ImageUrl']
                 
                return render_template('output.html',vechile_number_show=vechile_clean_number,vechile_details_show=vechile_details,
                Description_show=Description,RegistrationYear_show=RegistrationYear,CarMake_show=CarMake,CarModel_show=CarModel,
                MakeDescription_show=MakeDescription,FuelType_show=FuelType,Owner_show=Owner,VehicleType_show=VehicleType,ImageUrl_show=ImageUrl,
                Location_show=Location)
                 

    #return """{{car_number}}"""

def file_extension_finder(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower()

def no_plate_and_ocr_finder(filename): 
     print("aya") 
     no_plate_detction="haarcascade_russian_plate_number.xml"
     model=cv2.CascadeClassifier(no_plate_detction)
     print(filename)
     file_location='images/'+filename
     test_car=cv2.imread(file_location)
     #print(test_car)
     plate=model.detectMultiScale(test_car)
     print(plate)
     print(type(plate))
      
     try: #here used try cache so that if no no_plate found then below statement can not give error,
         #tried to use if else instead of try catche but it was giving error...
        x1=plate[0][0]
        y1=plate[0][1]
        x2=x1+plate[0][2]
        y2=y1+plate[0][3]
        no_plate=test_car[y1:y2,x1:x2] 
        tess.pytesseract.tesseract_cmd= (r"C:Program Files\Tesseract-OCR\tesseract")
        text=tess.image_to_string(no_plate)
        print(text)
        return text
     except:
         return "No vechile Plate Found"
      

def cleaning_vechile_number(text):
    i=0
    final_no_plate=[]
    while i<20:
        try:
            if text[i]=="|" or text[i]=="-" or text[i]=="," or text[i]=="" or text[i]==" " or  text[i]==")" or text[i]=="(" :
                #print("hatao isko")
                #print(text[i])
                pass
            else:
                if text[i]=="\n":
                    break
                else:
                    final_no_plate.append(text[i])
        except:
            break
        i=i+1
    def listToString(s): 
    
        # initialize an empty string
        str1 = "" 
            
        # traverse in the string  
        for ele in s: 
            str1 = str1+ele  

        # return string  
        return str1 
    return(listToString(final_no_plate)) 

def Vechile_info_finder(plate_number):
    r = requests.get("http://www.regcheck.org.uk/api/reg.asmx/CheckIndia?RegistrationNumber={0}&username=sudhanshu12222".format(str(plate_number)))
    data = xmltodict.parse(r.content)
    jdata = json.dumps(data)
    df = json.loads(jdata)
    df1 = json.loads(df['Vehicle']['vehicleJson'])
    #print(df1)
    return df1

 
if __name__ == 'webapp1':
    app.debug = True
    app.run(debug=True)
