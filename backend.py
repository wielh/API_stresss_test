from os import listdir
import os, random ,json, datetime
from threading import Thread,Lock
import requests

safe_print_lock = Lock()
def safe_print(*a, **b):
    """Thread safe print function"""
    with safe_print_lock:
        print(*a, **b)

class stress_test_leader_thread(Thread):
    def __init__(self,parameters:dict):
        Thread.__init__(self) 
        self.parameter = parameters
        self.current_num = 0 
        self.request_num = parameters.get("request_num",100)
        self.thread_num = parameters.get("thread_num",1)
        self.output_folder = parameters.get("output_folder",1)
        self.thread_list = []
  
    def self_current_number_plus1(self):
        lock = Lock()
        lock.acquire()
        self.current_num +=1
        answer = self.current_num-1
        lock.release()
        return answer

    def edit_status_record(self,status_code:int,req_number:int):
        lock = Lock()
        lock.acquire()
        if status_code in self.status_record.keys():
            self.status_record[status_code].append(req_number)
        else:
            self.status_record[status_code]=[]
            self.status_record[status_code].append(req_number)
        lock.release()

    def run(self):
        # create thread and execute
        self.thread_list.clear()
        self.status_record={}     
        start_time = datetime.datetime.now()
        start_time_str = start_time.strftime("%Y/%m/%d, %H:%M:%S.%f")[:-3]
        print(f"start_time:{start_time_str}")

        for i in range(self.thread_num):     
            self.thread_list.append(
                stress_test_thread(
                    main_thread=self,
                    parameters=self.parameter,
                    thread_index=i,
                    max_request_num=self.request_num
                )
            )

        for thread in self.thread_list:
            thread.start()

        for thread in self.thread_list:
            thread.join()

        # After finishing test, write status record to log.txt
        # ==========================================================
        logfile = open(os.path.join(self.output_folder,"log.txt"),mode="w") 
        for status in self.status_record.keys():
            logfile.write("status:"+str(status)+":"+
                str(len(self.status_record[status]))+"times\n")
            tmp_str=""
            for index in self.status_record[status]:
                tmp_str+=str(index)+","
                if len(tmp_str)>100:
                    logfile.write(tmp_str+"\n")
                    tmp_str=""
            if not tmp_str=="":
                logfile.write(tmp_str+"\n")
                tmp_str=""
            logfile.write("\n")

        end_time = datetime.datetime.now()
        end_time_str=end_time.strftime("%Y/%m/%d, %H:%M:%S.%f")[:-3]
        time_difference = end_time-start_time       
        safe_print(f"end_time:{end_time_str}")
        #time_string = f"time cost:{str(hour)} h {str(minute)} m {str(total_second)} s"
        time_string = f"time cost: {str(time_difference)}"
        safe_print(time_string) 
        logfile.write(time_string+"\n")
        logfile.flush()
        logfile.close()

