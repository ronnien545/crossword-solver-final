import torch
import datasets
from datasets import load_from_disk,Dataset 
import sys
from transformers import AutoTokenizer, TFAutoModel
import os
import logging
import threading
import copy

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow info messages
logging.getLogger("tensorflow").setLevel(logging.ERROR)  # Suppress TensorFlow warning messages
logging.getLogger("keras").setLevel(logging.ERROR)

model_ckpt = "all-mpnet-base-v2"
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

model = AutoTokenizer.from_pretrained("bert-base-uncased") 
#loads a empty dataset to set load_dataset 
load_dataset = Dataset.from_dict({"text": [], "label": []}) 

def loadmodel():
   global model
   global load_dataset
   global tokenizer

   tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
   model = TFAutoModel.from_pretrained(model_ckpt, from_pt=True)

   load_dataset = load_from_disk("total_concatenated")
   load_dataset.load_faiss_index('embeddings', 'total_concatenated.faiss')


currthread = threading.Thread(target=loadmodel)
#starts thread that loads dataset
currthread.start()

def finishload():
  currthread.join()
    

def cls_pooling(model_output):
    #get final hidden state of output embedding
    return model_output.last_hidden_state[:, 0]

def get_embeddings(text_list):
    #get embedding given a list of text
    encoded_input = tokenizer(
        text_list, padding=True, truncation=True, return_tensors="tf"
    )
    encoded_input = {k: v for k, v in encoded_input.items()}
    model_output = model(**encoded_input)
    return cls_pooling(model_output)



#solve function
def solve(nsom,cluelst):  
  n = len(nsom[0])
  consmat = []
  tmpb =''

  anslst = []

 #create empty constraint matrix 
  for i in range(len(nsom)): 
    tmpa=[]
    for j in range(len(nsom[0])):
       tmpa.append(tmpb)
    consmat.append(tmpa)
    
  #anlst is same structure as cluelst
  sizecluelst = len(cluelst)
  for i in range(sizecluelst):
    tempa = []
    for j in range(2):
      if(cluelst[i][j]==None):
         tempa.append(None)
      else:
         tempa.append(0)
    anslst.append(tempa)
   

  return findexactclues(cluelst,nsom,consmat,anslst)













