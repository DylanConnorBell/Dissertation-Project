import codecs
from ctypes.wintypes import tagMSG
from hashlib import sha256
from django.http import HttpResponse
from django.utils.timezone import datetime
import re
from django.shortcuts import render, redirect
import json
from .models import ImageStorage
from django.contrib import messages
import os
from django.contrib import admin
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad
from base64 import b64decode, b64encode
import time
#If setup has been executed session.csv will contain a simple string saying something like "session started"
#key.txt for key, sig.txt for sigma map, T.txt for t map.

textpath = "D:/Dissertation/website/website/website/static/website/text/"
T={}
accepted_file_types = [".jpg", ".png", ".jpeg", ".gif", ".jfif", ".svg"]


def home(request):
    filesize = os.path.getsize(textpath + "session.txt")
    if filesize == 0:
        T={}
        json.dump(T, open("T.txt", "w"))
        return render(request, "website/mainpage.html", {"setup": False, "sigmap":"", "masterkey": ""})
    else:
        with open(textpath + "T.txt", "r") as TFile:
            raw_t = TFile.read()
            T = json.loads(raw_t)
            TFile.close()
        with open(textpath + "sig.txt") as SFile:
            temp = SFile.read()
            sig = json.loads(temp)
            SFile.close()
        with open(textpath + "masterkey.txt") as KFile: 
            masterkey = KFile.read()
            KFile.close()
        #print("T MAP: ",T)
        #print("SIG MAP: ",sig)
        #print("KEY: ",masterkey)
        return render(request, "website/mainpage.html", {"setup": True, "sigmap": sig, "masterkey":masterkey})

def addImage(request):
    if request.method == "POST":
        indicator = ""
        if 'SingleSubmit' in request.POST:
            indicator = "Single"
        elif 'MultipleSubmit' in request.POST:
            indicator = "Multiple"

        if(os.path.getsize(textpath + "session.txt") == 0):
            with open(textpath + "session.txt", "w") as session:
                session.write("session started")
            with open(textpath + "masterkey.txt", "w") as KFile:
                if indicator == "Single":
                    KFile.write(request.POST.get('SingleKey'))
                elif indicator == "Multiple":
                    KFile.write(request.POST.get('MultipleKey'))

        if indicator == "Single":
            upload = ImageStorage()
            accept = False
            keyword = request.POST.get('SingleUploadKeyword')
            print(keyword)
            index = request.POST.get('SingleInd')
            print(index)
            image = request.FILES.get('SingleUploadImage')
            for ending in accepted_file_types:
                if str(image).endswith(ending) == True:
                    accept = True
            if accept == True:
                temp = str(request.POST.get('SingleSig'))
                sig = json.loads(temp)
                u = request.POST.get('SingleU')
                e = request.POST.get('SingleE')
                print("sig: ",sig)
                print("u: ",u)
                print("e: ",e)
                update(u,e,sig)
                upload.index = index
                print(image)
                upload.imagefile = image
                messages.success(request, 'Success: '+keyword+ ' has been uploaded.')
                ImageStorage.save(upload)
                return redirect('/')
            else:
                messages.success(request, 'Invalid image type uploaded, please try again, please try again')
                return redirect('/')
        elif indicator == "Multiple":
            files = request.FILES.getlist('MultipleUploadImage')
            temp = str(request.POST.get('MultipleSig'))
            sig =  json.loads(temp)
            load_u = str(request.POST.get('MultipleU'))
            us = json.loads(load_u)
            load_e = str(request.POST.get('MultipleE'))
            es = json.loads(load_e)
            keyword = request.POST.get('MultipleUploadKeyword')
            load_ind = request.POST.get('MultipleInd')
            indexes = json.loads(load_ind)
            #print(len(files))
            #print("sig: ",sig)
            #print("us: ",us)
            #print("es: ",es)
            #print("inds: ",indexes)
            accept = True
            accept_array = []
            for image in files:
                temp_array = []
                for ending in accepted_file_types:
                    if str(image).endswith(ending) == True:
                        temp_array.append("True")
                    else:
                        temp_array.append("False")
                        
                if "True" in temp_array:
                    accept_array.append("True")
                else: 
                    accept_array.append("False")

            for b in accept_array:
                if b == "False":
                    accept = False

            if accept == True:
                count = 0
                start = time.time()
                for f in files:
                    #print(f)
                    upload = ImageStorage()
                    u = us[str(count)]
                    #print("u: "+u)
                    e = es[str(count)]
                    #print("e: "+e)
                    update(u,e,sig)
                    upload.index = indexes[str(count)]
                    upload.imagefile = f
                    ImageStorage.save(upload)
                    count+=1
                end = time.time()
                timer = end-start
                average = timer/count
                if average < 0.1:
                    average = average * 1000
                    average = "{:.3f}".format(average)+"ms"
                else:
                    average = "{:.3f}".format(average)+"s"
                timer = "{:.3f}".format(timer)
                messages.success(request, "Success: "+str(count)+" images have been uploaded with the keyword "+keyword+" in "+timer+"s. Average time per image: "+average)
                return redirect('/')
            else:
                messages.success(request, 'Invalid image type uploaded, please try again')
                return redirect('/')
    return render(request, "website/add.html",{})

