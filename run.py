import os, zipfile, glob
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename

UPLOAD_FOLDER = '/home/ubuntu/converter/tmp/'
ALLOWED_EXTENSIONS = set(['zip'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/download")
def download():
    print "redirect"
    return "<a href="+url_for('static', filename='output.zip')+">download</a>"

@app.route("/convert")
def convert(filename):
    print "CONVERTING"
    zip_ref = zipfile.ZipFile(UPLOAD_FOLDER+filename, 'r')
    zip_ref.extractall(UPLOAD_FOLDER+filename.split('.')[0])
    zip_ref.close()
    os.system("mkdir "+UPLOAD_FOLDER+"output/")
    os.system("ufraw-batch --out-type jpg --out-path="+UPLOAD_FOLDER+"/output/ "+UPLOAD_FOLDER+"/"+filename.split('.')[0]+"/*.CR2")
    out = zipfile.ZipFile("/home/ubuntu/converter/static/output.zip", "w")
    for name in glob.glob("/home/ubuntu/converter/tmp/output/*"):
        out.write(name, os.path.basename(name), zipfile.ZIP_DEFLATED)
    out.close()
    print "Done"
    os.system("rm -rf "+UPLOAD_FOLDER+"/*")
    return redirect(url_for('download')) 

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return convert(filename)
    return """
    <!doctype html>
    <title>Convert CR2 to JPG</title>
    <h1>Convert CR2 to JPG</h1>
    <h4>Upload Zip File</h4>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    """

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