def findexactclues(cluelst,nsom,consmat,anslst):
 
 
 startlst = []

 tmpmat = copy.deepcopy(consmat)
 
 for i in range(len(cluelst)):
   for j in (range(2)):
     print("This is what the constriant matrix looks like")
     print(tmpmat)
     print(anslst)
     print("asdasdasdas")
     #find unassigned clues to set
     if cluelst[i][j] != None:
      start = ""
      start += "|1"
      if j==0:
        start += "r" + str(i+1) + "|"
      else:
        start += "d" + str(i+1) + "|"
      
      #modify constraints to insert future clue
      k,tmpmat = modify_constraint(cluelst[i][j],nsom,tmpmat,cluelst,start)

      print(anslst)

      clueis = cluelst[i][j]
      
      question_embedding = get_embeddings([clueis]).numpy()[0]
      scores, samples = load_dataset.get_nearest_examples(
      "embeddings", question_embedding, k=5
      )

      constraints = []

      n = len(consmat[0])
      
      #find starting position in consmat and find all constraints occurring in word
      for i1 in range(len(nsom)):
        for i2 in range(len(nsom[0])):
          if start in tmpmat[i1][i2]:
            c = 0
            if "d" in start:
               while c<k:
                  result_list = tmpmat[i1+c][i2].split("|")
                  result_lstcpy = copy.deepcopy(result_list)
                  for l in result_lstcpy:
                    start3 = []
                    lcpy = copy.copy(l)
                    #remove from constraints its own constraint
                    if "d" in l:
                      startcpy = copy.copy(start)
                      start2 = startcpy[:-1].split("d")
                      start3 = lcpy.split("d")
                      if (start2[1] == start3[1]):
                        result_list.remove(l)
                    if (l==''):
                        result_list.remove(l)
                  constraints += [result_list]
                  c+=1
            elif "r" in start:
               while c<k:
                  result_list = tmpmat[i1][i2+c].split("|")
                  result_lstcpy = copy.deepcopy(result_list)
                  for l in result_lstcpy:
                    start3 = []
                    lcpy = copy.copy(l)
                    if "r" in l:
                      startcpy = copy.copy(start)
                      start2 = startcpy[:-1].split("r")
                      start3 = lcpy.split("r")
                      if (start2[1] == start3[1]):
                        result_list.remove(l)
                    if (l==''):
                        result_list.remove(l)
                  constraints += [result_list]
                  c+=1

      lettercons = []
      crosscnt = 0
      wordstomodify= []
     
      for ia in constraints:
       
       if ia==[]:
         lettercons.append('')
       else:
         #for each constraint check if word is in anslst and then add to wordstomodify
         for word in ia:
          if "r" in word:
            start2 = word.split('r')
            if anslst[int(start2[1])-1][0]!= 0 and anslst[int(start2[1])-1][0]!= None:
               wordstomodify.append(word) 
          elif "d" in word:
            start2 = word.split('d')
            if anslst[int(start2[1])-1][1]!= 0 and anslst[int(start2[1])-1][1]!= None:
               wordstomodify.append(word) 
       for ib in ia:
         if "r" in str(ib):
            crosscnt +=1
            start2 = ib.split('r')
            #only append to lettercons if anslist at that position is unassigned
            if anslst[int(start2[1])-1][0]!= 0 and anslst[int(start2[1])-1][0]!= None:
              lettercons.append(anslst[int(start2[1])-1][0][0][int(start2[0])-1])
            else:
              lettercons.append('')
            #lettercons.append(anslst[int(j[2:])-1][0][int(j[:1])-1])
         elif "d" in ib:
            crosscnt +=1
            start2 = ib.split('d')
            #only append to lettercons if anslist at that position is assigned
            if anslst[int(start2[1])-1][1]!= 0 and anslst[int(start2[1])-1][1]!= None:
              lettercons.append(anslst[int(start2[1])-1][1][0][int(start2[0])-1])
            else:
              lettercons.append('')
            #lettercons.append(anslst[int(j[2:])-1][1][int(j[:1])-1])
            
      for itema in range(len(samples['Word'])):
        if samples['Word'][itema]==None:
          samples['Word'][itema]= 'NULL'
          didhappen = True
          print("ok")  
  
      alst = copy.deepcopy(list(samples['Word']))
      for s in samples['Word']:
        indextoget = 0
        for ia in range(len(s)):
          if scores[samples['Word'].index(s)] >= 0.001:
            if s in alst:
                alst.remove(s)
                break
          if len(s)>k or len(s)<k or (lettercons[ia]!="" and lettercons[ia] != s[ia]):
            #if the clue is identical in length
            if len(s) == k:
              if scores[samples['Word'].index(s)] < 0.001:
                max = 0
                #get the word that wordstomodify
                ib = wordstomodify[indextoget]
                if ("r" in ib):
                 start2 = ib.split("r")
                 if anslst[int(start2[1])-1][0] !=0:
                   max = anslst[int(start2[1])-1][0][1]
                elif ("d" in ib):
                 start2 = ib.split("d")
                 if anslst[int(start2[1])-1][1] !=0:
                   max = anslst[int(start2[1])-1][1][1]

                #then remove word from possible answer if its nummber of crossings is less than the max + 1
                if (len(wordstomodify)< max + 1):
                  if s in alst:
                    alst.remove(s)
                else:
                  #otherwise remove other word from anslst
                  anslst[int(start2[1])-1]["d" in ib] = 0
              else:
                if s in alst:
                  alst.remove(s)
            else:
              if s in alst:
                alst.remove(s)
            break

          #if letters match then increase index to go to next constraint in wordstomodify
          elif len(s) == k and lettercons[ia]!="" :
            indextoget +=1
 
          
      #modify the answerlist and increase the number of crossings for all constrained clues
      if len(alst)>0:
         anslst[i][j] = [alst[0], len(wordstomodify)]
         #increase the number of crossings for each word that it is connected to
         for word in wordstomodify:
           coords = []

           if "r" in word:
             start2 = word.split('r')
             if anslst[int(start2[1])-1][0]!= 0 and anslst[int(start2[1])-1][0]!= None:
               coords.append(start2[1])
               coords.append(0)
           else:
             start2 = word.split("d")
             if anslst[int(start2[1])-1][1]!= 0 and anslst[int(start2[1])-1][1]!= None:
               coords.append(start2[1])
               coords.append(1)
           
           if len(coords)> 0:
            anslst[int(coords[0])-1][coords[1]][1]+=1

 #create a copy of old tmpmat to pass to fillmissing 
 oldtmpmat = copy.deepcopy(tmpmat)
 #go through tmpmat and remove any constraints that don't have answers before passing to backtrack
 for i in range(len(tmpmat)):
   for j in range(len(tmpmat[i])):
     
     lstofcons = tmpmat[i][j].split('|')
     lstofcons  = [a for a in lstofcons if a!=""]
     lstofcons2 = copy.copy(lstofcons)

     for c in lstofcons:
       if "r" in c:
         start2 = c.split("r")
         if anslst[int(start2[1])-1][0]== 0 or anslst[int(start2[1])-1][0]== None:
           lstofcons2.remove(c)
       elif "d" in  c:
         start2 = c.split("d")
         if anslst[int(start2[1])-1][1]== 0 or anslst[int(start2[1])-1][1]== None:
           lstofcons2.remove(c)

     tmpmat[i][j] = ""
     if len(lstofcons2) != 0:
        tmpmat[i][j] += "|"
        for a  in lstofcons2:
          tmpmat[i][j] += a + "|"
 


 infolst = copy.deepcopy(anslst)
  
 answer = backtrack(cluelst,nsom,copy.deepcopy(tmpmat),anslst,[-1,-1],infolst)

 answer2 = fillmissing(answer,cluelst,nsom,oldtmpmat)

 return answer2















