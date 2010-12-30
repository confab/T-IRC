################################################################################
##  confabot.py                                                               ##
##  IRC bot based on twisted                                                  ##
##  Written by Taos, modified by confab                                       ##
################################################################################

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.python import log
from twisted.words.protocols import irc
import math
import random
import sys
import time
import urllib

class Tirc(irc.IRCClient):
    '''IRC operations class.'''

    def _get_nickname(self):
        '''Sets the nick to a local variable'''
        return self.factory.nickname
    nickname = property(_get_nickname)

    def _get_com(self):
        '''Sets the com class to a local variable'''
        return self.factory.com()
    com = property(_get_com)

    def signedOn(self):
        '''Calls the ident function and displays nick'''
        self.ident()
        log.msg("Signed on as %s" % self.nickname)

    def joined(self, channel):
        '''Displays the channel joined and the topic in CLI'''
        
        log.msg("Joined %s" % channel)
        log.msg("Got topic %s" % self.topic(channel))

    def noticed(self, user, channel, message):
        '''Displays all notices in CLI'''
        
        log.msg("I got a notice from %s in %s, here it is: %s" % (user,
            channel, message))

    def ident(self):
        '''Identifies bot using password entered at initialization'''
        
        log.msg("Trying to ident.")
        self.msg('NickServ', 'identify %s' % self.factory.password)
        self.join(self.factory.channel)

    def privmsg(self, user, channel, msg):
        '''Displays all messages in CLI and uses pertinent messages'''
        
        log.msg("\nUser: %s\nChannel: %s\nMessage: %s\n" % (user, channel, msg))
        #work out if its addressed to me
        chain = msg.strip()
        if msg.startswith(self.nickname):
            chain = chain.split()[1:]
            if chain[0].startswith('!'):
                chain[0].strip('!')
                self.msg(channel, self.com.process_command(chain))
            else:
                pass
        else:
            pass
            
    def get_topic(self):
        return """Welcome to Python-forum ~ Tenarus is a bot, powered by Tirc
        written by Taos ~ Don't ask just ask. ~ Paste > 3 lines? Use a paste
        service..."""


class TircFactory(protocol.ClientFactory):
    '''Variables used to connect.'''
    
    protocol = Tirc

    def __init__(self, channel, nickname, password, com_map):
        self.channel = channel
        self.nickname = nickname
        self.password = password
        self.com = com_map

    def clientConnectionLost(self, connector, reason):
        log.msg("Lost connection because: %s Reconnecting" % reason)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        log.msg("Could not connect: %s" % reason)