class stress_test_thread(Thread):
 
    def __init__(self, main_thread:stress_test_leader_thread,
        parameters:dict, thread_index:int, max_request_num:int):
        Thread.__init__(self)    
        self.daemon = True
        self.main_thread = main_thread
        self.thread_index = thread_index
        self.method = parameters.get("method","POST")
        self.mimetype = parameters.get("mimetype","")
        self.url = parameters.get("url","")
        self.output_folder = parameters.get("output_folder","")
        self.current_num = 0
        self.max_request_num = max_request_num

        # take variable before run 
        if self.mimetype == 'args':
            self.urlencoded_folder = parameters.get("urlencoded_folder","")
            self.urlencoded_filelist = []
            for f in os.listdir(self.urlencoded_folder):
                filename = os.path.join(self.urlencoded_folder, f)
                if os.path.isfile(filename) and\
                len(os.path.splitext(filename))>1 and\
                os.path.splitext(f)[1]=='.txt':
                    self.urlencoded_filelist.append(filename)
            #=================================================
        elif self.mimetype =='urlencoded':  
            self.urlencoded_folder = parameters.get("urlencoded_folder","") 
            self.urlencoded_filelist = []
            for f in os.listdir(self.urlencoded_folder):
                filename = os.path.join(self.urlencoded_folder, f)
                if os.path.isfile(filename) and\
                len(os.path.splitext(filename))>1 and\
                os.path.splitext(f)[1]=='.txt':
                    self.urlencoded_filelist.append(filename)        
            #=================================================       
        elif self.mimetype == 'json':
            self.json_folder = parameters.get("json_folder","")
            self.json_filelist = []
            for f in os.listdir(self.json_folder):
                filename = os.path.join(self.json_folder, f)
                if os.path.isfile(filename) and\
                len(os.path.splitext(filename))>1 and\
                os.path.splitext(f)[1]=='.json':
                    self.json_filelist.append(filename)
            #=================================================   
        elif self.mimetype == 'form':           
            self.file_list = {}
            self.urlencoded_filelist = []
            for key in parameters.get("form_data","").keys():
                folder = parameters.get("form_data","")[key]
                filelist = []
                if key == 'data':
                    self.urlencoded_folder = folder 
                    for f in os.listdir(self.urlencoded_folder):
                        filename = os.path.join(self.urlencoded_folder, f)
                        if os.path.isfile(filename) and\
                        len(os.path.splitext(filename))>1 and\
                        os.path.splitext(f)[1]=='.txt':
                            self.urlencoded_filelist.append(filename)  
                elif os.path.isdir(folder):
                    for f in listdir(folder):
                        filename = os.path.join(folder,f)
                        if os.path.isfile(filename):
                            filelist.append(filename)
                    self.file_list[key] = filelist
                else:
                    self.file_list[key] = []

    def run(self):
        while True:
            self.current_num = self.main_thread.self_current_number_plus1() 
            if self.current_num < self.max_request_num:  
                try:
                    self.init_variables()
                    self.generate_new_request()  
                    self.send_request()
                    self.get_result()
                except Exception as ex:
                    safe_print(ex)  
            else:
                break

    def init_variables(self):
        self.random_urlencoded_filename = ""
        self.random_file_content = {}
        self.random_json_filename = ""
        self.random_jsonobj = None
        self.random_filelist = {}
        self.random_file = {}

    def generate_urlencoded(self):    
        if len(self.urlencoded_filelist)>0:
            self.random_urlencoded_filename =\
                random.choice(self.urlencoded_filelist)
            random_urlencoded_file = open(
                self.random_urlencoded_filename, mode="r")
            all_content = random_urlencoded_file.read()
            random_urlencoded_file.flush()
            random_urlencoded_file.close()
            #TODO variable type
            for line in all_content.split("\n"):
                if len(line.split("="))>1:
                    name = line.split("=",maxsplit=2)[0]
                    value = line.split("=",maxsplit=2)[1]
                    if name.endswith('[]'):
                        values = value.split(",")
                        self.random_file_content[name[:-2]] = values
                    else:
                        self.random_file_content[name]=value

    #TODO all variable type
    def generate_json(self):         
        if len(self.json_filelist)>0:
            self.random_json_filename = random.choice(self.json_filelist)       
            try:     
                random_json_file = open(self.random_json_filename,mode="r")
                self.random_jsonobj = json.loads(random_json_file.read())
            except:
                self.random_jsonobj = None
            random_json_file.flush()
            random_json_file.close()
           
    def generate_file_dict(self):   
        self.generate_urlencoded()   
        for key in self.file_list:     
            if len(self.file_list[key])>0:
                random_file = random.choice(self.file_list[key])
                self.random_filelist[key] = random_file
                f = open(random_file,mode="rb")
                self.random_file[key] = f.read()
                f.close()
                 
    def generate_new_request(self):
        if self.mimetype =='args':        
            self.generate_urlencoded()
        elif self.mimetype =='urlencoded':        
            self.generate_urlencoded()
        elif self.mimetype == 'json':
            self.generate_json()
        elif self.mimetype == 'form':
            self.generate_file_dict()
    #=========================================================
    def send_request(self):
        if self.method == 'GET':
            new_url = self.url
            if len(self.random_file_content.keys())>0:
                new_url = new_url+"?"
                for key in self.random_file_content.keys():
                    new_url+=key
                    new_url+="="
                    new_url+=self.random_file_content[key]
                    new_url+="&"
                new_url=new_url[:-1]         
            self.resp = requests.get(url= new_url, timeout=60)
        elif self.method == 'POST':     
            self.resp = requests.post(url= self.url, files=self.random_file,\
                json= self.random_jsonobj, data=self.random_file_content, timeout=60)  
            #self.resp = requests.post(url= self.url, timeout=60)               
        else:     
            safe_print("Use default method POST.")
            self.resp = requests.post(url= self.url, 
                files=self.random_file,json= self.random_jsonobj, 
                data=self.random_file_content,timeout=60)
  
    def get_result(self)-> None: 
        path = os.path.join(self.output_folder , str(self.current_num))
        if not os.path.exists(path):
            os.makedirs(path)
    
        summary_path = os.path.join(path,"summary.txt")
        summary_path_file = open(summary_path, "w") 

        info = "request number:"+str(self.current_num)
        self.write_log_and_print(summary_path_file,info)
      
        if not self.random_urlencoded_filename == '':
            info = "choose urlencoded file:"+ self.random_urlencoded_filename
            self.write_log_and_print(summary_path_file,info)

        if not self.random_json_filename == '':
            info = "choose json file:"+self.random_json_filename
            self.write_log_and_print(summary_path_file,info)
       
        if not self.random_filelist is None and len(self.random_filelist.keys())>0:   
            info = "choose filelist:"
            self.write_log_and_print(summary_path_file,info)                 
            for key in self.random_filelist.keys():
                if type(self.random_filelist.get(key,"")).__name__=="str":
                    info = "  " +str(key)+":"+self.random_filelist.get(key,"")
                    self.write_log_and_print(summary_path_file,info)
                else:
                    info = type(self.random_filelist.get(key,"")).__name__
                    self.write_log_and_print(summary_path_file,info)

        info = "status_code:"+str(self.resp.status_code)
        self.write_log_and_print(summary_path_file,info)   
         
        self.main_thread.edit_status_record(
            status_code = self.resp.status_code,
            req_number = self.current_num
        )
          
        info = "reason:"+ self.resp.reason
        self.write_log_and_print(summary_path_file,info)
    
        output_headers = self.resp.headers.__dict__
        if output_headers is None:
            info = "header:"
        else:
            info = "header:"+output_headers.__str__()
        self.write_log_and_print(summary_path_file,info)
              
        '''TODO
        info = "cookies:"
        self.write_log_and_print(summary_path_file,info)

        for key in self.resp.cookies.keys():
            info = str(key)+":"+str(self.resp.cookies.get(key,default=''))
            self.write_log_and_print(summary_path_file,info)
        '''
        
        summary_path_file.flush()
        summary_path_file.close()
        #=========================================================   
        name = output_headers.get("Content-Disposition","")
        array = name.split("filename=")
        if len(array)>=2:
            name = name.split("filename=")[1]
            name = name[1:-1]
        else:
            name = "file"

        file_path = os.path.join(path,name)            
        file = open(file_path, "wb") 
        file.write(self.resp.content)   
        file.flush()
        file.close()    
        self.resp.close()
        
    def write_log_and_print(self,summary_path_file,info:str):
        summary_path_file.write(f"(Thread {str(self.thread_index)}):"+info+"\n")
        safe_print(f"(Thread {str(self.thread_index)}):"+info)

