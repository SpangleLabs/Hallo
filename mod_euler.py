import collections

class mod_euler:
    def fn_euler(self, args, client, destination):
        'Project Euler functions. Format: "euler list" to list project euler solutions. "euler <number>" for the solution to project euler problem of the given number.'
        if(args.replace(' ','').isdigit()):
            #try and do that euler function command
            if(hasattr(mod_euler,'fnn_euler_' + args) and isinstance(getattr(mod_euler,'fnn_euler_' + args), collections.Callable)):
                eulerfunc = getattr(mod_euler,'fnn_euler_' + args)
                if(hasattr(eulerfunc, '__call__')):
                    try:
                        answer = "Euler project problem " + args + "? I think the answer is: " + str(eulerfunc(self)) + "."
                    except Exception as e:
                        answer = "hmm, seems that one doesn't work... darnit."
                        print("EULER ERROR: " + str(e))
                else:
                    answer = "That doesn't seem to work."
            else:
                answer = "I don't think I've solved that one yet."
        elif(args.replace(' ','').lower() == 'list'):
            #list all available project Euler answers
            problem_funcs = []
            for fn in dir(mod_euler):
                if(fn[:10] == 'fnn_euler_' and fn[10:].isdigit()):
                    problem_funcs.append(fn[10:])
            answer = "Currently I can do Project Euler problems " + ', '.join(sorted(problem_funcs,key=int)[:-1]) + " and " + sorted(problem_funcs,key=int)[-1] + '.'
        else:
            count = sum(1 for fn in dir(mod_euler) if fn[:10] == 'fnn_euler_' and fn[10:].isdigit())
            answer = "I'm learning to complete the project Euler programming problems. I've not done many so far, I've only done " + str(count) + " of the 434 problems. But I'm working at it... say 'Hallo Euler list' and I'll list what I've done so far, say 'Hallo Euler {num}' for the answer to challenge number {num}."
        return answer

    def fnn_euler_readfiletostring(self,filename):
        f = open(filename,"r")
        return f.read()[:-1]

    def fnn_euler_readfiletolist(self,filename):
        f = open(filename,"r")
        filearray = []
        num_line = 0
        raw_line = f.readline()
        while raw_line != '':
            filearray.append(raw_line.replace("\n",''))
            num_line = num_line + 1
            raw_line = f.readline()
        return filearray

    def fnn_euler_wordvalue(self,word):
        value = 0
        word = word.upper()
        for char in word:
            value += ord(char)-64
        return value
        
    def fnn_euler_42(self):
        filestring = mod_euler.fnn_euler_readfiletostring(self,'euler/euler_42_words.txt')
        words = [word.replace('"','') for word in filestring.split(',')]
        longestword = max(words,key=len)
        triangles = []
        count = 0
        x = 1
        while (0.5*x*(x+1)) < 26*len(longestword):
            triangles.append(0.5*x*(x+1))
            x += 1
        for word in words:
            if(mod_euler.fnn_euler_wordvalue(self,word) in triangles):
                print('found a triangle word: ' + word)
                count += 1
        return count
        

    def fnn_euler_pandigitals(self):
        pandigitals = []
        digits = list(range(10))
        for a in range(9):
            adigit = digits[a+1]
            adigits = list(digits)
            del adigits[a+1]
            for b in range(9):
                bdigit = adigits[b]
                bdigits = list(adigits)
                del bdigits[b]
                for c in range(8):
                    cdigit = bdigits[c]
                    cdigits = list(bdigits)
                    del cdigits[c]
                    for d in range(7):
                        ddigit = cdigits[d]
                        ddigits = list(cdigits)
                        del ddigits[d]
                        for e in range(6):
                            edigit = ddigits[e]
                            edigits = list(ddigits)
                            del edigits[e]
                            for f in range(5):
                                fdigit = edigits[f]
                                fdigits = list(edigits)
                                del fdigits[f]
                                for g in range(4):
                                    gdigit = fdigits[g]
                                    gdigits = list(fdigits)
                                    del gdigits[g]
                                    for h in range(3):
                                        hdigit = gdigits[h]
                                        hdigits = list(gdigits)
                                        del hdigits[h]
                                        for i in range(2):
                                            idigit = hdigits[i]
                                            idigits = list(hdigits)
                                            del idigits[i]
                                            jdigit = idigits[0]
                                            pandigitals.append(1000000000*adigit+100000000*bdigit+10000000*cdigit+1000000*ddigit+100000*edigit+10000*fdigit+1000*gdigit+100*hdigit+10*idigit+jdigit)
        return pandigitals

    def fnn_euler_43(self):
        pandigitals = mod_euler.fnn_euler_pandigitals(self)
        pandigital_sum = 0
        for pandigital in pandigitals:
            if(int(str(pandigital)[1:4])%2==0 and int(str(pandigital)[2:5])%3==0 and int(str(pandigital)[3:6])%5==0 and int(str(pandigital)[4:7])%7==0 and int(str(pandigital)[5:8])%11==0):
                if(int(str(pandigital)[6:9])%13==0 and int(str(pandigital)[7:10])%17==0):
                    print('found one: ' + str(pandigital))
                    pandigital_sum += pandigital
        return pandigital_sum

    def fnn_euler_44(self):
        epsilon = 0.000001
        pentagonals = [0,1]
        smallest_diff = 10**9
        for x in range(2,3000):
            pentagonals.append(int(x*(3*x-1)/2))
            for y in range(1,x):
                pentagonal_sum = pentagonals[x] + pentagonals[y]
                diff = pentagonals[x] - pentagonals[y]
                sumpent = (1+(1+24*pentagonal_sum)**0.5)/6
                diffpent = (1+(1+24*diff)**0.5)/6
                if(sumpent%1<epsilon and diffpent%1<epsilon):
                    print('found one.')
                    if(diff<smallest_diff):
                        smallest_diff = diff
        return smallest_diff

    def fnn_euler_45(self):
        epsilon = 0.0000001
        tripenthex = 0
        for x in range(40756,10**9):
            xtri = (-1+(1+8*x)**0.5)/2
            if(xtri%1<epsilon):
                xpent = (1+(1+24*x)**0.5)/6
                if(xpent%1<epsilon):
                    xhex = (1+(1+8*x)**0.5)/4
                    if(xhex%1<epsilon):
                        print('found it.')
                        tripenthex = x
                        break
        return tripenthex



    def fnn_euler_67(self):
        #this is the same as  problem 18, but bigger file.
        arr_triangle = mod_euler.fnn_euler_readfiletolist(self,"euler/euler_67_triangle.txt")
        for x in range(len(arr_triangle)):
            arr_triangle[x] = arr_triangle[x].split()
        for row in range(len(arr_triangle)-2,-1,-1):
            for col in range(len(arr_triangle[row])):
                if(int(arr_triangle[row+1][col]) > int(arr_triangle[row+1][col+1])):
                    arr_triangle[row][col] = int(arr_triangle[row][col]) + int(arr_triangle[row+1][col])
                else:
                    arr_triangle[row][col] = int(arr_triangle[row][col]) + int(arr_triangle[row+1][col+1])
        return arr_triangle[0][0]










