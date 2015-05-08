import ircbot_chk


endl = '\r\n'
class hallobase_oper:

    def fn_nicklist(self,args,client,destination):
        'Returns a user list for a given channel. format: nicklist <channel>'
        channels = ircbot_chk.ircbot_chk.chk_destination(self,destination[0],destination[1],client,args)
        if(channels[0][0] is None):
            return "This is not a valid channel, or one I am not part of. Error returned was: " + channels[0][1]
        output = []
        for channel in channels:
            userlist = self.core['server'][channel[0]]['channel'][channel[1]]['user_list']
            output.append("Users in " + channel[0] + ":" + channel[1] + "> (" + str(len(userlist)) + ") " + ', '.join(userlist) + ".")
        return "\n".join(output)



