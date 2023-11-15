from flask import Flask, render_template, request, jsonify
from views import views
from subprocess import check_output
import sys, io, threading, subprocess, re, platform, os, requests, time, speedtest, re
app = Flask(__name__)
app.register_blueprint(views, url_prefix = "/views")
#----------------------------------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')
#----------------------------------------------------------------------------------------------------
def speed_test(type="", size=0):
    t_datasize =""
    t_time = ""
    t_speed = ""
    if type == 'download':
       size = f"{size}MB"
       url = f"http://ipv4.download.thinkbroadband.com:8080/{size}.zip"
       with io.BytesIO() as f:
            start = time.perf_counter()
            r = requests.get(url, stream=True)
            total_length = r.headers.get('content-length')
            dl = 0
            if total_length is None:
                f.write("")
            else:
                for chunk in r.iter_content(1024):
                    dl += len(chunk)
                    done = int(30 * dl / int(total_length))
       t_datasize =   f"\n{size}"
       t_time = f"\n{(time.perf_counter() - start):.2f} seconds"
       t_speed = dl//(time.perf_counter() - start) / 100000
    elif type == 'upload':
        file_name = f"{size}MB.png"
        nullFile = os.devnull
        file_stats = os.stat(file_name)
        with open(nullFile, "wb") as f:
                start = time.perf_counter()
                r = requests.post('https://httpbin.org/post', files={'file': open(file_name, 'rb')})
                if r.ok:
                   total_length = r.headers.get('content-length')
                   dl = 0
                   for chunk in r.iter_content(1024):
                        dl += len(chunk)
                        done = int(30 * dl / int(total_length))             
                        t_datasize =f"\n{size}MB"
                        t_time = f"\n{(time.perf_counter() - start):.2f} seconds"
                        t_speed = dl//(time.perf_counter() - start) / 100000
                else:
                        t_datasize ="Please Upload again !"
                        t_speed="Please Upload again ! "
                        t_speed="0"
    else:
        t_datasize ="unknown operation"
        t_speed="unknown operation"
        t_speed="0"
        raise
    return t_time,  t_speed, t_datasize 
#----------------------------------------------------------------------------------------------------
def measure_ping_speed(host):
 try:
     command = "-n 4" if platform.system().lower() == "windows" else "-c 4"
     response = subprocess.Popen(f"ping {command} {host}", stdout=subprocess.PIPE,  universal_newlines=True, encoding="utf-8").communicate()[0]
     response = response.split('\n')
     return response[1] + "\n",response[2] + "\n"
 except subprocess.CalledProcessError:
    pass
    return None,None
#****************************************************************************************************   
@app.route('/measure', methods=['POST'])
def measure():
    if request.method == 'POST':
        download_datasize = ""
        download_datatime = ""
        download_speed = ""
        upload_datasize = ""
        upload_datatime = ""
        upload_speed = ""
        #------------------------------------------
        t_download_time,  t_download_speed, t_download_datasize = speed_test("download", 5) 
        download_datasize = t_download_datasize
        download_datatime = t_download_time
        download_speed = t_download_speed 
        #------------------------------------------
        t_upload_time,  t_upload_speed, t_upload_datasize = speed_test("upload", 5) 
        upload_datasize = t_upload_datasize
        upload_datatime = t_upload_time
        upload_speed = t_upload_speed 
         #------------------------------------------
         #Speed ​​Test Result uses Speedtest component - Begin
        st = speedtest.Speedtest()
        servers = st.get_best_server()
        download_speedtest = ""
        upload_speedtest = ""
        download_speedtest = st.download() / 1000000  # Convert to Mbps
        upload_speedtest = st.upload() / 1000000  # Convert to Mbps
        country_speedtest=servers['country']
        name_speedtest= servers['name']
        sponsor_speedtest=servers['sponsor']
        host_speedtest=servers['host']
        #Speed ​​Test Result uses Speedtest component - End
         #------------------------------------------
        ping_speed,ping_result = measure_ping_speed("www.verizon.com")#Frankfurt
        if ping_speed is not None:
            ping_Command = f"{ping_speed}"   
        else:
            ping_Command = "-1"
        #------------------------------------------
    return render_template('measure.html',  
           download_datatime=download_datatime, download_datasize=download_datasize, download_speed=download_speed, 
           upload_datatime=upload_datatime, upload_speed=upload_speed,upload_datasize=upload_datasize ,
           download_speedtest=download_speedtest, upload_speedtest=upload_speedtest,
           country_speedtest=country_speedtest, name_speedtest=name_speedtest, sponsor_speedtest=sponsor_speedtest, host_speedtest=host_speedtest,
           ping_Command=ping_Command,ping_result=ping_result)
#****************************************************************************************************   
@app.route('/ping')
def ping():
    return 'Pong'
#****************************************************************************************************   
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'Dosya bulunamadı.'

    file = request.files['file']

    if file.filename == '':
        return 'Dosya adı boş.'

    file.save('uploads/' + file.filename)
    return 'Dosya başarıyla yüklendi: ' + file.filename
#****************************************************************************************************   
if __name__ == '__main__':
    app.run(debug=True, port=8000)
#----------------------------------------------------------------------------------------------------