def update(u,e,sig):
    T = loadTMap()
    original_sig = loadSig()
    with open(textpath + "T.txt", "w") as TFile:
            TFile.truncate(0)
            T[u]=e
            TFile.write(json.dumps(T))
            TFile.close()
    
    if original_sig != sig:
        with open(textpath + "sig.txt", "w") as SFile:
                SFile.truncate(0)
                SFile.write(json.dumps(sig))
                SFile.close()

def loadSig():
    with open(textpath + "sig.txt") as SFile:
        temp = SFile.read()
        if(len(temp)!= 0):
            sig = json.loads(temp)
            SFile.close()
            return sig
        else:
            SFile.close()
            return {}

def deleteImage(request):
    if 'DeleteSubmit' in request.POST:
        keyword = request.POST.get('DeletionKeyword')
        temp = str(request.POST.get('DeleteSig'))
        sig =  json.loads(temp)
        load_u = str(request.POST.get('DeleteU'))
        us = json.loads(load_u)
        #print(len(us))
        load_e = str(request.POST.get('DeleteE'))
        es = json.loads(load_e)
        #print(len(es))
        load_display = str(request.POST.get('DisplayImages')).replace("'", '"')
        display = json.loads(load_display)
        #print(len(display))
        #print(request.POST.get("DeleteTag"))
        start = time.time()
        for i in range(0, len(display)):
            ind = display[i]
            #print(ind)
            image = ImageStorage.objects.get(index=ind)
            u = us[str(i)]
            #print("u: "+u)
            e = es[str(i)]
            #print("e: "+e)
            update(u,e,sig)
            image.delete()
            #print("Image deleted with ind: "+ind)
        end = time.time()
        timer = end - start
        count = len(display)
        average = timer/count
        if average < 0.1:
            average = average * 1000
            average = "{:.3f}".format(average)+"ms"
        else:
            average = "{:.3f}".format(average)+"s"
        timer = "{:.3f}".format(timer)+"s"
        #print(count)
        #print("sig: ",sig)
        messages.success(request, str(count)+" image(s) with the keyword "+keyword+" have been deleted from the database in "+timer+". Average deletion time is "+average)
        return render(request, "website/del.html", {"keyword":"", "sig":"", "u":"", "e":"", "results":"","count":"",  "indicator":"GET"})
    

    if 'SearchButton' in request.POST:
        keyword = request.POST.get('GetKeyword')
        #print(keyword)
        check = request.POST.get('InSig')
        if(check == "True"):
            display = []
            T = loadTMap()
            #print(len(T))
            tag = request.POST.get('GetTag')
            #print(tag)
            state = request.POST.get('State')
            print(state)
            delta = set()
            ID = set()
            counter = int(request.POST.get('Counter'))
            for count in range(counter, 0, -1):
                encoded = bytes(tag+","+state, 'UTF-8')
                u = SHA256.new(encoded).hexdigest()
                #print(u)
                e = str(T[u])
                e = e.split(" ")
                #print(e)
                temp = ""
                #print(len(u))
                #print(len(e))
                for i in range(0,len(u)):
                    x = chr(ord(chr(int(e[i], 2))) ^ ord(u[i]))
                    temp += x
                #print(temp)
                data = temp.split(",")
                ind = str(data[0])
                op = str(data[1])
                #print(op)
                key = str(data[2])
                if op == "del":
                    delta.add(ind)
                    #print(ind+" added to delta")
                elif op == "add":
                    if ind in delta:
                        delta.remove(ind)
                        #print(ind+" removed")
                    else:
                        ID.add(ind)
                        display.append(ind)
                #print("ID: "+str(ID))
                #print("Delta: "+str(delta))
                aes = AES.new(bytes(key, encoding='utf8'),AES.MODE_ECB)
                raw_newstate = aes.decrypt(b64decode(state))
                #print(raw_newstate)
                state = b64encode(bytes.fromhex((raw_newstate[:-raw_newstate[-1]]).hex())).decode()
                #print(state)
            count = len(display)
            messages.success(request, str(count)+" image(s) with the keyword "+keyword+" exist in the database.")
            return render(request, "website/del.html", {"keyword":keyword, "results":display, "count":count, "indicator":"POST"})
        else:
            messages.success(request, "There are no images with the keyword "+keyword+" in the database.")
            return render(request, "website/del.html", {"keyword":"", "sig":"", "u":"", "e":"", "results":"", "count":"", "indicator":"GET"})

    return render(request, "website/del.html", {"keyword":"", "sig":"", "u":"", "e":"", "results":"", "count":"", "indicator":"GET"})

