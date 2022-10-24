'''
使用post發送資料回後端的時候，有以下四種常見的資料格式:
1.application/x-www-form-urlencoded
瀏覽器的原生<form>表單，如果不設置mimetype，那麼最終就會以
application/x-www-form-urlencoded方式提交數據。這是以編碼為URL參數的表單數據。
2.multipart/form-data
使用表單上傳文件時，必須讓<form>表單的encype等於multipart/form-data。
3.application/json
'''

import sys

if len(sys.argv)==1:
    from UI.MainUI import UI
    ui=UI()
    ui.mainloop()
elif sys.argv[1]=="--help": 
    # TODO
    print("The task of this program is to send many request to API")
    print("")
    print("Part1: arguments")
    print("The following parameter are as follow:")
    print("--get: use GET method")
    print("--post: use POST method")
    print("--mimetype \{type\}: The datatype of request")
    print("If you choose --get,then type option=\{none,args\}")
    print("none: No parameters")
    print("args: key_value pair on url")
    print("If you choose --post,then type option=\{none,urlencoded,json,form\}")
    print("none: No parameters")
    print("urlencoded: key_value pair in request body")
    print("json: carry json in request body")
    print("form: key_value pair in request body and carry some files")
    print("")
    print("--url {URL}: URL of API.")
    print("--thread_num {number}: The Number of threads to send requests")
    print("--request_num {number}: The Number of requests to be send to API")
    print("--output_folder {folder}:The folder that store output form respense")
    print("--urlencoded_folder {folder}: The folder that contains txt files")
    print("   this flag is requried if mimetype is arg or urlencoded")
    print("--json_folder {folder}: The folder that contains txt files")
    print("   this flag is requried if mimetype is json")
    print("--form_data {key_1} {folder_1} {key_2} {folder_2} ... --form_data_end")
    print("   this flag is requried if mimetype is from")
    print("   If key is data, then we treat it as key-value pair,")
    print("   otherwise,we will send a random file with key key_n")
    print("")
    print("Part2: files in folder:")
    print("urlencoded_folder: It should contain several txt file with the following context:")
    print("key1=value1")
    print("key2=value2")
    print("...")
    print("We will choose a random file in folder as parameters of requests.")
    print("json_folder: It should contain several json file")
    print("We will choose a random json file in folder as parameters of requests.")
    print("form_data: For each key, it should have a folder path with some files")
    print("If key=data,then we will treat folder as urlencoded_folder.")
    print("We will choose a random file in folder for each key as parameters of requests.")
else:
    from backend import stress_test_leader_thread
    parameters = {}
    for index in range(1,len(sys.argv)):     
        if sys.argv[index]=="--get":
            parameters["method"]="GET"
        elif sys.argv[index]=="--post":
            parameters["method"]="POST"
        elif sys.argv[index]=="--mimetype" and index<len(sys.argv)-1:
            parameters["mimetype"]=sys.argv[index+1]
        elif sys.argv[index]=="--url" and index<len(sys.argv)-1:
            parameters["url"]=sys.argv[index+1]
        elif sys.argv[index]=="--thread_num" and index<len(sys.argv)-1:
            try:
                parameters["thread_num"]=int(sys.argv[index+1])
            except:
                print("The thread_num is an integer")
        elif sys.argv[index]=="--request_num" and index<len(sys.argv)-1:
            try:
                parameters["request_num"]=int(sys.argv[index+1])
            except:
                print("The request_num is an integer")
        elif sys.argv[index]=="--urlencoded_folder" and index<len(sys.argv)-1:
            parameters["urlencoded_folder"]=sys.argv[index+1]
        elif sys.argv[index]=="--json_folder" and index<len(sys.argv)-1:
            parameters["json_folder"]=sys.argv[index+1]
        elif sys.argv[index]=="--form_data" and index<len(sys.argv)-1:
            result_dict = {}
            for index_2 in range(index+1,len(sys.argv),2):
                if sys.argv[index_2] == "--form_data_end":
                    break
                elif index_2 < len(sys.argv)-2 and sys.argv[index_2+1] == "--form_data_end":
                    break
                else:
                    result_dict[sys.argv[index_2]]= sys.argv[index_2+1]
            print(str(result_dict))
            parameters["form_data"]=result_dict
        elif  sys.argv[index]=="--output_folder" and index<len(sys.argv)-1:
            parameters["output_folder"]=sys.argv[index+1]
    stress_test_leader_thread(parameters=parameters).start()
   



   







 