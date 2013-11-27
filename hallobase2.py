def fn_kick(self, args, client, destination):
    'Kick user(s) from all channels hallo has op in.  Use "kick <user1> <user2> <user3>...".  Ops only.'
    if(self.chk_op(client)):
        if(destination[0] == 'canternet'):
            for channel in self.conf['server'][destination[0]]['channels']:
                self.conf['server'][destination[0]]['socket'].send(endl.join('KICK ' + channel + ' ' + nick for nick in args.split(' ')) + endl)
            return 'Kicked ' + ', '.join(args.split()) + '.'
        else:
            return 'No kicking here.'
    else:
        return 'Insufficient privileges to kick.'