def loadTMap():
    with open(textpath + "T.txt", "r") as TRead:
        temp = TRead.read()
        #print("FILE CONTENTS: "+temp)
        if(len(temp)==0):
            print("FILE EMPTY")
            return {}
        else:
            #print("FILE NOT EMPTY")
            T = json.loads(temp)
            return T

def imageSearch(request):
    if 'SearchButton' in request.POST:
        search = True
        keyword = request.POST.get('Search')
        check = request.POST.get('InSig')
        if(check == "True"):
            start = time.time()
            T = loadTMap()
            tag = request.POST.get('Tag')
            state = request.POST.get('State')
            display = []
            delta = set()
            ID = set()
            counter = int(request.POST.get('Counter'))
            for count in range(counter, 0, -1):
                encoded = bytes(tag+","+state, 'UTF-8')
                u = SHA256.new(encoded).hexdigest()
                e = str(T[u])
                e = e.split(" ")
                temp = ""
                for i in range(0,len(u)):
                    x = chr(ord(chr(int(e[i], 2))) ^ ord(u[i]))
                    temp += x
                data = temp.split(",")
                ind = str(data[0])
                op = str(data[1])
                key = str(data[2])
                if op == "del":
                    delta.add(ind)
                elif op == "add":
                    if ind in delta:
                        delta.remove(ind)
                    else:
                        ID.add(ind)
                        image = ImageStorage.objects.get(index=ind)
                        display.append(image)
                aes = AES.new(bytes(key, encoding='utf8'),AES.MODE_ECB)
                raw_newstate = aes.decrypt(b64decode(state))
                state = b64encode(bytes.fromhex((raw_newstate[:-raw_newstate[-1]]).hex())).decode()
            end = time.time()
            elapsed = end-start
            count = len(display)
            if count > 0:
                average_time = elapsed/count
                elapsed = "{:.3f}".format(elapsed)
                average_time = "{:.3f}".format(average_time*1000)
                context = {'images': display, 'search': search, 'keyword': keyword, "time": elapsed, "average":average_time, "count": count}
                return render(request, "website/search.html", context)
            else: 
                context = {'images': display, 'search': search, 'keyword': keyword, "count": count}
                return render(request, "website/search.html", context)
        else:
            context = {'images': [], 'search': search, 'keyword': keyword, "time":"", "average":"", "count":""}
            return render(request, "website/search.html", context)

    else:    
        search = False
        context = {'search': search}
        return render(request, "website/search.html", context)
