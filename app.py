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
            vechile_number, len_of_vechile_number=no_plate_and_ocr_finder(filename)
            print(vechile_number)
            if vechile_number=="No vechile Plate Found":
                print("No vechile Plate Found")
                return  render_template('output.html',error="No vechile Plate Found")
            else:
                vechile_clean_number=cleaning_vechile_number(vechile_number,len_of_vechile_number)
                print(vechile_clean_number)
                vechile_details=Vechile_info_finder(vechile_clean_number)
                if vechile_details=="No Info Found":
                    return render_template('output.html',vechile_number_show=vechile_clean_number,error="No Info Found")
                else:
                    try:
                        Description=vechile_details['Description']
                    except:
                        Description=""
                    try:
                        RegistrationYear=vechile_details['RegistrationYear']
                    except:
                        RegistrationYear=""
                    try:
                        CarMake=vechile_details['CarMake']['CurrentTextValue']
                    except:
                        CarMake=""
                    try:
                        CarModel=vechile_details['CarModel']['CurrentTextValue']
                    except:
                        CarModel=""
                    try:
                        MakeDescription=vechile_details['MakeDescription']['CurrentTextValue']
                    except:
                        MakeDescription=""
                    try:
                        FuelType=vechile_details['FuelType']['CurrentTextValue']
                    except:
                        FuelType=""
                    try:
                        Owner=vechile_details['Owner']
                    except:
                        Owner="Null"
                     
                    try:
                        VehicleType=vechile_details['VehicleType']
                    except:
                        VehicleType="UnKnown"
                    try:
                        Location=vechile_details['Location']
                    except:
                        Location=""
                    try:
                        ImageUrl=vechile_details['ImageUrl']
                    except:
                        ImageUrl=""
                    
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
     #print(type(plate))
      
     try: #here used try cache so that if no no_plate found then below statement can not give error,
         #tried to use if else instead of try catche but it was giving error...
        x1=plate[0][0]
        y1=plate[0][1]
        x2=x1+plate[0][2]
        y2=y1+plate[0][3]
        no_plate=test_car[y1:y2,x1:x2] 
        tess.pytesseract.tesseract_cmd= (r"C:Program Files\Tesseract-OCR\tesseract")
        text=tess.image_to_string(no_plate)
        #print(text)
        print(len(text))
        return (text,len(text))
     except:
         return "No vechile Plate Found"
      

def cleaning_vechile_number(text ,len_of_vechile_number):
    i=0
    final_no_plate=[]
    while i<len_of_vechile_number:
        if text[i]=="A" or text[i]=="B" or text[i]=="C"or text[i]=="D"or text[i]=="E"or text[i]=="F"or text[i]=="G"or text[i]=="H" or text[i]=="I"or text[i]=="J"or text[i]=="K"or text[i]=="L"or text[i]=="M" or text[i]=="N"or text[i]=="O"or text[i]=="P"or text[i]=="Q"or text[i]=="R"or text[i]=="S"or text[i]=="T"or text[i]=="U"or text[i]=="V"or text[i]=="W" or text[i]=="X" or text[i]=="Y" or text[i]=="Z" :
            final_no_plate.append(text[i])
            #print(text[i])
            
        elif text[i]=="1" or text[i]=="2" or text[i]=="3"or text[i]=="4"or text[i]=="5"or text[i]=="6"or text[i]=="7"or text[i]=="8" or text[i]=="9"or text[i]=="0":
            final_no_plate.append(text[i])
        i=i+1
    #print(final_no_plate)
         
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
    try:
        #print("info finder")
        r = requests.get("http://www.regcheck.org.uk/api/reg.asmx/CheckIndia?RegistrationNumber={0}&username=sudhanshu122222".format(str(plate_number)))
        data = xmltodict.parse(r.content)
        jdata = json.dumps(data)
        df = json.loads(jdata)
        df1 = json.loads(df['Vehicle']['vehicleJson'])
        print(df1)
        return df1
    except:
        return "No Info Found"

 
if __name__ == 'webapp1':
    app.debug = True
    app.run(debug=True)