def modify_constraint(clue,nsom,consmatcpy,cluelst,start):
  n = len(nsom[0])
  k = 0


  if "r" in start:
     start2 = start.split('r')
  elif "d" in start:
     start2 = start.split('d')

 #find in nsom where it is equal to start which is in format like "|1d5|" so the number to find is 5
  for i in range(len(nsom)):
    for j in range(len(nsom[0])):
      if start2[1][:-1]== str(nsom[i][j]):
        if "r" in start: 
         while(j+k<len(nsom[0]) and nsom[i][j+k] != 0):
                #add to the constraint matrix as crossword is getting solved
                if consmatcpy[i][j+k]=="":
                  consmatcpy[i][j+k] += "|" + str(k+1) + "r"+str(nsom[i][j]) + "|"
                else:
                  consmatcpy[i][j+k] += str(k+1) + "r"+str(nsom[i][j]) + "|"
                k+=1
        elif "d" in start:
         while(i+k<len(nsom) and nsom[i+k][j] != 0):
                #add to the constraint matrix as crossword is getting solved
                if consmatcpy[i+k][j]=="":
                  consmatcpy[i+k][j] += "|" + str(k+1) + "d"+str(nsom[i][j]) + "|"
                else:
                  consmatcpy[i+k][j] += str(k+1) + "d"+str(nsom[i][j]) + "|"
                k+=1 

  return k,consmatcpy












def solveconstr(clue,k,consmat,start,anslst):

   constraints = []

   n = len(consmat[0])

   for i in range(len(consmat)):
     for  j in range(len(consmat[0])):
        if start in consmat[i][j]:
           c = 0
           if "d" in start:
             while c<k:
               result_list = consmat[i+c][j].split("|")
               result_lstcpy = copy.deepcopy(result_list)
               for l in result_lstcpy:
                  lcpy = copy.copy(l)
                  if "d" in l:
                    startcpy = copy.copy(start)
                    start2 = startcpy[:-1].split("d")
                    start3 = lcpy.split("d")
                    if (start2[1] == start3[1]):
                      result_list.remove(l)
                  elif (l==''):
                    result_list.remove(l)
               constraints += [result_list]
               c+=1
           elif "r" in start:
             while c<k:
               result_list = consmat[i][j+c].split("|")
               result_lstcpy = copy.deepcopy(result_list)
               for l in result_list:
                  lcpy = copy.copy(l)
                  if "r" in l:
                    startcpy = copy.copy(start)
                    start2 = startcpy[:-1].split("r")
                    start3 = lcpy.split("r")
                    if (start2[1] == start3[1]):
                      result_list.remove(l)
                  elif (l==''):
                    result_list.remove(l)
               constraints += [result_list]
               c+=1
   lettercons = []
   wordstomodify= []

   for l in constraints:
    if l==[]:
      lettercons.append('')
    else:
      for word in l:
        if "r" in word:
            start2 = word.split('r')
            if anslst[int(start2[1])-1][0]!= 0:
               wordstomodify.append(word)
        elif "d" in word:
            start2 = word.split('d')
            if anslst[int(start2[1])-1][1]!= 0:
               wordstomodify.append(word) 
    for m in l:
      if "r" in m:
         start2 = m.split('r')
         if anslst[int(start2[1])-1][0]!= 0:
           lettercons.append(anslst[int(start2[1])-1][0][0][int(start2[0])-1])
         else:
           lettercons.append('')
         #lettercons.append(anslst[int(j[2:])-1][0][int(j[:1])-1])
      elif "d" in m:
         start2 = m.split('d')
         if anslst[int(start2[1])-1][1]!= 0:
           lettercons.append(anslst[int(start2[1])-1][1][0][int(start2[0])-1])
         else:
           lettercons.append('')
         #lettercons.append(anslst[int(j[2:])-1][1][int(j[:1])-1])

   question_embedding = get_embeddings([clue]).numpy()[0]


   scores, samples = load_dataset.get_nearest_examples(
      "embeddings", question_embedding, k=5
   )

   didhappen = False

   for itema in range(len(samples['Word'])):
        if samples['Word'][itema]==None:
          samples['Word'][itema]= 'NULL'

   alst = list(samples['Word'])
   
   for s in samples['Word']:
      for l in range(len(s)):
        if len(s)>k or len(s)<k or (lettercons[l]!="" and lettercons[l] != s[l]):
          alst.remove(s)
          break 

   if len(alst)>0:
      return alst,wordstomodify

   return alst,wordstomodify











