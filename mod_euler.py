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










