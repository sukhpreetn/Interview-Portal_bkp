


def displayformat(question):
    #return HttpResponse("display")
    b = question
    a = b.split("|")
    print(a)
    func_name = ""
    func_name1 = " "
    for entry in a:
        if 'def' in entry:
            c = entry.split(" ")
            # print(c[1])
            if "(" in c[1]:
                d = c[1].split("(")
                # print(d[0])
                func_name = d[0]

        

    out = []
    empty = "    "
    func_name1 = func_name + "("
    print("*******")
    print(func_name1)
    for entry in a:
        if 'def' in entry:
            out.append(entry)
        elif func_name1 in entry:
            out.append(entry)
        else:
            newdata = empty + entry
            out.append(newdata)

    return out

a = "def printLine(text):  |print(text, 'is awesome.') |printLine('Python')"
out = displayformat(a)
print(out)

''''
a = ['def printLine(text):', " print(text, 'is awesome.') ", " printLine('Python')"," Print(text, 'is awesome.') "]

for entry in a:
    if 'def' in entry:
        c = entry.split(" ")
        print(c[1])
        if "(" in c[1]:
            d = c[1].split("(")
            #print(d[0])
            data = d[0]

print(data)
empty = "   "
out = []
for entry in a:
    if 'def' in entry:
        out.append(entry)
    elif data in entry:
        out.append(entry)
    else:
        newdata = empty + entry
        out.append(newdata)
print("----------")
print(out)

    
        


'''
'''
b = "def printLine(text): ;print(text, 'is awesome.') ;printLine('Python')"
a = b.split(";")
print(a)

print("------ ")
out= []
for entry in a:
    if 'def' in entry:
        str1 = entry.split(" ")
        print(str1)
        for  str2 in str1 :
            if "(" in str2:
                 data = str2.split("(")
                 data1 = data[0]
                 print(data1)
                 
print("-------------------------- ")       
print(a)
for entry in a:
    if 'def' in entry:
        out.append(entry)
    elif data1 in entry:
        out.append(entry)
    else:
        out.append("  "+entry)
     
print(out[0])
print(out[1])
print(out[2])
'''


'''

b = "def printLine(text): , print(text, 'is awesome.') , printLine('Python')"
if ',' in b:
    print("yay")
a = b.split("|")
out = []
empty = "   "
for entry in a:
    if 'def' in entry:
        str1 = entry.split(" ")
        for  str2 in str1 :
            if "print(" not in str2:
                 data = str2
                 print(data)
print("----------")                 
for entry in a:
    if 'def' in entry:
        out.append(entry)
    elif print( in entry:
        out.append(data1)
    else:
        newdata = empty + entry
        out.append(newdata)

print(out)
print(out[0])
print(out[1])
print(out[2])
'''