#backtracking algorithm in constraint satisfaction
def backtrack(cluelst,nsom,consmat,anslst,prev,infolst):
   
   
   clue = ""

   posx = 0
   posy = 0
    
   start = ""
   for i in range(len(anslst)):
     for j in range(2):
       #look for unassigned clues and set variable start
       if anslst[i][j]==0 and infolst[i][j]!=-2:
          clue = cluelst[i][j]
          posx= i
          posy= j
          if(j==0):
            start += "|" + str(1) + "r" + str(i+1) + "|"
          else:
            start += "|" + str(1) + "d" + str(i+1) + "|"
          break
     if clue != "":
        break

   #if no unassigned clues can be found then return the answer list
   if(start==""):
      return anslst
   
   #modify constraint for the future word
   n = len(nsom[0])
   nletters = 0

   #print(nletters)
   
   nletters,nconsmat = modify_constraint(clue,nsom,consmat,cluelst,start)

   #find the word based on the new constraint
   wordlst,wordstomodify = solveconstr(clue,nletters,nconsmat,start,anslst)
   
   if len(wordlst) > 0:
    wordcount = 0
    for word in wordlst:
       wordcount+=1
       #go through each word if one of these gives a complete result then return this
       anslst[posx][posy] = [word, len(wordstomodify)]
       #increase the number of crossings for each word that it is connected to
       for word in wordstomodify:
        coords = []

        if "r" in word:
          start2 = word.split('r')
          coords.append(start2[1])
          coords.append(0)
        else:
          start2 = word.split("d")
          coords.append(start2[1])
          coords.append(1)
        anslst[int(coords[0])-1][coords[1]][1]+=1

        if len(wordstomodify)>2:
          infolst[prev[0]][prev[1]]=-2

        result = backtrack(cluelst,nsom,copy.deepcopy(nconsmat),copy.deepcopy(anslst),[posx,posy],infolst)
        if result is not None:
          return result
  

   if prev ==[-1,-1]:
      infolst[posx][posy] = -2
      return backtrack(cluelst,nsom,copy.deepcopy(nconsmat),copy.deepcopy(anslst),[posx,posy],infolst)
   elif infolst[prev[0]][prev[1]]==-2:
      infolst[posx][posy] = -2
      return backtrack(cluelst,nsom,copy.deepcopy(nconsmat),copy.deepcopy(anslst),[posx,posy],infolst) 
         
   #if no words in wordlst or no words give non complete result then return None
   return None












