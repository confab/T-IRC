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
import re
import sys
import time
import urllib
import urllib2

class Tirc(irc.IRCClient):
    '''IRC operations class.'''
##  Comments here are for a form of user authorization.  Looks to be too much
##  work, so it will probably be removed.

    def __init__(self):
        self.nickname = nick
        self.com = COM(self)
#        self.i_am = ''

    def signedOn(self):
        '''Calls the ident function and displays nick'''
        self.ident()
        log.msg("Signed on as %s" % self.nickname)

    def joined(self, channel):
        '''Displays the channel joined and the topic in CLI'''
        
        log.msg("Joined %s" % channel)
        log.msg("Got topic %s" % self.topic(channel))
#        self.get_hostname()

#    def get_hostname(self):
#        self.msg(self.nickname, 'hi')

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
        chain = msg.strip()
        #work out if its addressed to me
#        username = user.split('!')[0]
#        hostname = user.split('@', 1)[1]
#        if username == self.nickname:
#            self.i_am = user.split('@', 1)[1]
#        elif self.i_am == hostname:
#            chain = chain.split()[1:]
#            if not chain:
#                pass
#            elif chain[0] == '!reload':
#                reload(Tirc())
#                self.msg(channel, 'Reloading script...')
#            else:
#                self.msg(channel, self.com.process_command(chain))
        if chain.startswith(self.nickname):
            chain = chain.split()[1:]
            if chain[0].startswith('!'):
                self.msg(channel, self.com.process_command(chain))
            else:
                pass
        else:
            pass
            
    def get_topic(self):
        return """Welcome to Python-forum ~ Tenarus is a bot, powered by Tirc
        written by Taos ~ Don't ask just ask. ~ Paste > 3 lines? Use a paste
        service..."""

    def userJoined(self, user, channel):
        time.sleep(2)
        self.msg(channel, 'Hello %s!' % user)

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
    
    def __init__(self, parent):
        self.parent = parent

        #   Dictionary of main commands
        self.cmd = {'!emote': self.emote,
                    '!factors': self.factors,
                    '!google': self.google_search,
                    '!help': self.helper,
                    '!prime': self.prime_sieve,
                    '!pysearch': self.python_forum_search,
                    '!roll': self.dice,
                    '!say': self.say,
                    '!time': self.get_time,
                    '!wiki': self.wikipedia}

        #   Dictionary of help commands
        self.help_cmd = {'!emote': self.emote.__doc__,
                         '!factors': self.factors.__doc__,
                         '!google': self.google_search.__doc__,
                         '!prime': self.prime_sieve.__doc__,
                         '!pysearch': self.python_forum_search.__doc__,
                         '!roll': self.dice.__doc__,
                         '!say': self.say.__doc__,
                         '!time': self.get_time.__doc__,
                         '!wiki': self.wikipedia.__doc__}

    def dice(self, sides):
        '''"!dice" Rolls a die.
Proper format is !dice <sides>.  If <sides> is blank, defaults to six.'''

        try:
            if sides == '':
                sides = 6
            else:
                sides = int(sides)
                
        except ValueError:
            return 'That is not a valid number of sides.'
        roll = random.randint(1, sides)

        return 'You rolled a %d!' % roll

    def emote(self, *args):
        '''"!emote" Forces me to say whatever you want me to!
Proper format is !emote <keywords>'''

        self.parent.describe(chan, ' '.join(args))
        return ''

    def err1(self, *args):
        return 'Not a recognised command, type %s: !help for more info' % nick

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
             return '%d is not an integer greater than 1.' % n
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
        '''"!google" Returns a link to google with the keywords specified.
Proper format is !google <keywords>'''

        return 'http://www.google.com/search?q=%s' % urllib.quote_plus(
               ''.join(args))

    def helper(self, *args):
        '''Avalible commands are, %s
All commands must be prefaced with my name.
Type %s !help <cmd> for detailed help.  E.g. %s !help !time'''

        return self.help_cmd.get(args[0], self.helper.__doc__ \
               % (self.cmd.keys(), nick, nick))
    
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

        if n < 2:

            return 'That is not a valid number.'

        #   Compute prime if less than 100000.  Based on the Sieve of
        #   Eratosthenes.  Creates a list, goes through list zero-ing multiples
        #   of each number, then removing all zeroes.  Returns nth prime and
        #   time elapsed.
        elif n < 6:
            start = time.time()
            
            candidates = 12
            prime_list = range(candidates + 1)
            high_check = int(candidates ** .5) + 1

            for i in xrange(2, high_check):
                if not prime_list[i]:
                    continue
                prime_list[2 * i :: i] = [0] * (candidates / i - 1)
            prime_list = sorted(list(set(prime_list)))
            
            return 'The %dth prime is: %d: Calculated in %.12f seconds.' %(n,
                   prime_list[n + 1], time.time() - start)

        #   Same as before, but with numbers from 6 to 100,001.
        elif n < 100001:
            
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
        '''"!pysearch" Returns a link to the forum with the keywords specified.
Default format is !pysearch <keywords>  Search for a user with format \
!pysearch !user <username>'''

        args = args[0].strip()

        #   Check if a member is wanted.
        if args.startswith('!user'):
            args = args[1:].split()
            return 'http://www.python-forum.org/pythonforum/memberlist.php?username=%s'\
                   % urllib.quote_plus(args[1])

        #   Return a link to a search if a member is not wanted.
        else:
            return 'http://www.python-forum.org/pythonforum/search.php?keywords=%s'\
                   % urllib.quote_plus(''.join(args))

    def say(self, *args):
        '''"!say" Forces me to say whatever you want me to!
Proper format is !say <keywords>'''

        self.parent.msg(chan, ''.join(args))
        return ''

    def wikipedia(self, *args):
        '''"!wiki" Returns a link to wikipedia with the keywords specified.
Proper format is !wiki <keywords>.  Get a summmary with the format !wiki 
!summary <keywords>'''

        words = args[0].strip()

        #   Check if a summary is wanted.
        if words.startswith('!summary'):

            #   Attempt to parse the first paragraph of the page requested, and
            #   remove HTML tags
            try:
                keywords = words[9:].replace(' ', '_').title()
                opener = urllib2.build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                infile = opener.open('http://en.wikipedia.org/wiki/%s'
                                     % keywords)
                page = infile.read()
                infile.close()
                first = re.split(r'\<\p\>', page)
                second = re.split(r'\<\/\p\>', first[1])
                summary = re.sub(r'\<.*?\>', '', second[0])

                #   If the page is a disambiguity page, recommend more detail.
                if re.search('may refer to:', summary):
                    return '%s is too vague.  Please be more specific.' \
                           % keywords

                #   Returns the first paragraph of the page requested.
                ##   Still needs flood control worked out.
                else:    
                    return summary

            #   Notify if the page does not exist.
            except urllib2.HTTPError:
                return '%s is not a valid article.' % keywords

        #   Return a link to a page if a summary is not requested.
        else:
            return 'http://en.wikipedia.org/wiki/%s' \
                   % ''.join(words).replace(' ', '_').title()

if __name__ in '__main__':
    '''Asks user for information: channel, nick, password, comlib and server.'''
    
    chan = '#confabot-test'
    nick = 'confabot'
#    nick = raw_input('Enter a nick: ')
    password = ''
#    password = raw_input('Enter a pass: ')
    log.startLogging(sys.stdout)
    reactor.connectTCP('irc.freenode.net',6667,
        TircFactory(chan, nick, password, COM))
    reactor.run()
