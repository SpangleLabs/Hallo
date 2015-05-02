import random
import ircbot_chk

class mod_pony:
    def fn_cupcake(self, args, client, destination):
        'Gives out cupcakes (much better than muffins.) Format: cupcake <username> <type>'
        if(args==''):
            return "You must specify a recipient for the cupcake."
        elif(len(ircbot_chk.ircbot_chk.chk_recipientonline(self,destination[0],[args.split()[0]]))!=0):
            if(len(args.split()) >= 2):
                return '\x01ACTION gives ' + args.split()[0] + ' a ' + ' '.join(args.split()[1:]) + ' cupcake, from ' + client + '.\x01'
            else:
                return '\x01ACTION gives ' + args.split()[0] + ' a cupcake, from ' + client + '.\x01'
        else:
            return 'No one called "' + args.split()[0] + '" is online.'