def fillmissing(anslst,cluelst, nsom,consmat):
    
    wordlst = []
    wordlst2 = []
    lstofallpossible = []
    with open("crosswordwords.txt", 'r') as file:
        for line in file:
          wordlst.append(line.strip())

    
    while True:
      #find missing words
      start = ""
      clue =""
      for i in range(len(anslst)):
       for j in range(2):
        #look for unassigned clues and set variable start
        if anslst[i][j]==0:
            anslst[i][j]=1
            clue = cluelst[i][j]
            posx= i
            posy= j
            if(j==0):
              start += "|" + str(1) + "r" + str(i+1) + "|"
            else:
              start += "|" + str(1) + "d" + str(i+1) + "|"
            break
       if clue != "":
          break
       
      
      #if no unassigned clues can be found then leave while loop
      if(start==""):
        break

      constraints = []
      
      print("")
      n = len(consmat[0])
      for i in range(len(consmat)):
        for j in range(len(consmat[0])):
            if start in consmat[i][j]:
              startnew = copy.copy(start)
              if "d" in start:
                startnew = startnew.split("d")
              elif "r" in start:
                startnew = startnew.split("r")
              c= 0
              if "d" in start:
                while (i+c < len(consmat)) and (startnew[1] in consmat[i+c][j]):
                  result_list = consmat[i+c][j].split("|")
                  result_lstcpy = copy.deepcopy(result_list)
                  for l in result_lstcpy:
                    start3= []
                    lcpy = copy.copy(l)
                    if "d" in l:
                     startcpy = copy.copy(start)
                     start2 = startcpy[:-1].split("d")
                     start3 = lcpy.split("d")
                     if (start2[1] == start3[1]):
                      result_list.remove(l)
                    elif (l==''):
                      result_list.remove(l)
                  constraints += [result_list]
                  c+=1
              elif "r" in start:
                while (j+c < len(consmat[0])) and (startnew[1] in consmat[i][j+c]):
                  result_list = consmat[i][j+c].split("|")
                  result_lstcpy = copy.deepcopy(result_list)
                  for l in result_lstcpy:
                    start3 = []
                    lcpy = copy.copy(l)
                    if "r" in l:
                      startcpy = copy.copy(start)
                      start2 = startcpy[:-1].split("r")
                      start3 = lcpy.split("r")
                      if (start2[1] == start3[1]):
                        result_list.remove(l)
                    elif (l==''):
                      result_list.remove(l)
                  constraints += [result_list]
                  c+=1

      lettercons = []
      wordstomodify= []
      
      unassignedcons = []
      for l in constraints:
        if l==[]:
          lettercons.append('')
          unassignedcons.append("")
        else:
          for word in l:
            wordstomodify.append(word)
        for m in l:
          tmpunassign=""
          if "r" in m:
            start2 = m.split('r')
            print(anslst[int(start2[1])-1][0])
            if anslst[int(start2[1])-1][0]==0 or anslst[int(start2[1])-1][0]==1:
              if start !=m:
               lettercons.append("")
               tmpunassign = m
            else:
              lettercons.append(anslst[int(start2[1])-1][0][0][int(start2[0])-1])
            #lettercons.append(anslst[int(j[2:])-1][0][int(j[:1])-1])
          elif "d" in m:
            start2 = m.split('d')
            if anslst[int(start2[1])-1][1]==0 or anslst[int(start2[1])-1][1]==1:
              if start !=m:
               lettercons.append("")
               tmpunassign = m
            else:
              lettercons.append(anslst[int(start2[1])-1][1][0][int(start2[0])-1])
            #lettercons.append(anslst[int(j[2:])-1][1][int(j[:1])-1])
          unassignedcons.append(tmpunassign)

      filename = 'yourfile.txt'
      min = 0
      max = -1
      
      mid = (max + min)//2
      potentialans = ""

      startpos = -1
      for i in range(len(wordlst)):
        if(len(wordlst[i])==len(lettercons)):
          if len(wordlst[i-1])== (len(lettercons)-1) or (i<=1):
             startpos = i
             break
      
      #find 
      while((len(wordlst[startpos]) != len(lettercons)+1) and potentialans==""):
        letters = wordlst[startpos]
        for i in range(len(letters)):
          if lettercons[i]=="":
            if i==len(letters)-1:
              potentialans=wordlst[startpos]
              break
            continue
          elif letters[i]!=lettercons[i]:
            break
          elif letters[i]==lettercons[i] and i==len(letters)-1:
            potentialans=wordlst[startpos]

        startpos +=1

      
      if "" in lettercons:
        lettercons = lettercons.remove("")

      tmplst = [potentialans,start,[con for con in unassignedcons]]
      wordlst2.append(tmplst)
    
    for i in range(len(anslst)):
      for j in range(len(anslst[0])):
        if anslst[i][j]==1:
          anslst[i][j]=0

    
    #sort the sortedwordlst so the words that have least constraints with other unassigned clues are put first
    sortedwordlst =  sorted(wordlst2, key=lambda word: (getnumcon(word), word))
    
    
    for i in sortedwordlst:
      start = i[1]
      potentialans = i[0]
      assign = False
      
      for j in range(len(i[2])):
        let = ""
        if potentialans== "":
          break
        if i[2][j] == "":
            if j==len(i[2])-1:
              assign = True
              break
            continue
        #check if each constraint of unassigned clues at the start is assigned or not
        if "r" in i[2][j]:
          start2 = i[2][j].split("r")
          if anslst[int(start2[1])-1][0]==0:
            if j==len(i[2])-1:
              assign = True
              break
            continue
          let= anslst[int(start2[1])-1][0][0][int(start2[0])-1]
        elif "d" in i[2][j]:
          start2 = i[2][j].split("d")
          if anslst[int(start2[1])-1][1]==0:
            if j==len(i[2])-1:
              assign = True
              break
            continue
          let= anslst[int(start2[1])-1][1][0][int(start2[0])-1]
        #compare each letter with each letter of potentialanswer
        #print("This is the wordlst")
        #print(sortedwordlst)
        if let==potentialans[j]:
            if j==len(i[2])-1:
              assign = True
              break
            continue
        else:
          break
      #if assign is set to true assign the potentialnaswer to answerlist
      if assign== True:
          start = start[:-1]
          if "r" in start:
            start2 = start.split("r")
            anslst[int(start2[1])-1][0]= [i[0],0]
          elif "d" in start:
            start2 = start.split("d")
            anslst[int(start2[1])-1][1]= [i[0],0]
      

    return anslst  
         








