#-------------------------------------------------------------------------------
# Name:        module1

from BaseHTTPServer import BaseHTTPRequestHandler
from robot import Robot
from pipetter import Pipette
from deck import Point, Well

class PostHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):   #This function suppresses the log message. Disable this function if u wan to see log in console.
        return

    def do_POST(self):
        # Parse the form data posted
        #The following keywords can be sent:
        #   home, aspirate, dispense, mix,
        #   aspirate
        #If parameter(s) is needed, use : to delimit the keywords and parameters. * means that parameter is needed.
        data = self.rfile.read(int(self.headers.getheader('content-length', 100)))

        # Begin the response
        self.send_response(200)
        self.end_headers()
        if not data.startswith(('Quote','Time','Asset','Balance')):
            print data      #debug

        if data.startswith('Login'):
            s = data.split(':')
            if b.login(s[1],s[2]) == "Error in Login":
                self.wfile.write('Error')
                return
            self.wfile.write("Login Successful")

        elif data == 'Time':
            #if b.is_closed:
            #    self.wfile.write('Error')
            #    raise RuntimeError
            if b.time:
                now = datetime.datetime.utcfromtimestamp(float(b.time))
            else:
                now = datetime.datetime.utcnow()
            if now.minute == 0:
                print b.tradeHistory       #alternatively with json dumps indent = 4
            oleTime = convertTime(now,True)
            self.wfile.write(str(oleTime))

        elif data.startswith(('Call','Put')):
            #example string: Call:EURUSD:10
            s = data.split(':')
            if s[1].endswith('binary'):
                s[1] = s[1][:-6]
            instrument = s[1][:3]+'/'+s[1][-3:]
            if len(s) < 3:
                self.wfile.write('Error in buying, Wrong Format')
                return
            try:
                deposit = abs(int(s[2]))
            except ValueError:
                deposit = abs(float(s[2]))
            for j in xrange(20):
                b.purchase(instrument,s[0],deposit)
                global oldTradeList
                print oldTradeList
                for i in xrange(120):
                    if b.tradeError:
                        break
                    if len(b.tradeHistory) > len(oldTradeList):
                        for key in b.tradeHistory.keys():
                            if key not in oldTradeList:
                                trade = b.tradeHistory[key]
                                self.wfile.write(str(key)+':'+str(trade['value']))       #price and id, no need time due to conversion
                                print str(key)+':'+str(trade['value'])
                                oldTradeList = b.tradeHistory.keys()
                                break
                        break
                    else:
                        time.sleep(0.5)
                if b.tradeError:
                    time.sleep(0.1)
                    b.tradeError = False
                else:
                    break

        elif data.startswith('Payout'):     #(Not yet) has been implemented in broker dll
            #example: Payout:EURUSD or Payout:EUR/USD.
            #Dun implement it on all asset as some of the asset is not available for the dll.
            s = data.split(':')
            if s[1].endswith('binary'):
                s[1] = s[1][:-6]
            instrument = s[1][:3]+'/'+s[1][-3:]
            self.wfile.write(b.getPayout(instrument))

        elif data == 'Balance':
            self.wfile.write(b.getBalance())

        elif data.startswith('Asset'):      #maybe can remove this part. Check the broker dll.  #no need to remove
            #example: Asset:EURUSD
            s = data.split(':')
            if s[1].endswith('binary'):
                s[1] = s[1][:-6]
            instrument = s[1][:3]+'/'+s[1][-3:]
            if instrument in b.asset:
                self.wfile.write('Asset available')
            else:
                self.wfile.write('Asset not available')

        elif data.startswith('Subscribe'):
            #example: Subscribe:EURUSD
            s = data.split(':')
            if s[1].find(',') > -1:
                instrument = s[1].split(',')        #check this code again. I think it will never be used.
            else:
                if s[1].endswith('binary'):
                    s[1] = s[1][:-6]
                instrument = s[1][:3]+'/'+s[1][-3:]
            if type(instrument) == list or (type(instrument) != list and instrument in b.asset):
                b.subscribeAsset(instrument)
            self.wfile.write('Subscribed')

        elif data.startswith('Quote'):
            #example: Quote:EURUSD
            s = data.split(':')
            if s[1].endswith('binary'):
                s[1] = s[1][:-6]
            instrument = s[1][:3]+'/'+s[1][-3:]
            self.wfile.write(b.getQuote(instrument))   #the quote is in unicode string

        elif data.startswith('History'):
            #example: History:EURUSD:startDate:endDate:15
            # path = r'C:\Users\User\tempData.csv'
            path = os.getcwd()+'tempData.csv'
            s = data.split(':')
            if s[1].endswith('binary'):
                s[1] = s[1][:-6]
            instrument = s[1][:3]+'/'+s[1][-3:]
            b.history(instrument,s[2],s[3])    #quotes is dataframe
            time.sleep(10)

            if instrument not in b.candleHistory:
                print 'Error in candleHistory'
            df = b.candleHistory[instrument]
            '''
            df = df.sort_values(by='epoch',ascending = False)
            b.history(instrument,s[2],convertTime(df['epoch'].iloc[-1]))
            time.sleep(5)

            if instrument not in b.candleHistory:
                print 'Error in candleHistory'
            df = df.append( b.candleHistory[instrument])
            df = df.drop_duplicates()
            '''
            df['epoch'] = df['epoch'].apply(lambda x:datetime.datetime.utcfromtimestamp(x))
            df = df.sort_values(by='epoch',ascending = False)     #epoch is in datetime format, converted by previous line.
            #df['epoch'] = df['epoch'].apply(lambda x:filterTime(x))
            #print df['epoch'][0]
            # debug
            #df = pd.read_csv('C:\\Users\\user\\tData.csv', names=['epoch', 'open', 'high', 'low', 'close'])
            #df['epoch'] = pd.to_datetime(df['epoch'])
            # end debug
            df['epoch'] = df['epoch'].apply(lambda x:convertTime(x,True))
            #df = df[df['epoch'] <= s[2]]
            df.to_csv(path,header = False,columns = ['epoch','open','high','low','close'],index = False)

            start = df['epoch'].iloc[0]
            end = df['epoch'].iloc[-1]
            print start,end

            self.wfile.write(path)  #try to add exception handler here.

        elif data.startswith('Trade'):      #not yet implemented. need to check the direction. add direction field into tradeHistory list.
            #example: Trade:id
            s = data.split(':')
            if int(s[1]) not in b.tradeHistory:
                self.wfile.write("Error")
                return
            thisTrade = b.tradeHistory[int(s[1])]
            for k,v in b.asset.iteritems():
                if v == str(thisTrade['id']):
                    instrument = k
                    break
            else:
                print 'Default instrument used'
                instrument = 'EUR/USD'
            if float(thisTrade['value']) < float(b.getQuote(instrument)):
                if thisTrade['direction'].lower() == 'put':
                    self.wfile.write("Lose:"+str(thisTrade['deposit']))   #lose
                elif thisTrade['direction'].lower() == 'call':
                    self.wfile.write(str(thisTrade['deposit'])+":"+str(thisTrade['payout']))   #win
            elif float(thisTrade['value']) > float(b.getQuote(instrument)):
                if thisTrade['direction'].lower() == 'put':
                    self.wfile.write(str(thisTrade['deposit'])+":"+str(thisTrade['payout']))   #win
                elif thisTrade['direction'].lower() == 'call':
                    self.wfile.write("Lose:"+str(thisTrade['deposit']))   #lose
            else:
                self.wfile.write('Atm'+":"+str(thisTrade['deposit']))

        elif data.startswith('Close'):
            #example: Close:id
            s = data.split(':')
            closed = b.sell(s[1])
            if closed:
                self.wfile.write('Close successful')
            else:
                self.wfile.write('Error in closing')
        return

def main():
    from BaseHTTPServer import HTTPServer
    print 'Starting Server.. Waiting for 5 seconds'
    tip = Point('rack1')
    trash = Point('dustbin1')
    p = Pipette('p20',trash,tip,20)
    r = Robot(p)
    server = HTTPServer(('localhost', 8750), PostHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        r.force_stop()  #check again
        print 'Terminated'

if __name__ == '__main__':
    main()