class COM(object):
    '''Main command class.  Put all commands here.'''
    
    def __init__(self):

        #   Dictionary of main commands
        self.cmd = {'!time': self.get_time,
                     '!google': self.google_search,
                     '!help': self.helper,
                     '!pysearch': self.python_forum_search,
                     '!prime': self.prime_sieve,
                     '!say': self.say,
                     '!factors': self.factors}

        #   Dictionary of help commands
        self.help_cmd = {'!google': self.google_search.__doc__,
                          '!pysearch': self.python_forum_search.__doc__,
                          '!time': self.get_time.__doc__,
                          '!prime': self.prime_sieve.__doc__,
                          '!say': self.say.__doc__,
                          '!factors': self.factors.__doc__}

    def err1(self, *args):
        return 'Not a recognised cmd, type confabot: !help for more info'

    def factors(self, *args):
        '''"!factors" Returns the factors of an integer greater than 1.
Proper format is !factors <number>'''

        #   Check if value entered is a number, show error if not a number.
        try:
            n = int(args[0])
        except ValueError:
            return '%s is not an integer greater than 1.' % ''.join(args)

        #   Check if number is within acceptable range, show errors if not.
        #   Compute factors if it is.            
        if n > 1000000:
            return 'I think it would be easier if I stuck to low numbers.'
        elif n < 2:
                return '%d is not a whole number greater than 1.' % n
        else:
            factors = [test for test in xrange(2, n) if n % test == 0]
            if not factors:
                return '%d is prime.' % n
            else:
                return ''.join(str(factors))


    def get_time(self, *args):
        '''"!time" Returns the current time in my timezone.'''

        return time.asctime()

    def google_search(self, *args):
        '''"!google" Returns a link to google with the search string appended \
to the end.
Proper format is !google <word> <word> <word> ...'''

        return 'http://www.google.com/search?q=%s' % urllib.quote_plus(
               ''.join(args))

    def helper(self, *args):
        '''Avalible commands are, %s
Type confabot: !help <cmd> for detailed help.  E.g. confabot !help !time'''

        return self.help_cmd.get(args[0], self.helper.__doc__ % self.cmd.keys())

    def process_command(self, cmd):
        '''Defaults to an error if command chosen does not exist.'''

        return self.cmd.get(cmd[0], self.err1)(' '.join(cmd[1:]))

    def prime_sieve(self, *args):
        '''"!prime" Returns the nth prime number.
        Proper format is !prime n.'''

        #   Check if value entered is a number, show error if not a number.
        try:
            n = int(args[0])
        except ValueError:
            return 'That is not a valid number.'

        #   Compute prime if less than 100000.  Based on the Sieve of
        #   Eratosthenes.  Creates a list, goes through list zero-ing multiples
        #   of each number, then removing all zeroes.  Returns nth prime and
        #   time elapsed.
        if n < 100001:
            
            start = time.time()
            
            candidates = int(1.3 * n * math.log(n))
            prime_list = range(candidates + 1)
            high_check = int(candidates ** .5) + 1

            for i in xrange(2, high_check):
                if not prime_list[i]:
                    continue
                prime_list[2 * i :: i] = [0] * (candidates / i - 1)
            prime_list = sorted(list(set(prime_list)))
            
            return 'The %dth prime is: %d: Calculated in %.12f seconds.' %(n,
                   prime_list[n + 1], time.time() - start)

        #   Same as before, but with numbers from 100,000 to 1,000,000.
        elif n < 1000001:
        
            start = time.time()
            
            candidates = int(1.129 * n * math.log(n))
            prime_list = range(candidates + 1)
            high_check = int(candidates ** .5) + 1

            for i in xrange(2, high_check):
                if not prime_list[i]:
                    continue
                prime_list[2 * i :: i] = [0] * (candidates / i - 1)
            prime_list = sorted(list(set(prime_list)))
            
            return 'The %dth prime is: %d: Calculated in %.12f seconds.' %(n,
                   prime_list[n + 1], time.time() - start)

        #   If the number is out of range, be a smartass.
        else:
        
            start = time.time()

            m, n = n, random.randint(10, 100)
            candidates = int(1.3 * n * math.log(n))
            prime_list = range(candidates + 1)
            high_check = int(candidates ** .5) + 1

            for i in xrange(2, high_check):
                if not prime_list[i]:
                    continue
                prime_list[2 * i :: i] = [0] * (candidates / i - 1)
            prime_list = sorted(list(set(prime_list)))
            
            return '''The %dth prime is: %d: Calculated in %.12f seconds.
Oh, you wanted the %dth prime?  I don't calculate that high.''' %(n, 
                   prime_list[n + 1], time.time() - start, m)
    
    def python_forum_search(self, *args):
        '''"!pysearch" Returns a link to the python forum with the string \
appended to the end.
Proper format is !pysearch <word> <word> <word> ...'''

        return 'http://www.python-forum.org/pythonforum/search.php?keywords=%s'\
               % urllib.quote_plus(''.join(args))

    def say(self, *args):
        '''"!say" Forces me to say whatever you want me to!
Proper format is !say <word> <word> <word> ...'''

        return ''.join(args)

def main(chan, nick, password, out):
    '''Main function, starts connection, etc...'''

    log.startLogging(out)
    reactor.connectTCP('irc.freenode.net',6667,
        TircFactory(chan, nick, password))
    reactor.run()

if __name__ in '__main__':
    '''Asks user for information: channel, nick, password, and server.'''
    
    chan = '#python-forum'
    nick = 'confabot'
#    nick = raw_input('Enter a nick: ')
    password = ''
#    password = raw_input('Enter a pass: ')
    log.startLogging(sys.stdout)
    reactor.connectTCP('irc.freenode.net',6667,
        TircFactory(chan, nick, password, COM))
    reactor.run()