def getnumcon(word):
   num = 0
   for i in word[2]:
     if i!="":
       num += len(i)

   return num





if __name__ == "__main__":
   #this is to test
   anslst = solve([[1, 2, 3, 4, 0], [5, -1, -1, -1, 6], [7, -1, -1, -1, -1], [8, -1, -1, -1, -1], [9, -1, -1, -1, -1], [0, 10, -1, -1, -1]],[['Put away in the overhead bin', 'Sends incessant messages to'], [None, 'Bad Wordle to spoil'], [None, '\nSeasoned hand'], [None, 'Begin to cry'], ['Pair for a skier', None], [None, 'Slowly drips out'], ['Confuse', None], ['With 9-Across, noted product of Vermont', None], ['See 8-Across', None], ['Liquid-absorbing substances', None]])
   #anslst = fillmissing([[0, ['BRAVE', 2]], [None, ['RICED', 1]], [None, ['AZURE', 1]], [None, ['ZOOEY', 1]], [None, ['INUSE', 1]], [None, 0], [0, ['AVER', 1]], [0, None], [0, None], [['REDEYE', 6], None]],[['Country with the most FIFA world cup titles', 'Courageous'], [None, 'Chopped into small pieces, as cauliflower'], [None, 'Sky-blue'], [None, 'Actress Deschanel of "New Girl"'], [None, 'Sign on an occupied lavatory'], [None, 'Stand the test of time'], ['One of the two U.S. states that doesnt observe daylight saving time', 'Confidently assert'], ['Mindless', None], ['Alpanist Dave karniCar once skied 12,000 feet down this mountain', None], ['Overnight flight', None]],[[0, 1, 2, 3, 4, 5, 6], [7, -1, -1, -1, -1, -1, -1], [8, -1, -1, -1, -1, -1, -1], [9, -1, -1, -1, -1, -1, -1], [10, -1, -1, -1, -1, -1, 0]],[['', '1r1|1d1|', '2r1|1d2|', '3r1|1d3|', '4r1|1d4|', '5r1|1d5|', '6r1|1d6|'], ['1r7|1d7|', '2d1|2r7|', '2d2|3r7|', '2d3|4r7|', '2d4|5r7|', '2d5|6r7|', '2d6|7r7|'], ['2d7|1r8|', '3d1|2r8|', '3d2|3r8|', '3d3|4r8|', '3d4|5r8|', '3d5|6r8|', '3d6|7r8|'], ['3d7|1r9|', '4d1|2r9|', '4d2|3r9|', '4d3|4r9|', '4d4|5r9|', '4d5|6r9|', '4d6|7r9|'], ['4d7|1r10|', '5d1|2r10|', '5d2|3r10|', '5d3|4r10|', '5d4|5r10|', '5d5|6r10|', '']])
   print(anslst)
   
