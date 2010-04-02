import tables as pt
from models.PositionModel import PositionModel
'''
Based on the model:
PositionModel:
    timestamp = pt.Time64Col()
    symbol = pt.StringCol(4) 
    shares = pt.Int32Col()
    open_price = pt.Int32Col()
'''

class Position:
    def __init__(self):
        self.positionFile = pt.openFile('PositionModel.h5', mode = "w")
        self.position = self.positionFile.createTable('/', 'position', PositionModel)

    def addPosition(self,timestamp,symbol,shares,open_price):
        row = self.position.row
        row['timestamp'] = timestamp
        row['symbol'] = symbol 
        row['shares'] = shares
        row['open_price'] = open_price
        row.append()
        self.position.flush()
    
    def removePosition(self, symbol, shares, closeType):
        '''
        symbol: the representation of the shares to be removed
        shares: the number of shares to remove
        closeType: removal order "lifo" or "fifo"
        Removes/modifies positions until the total number of shares have been removed
        NOTE: Method assumes that verification of valid sell has already been completed
        '''
        rowIndexes = []
        rows = []
        debug = False
        if debug:
            print 'REMOVING POSITIONS'
            print 'REMOVE:',symbol,shares,closeType
            for row in self.position.iterrows():
                print 'CURRROWS:', row
        for row in self.position.where("symbol=='%s'"%symbol):
            if debug:
                print 'SELEROWS:', row  
            rows.append(self.cloneRow(row))
            rowIndexes.append(row.nrow)
        if(closeType=='fifo'):
            if debug:
                print 'FIFO', row
            i = 0
            row = rows[i]
            posShares = row['shares']            
            while(shares>posShares):
                shares-=posShares
                i+=1
                row = rows[i]
                posShares = row['shares']
            cnt=0
            while cnt<i:                
                self.position.removeRows(rowIndexes[cnt]-cnt,rowIndexes[cnt]-cnt+1)
                self.position.flush()
                cnt+=1
                if debug:
                    print 'ROWREMOVED', row
            cnt=0
            for newRow in self.position.where('(symbol=="%s") & (timestamp==%i)'%(symbol,row['timestamp'])):
                if(cnt==0):
                    newShares = posShares-shares
                    newRow['shares'] = newShares
                    newRow.update()
                    if debug:
                        print 'UPDATEDROW(FIFO):', newRow
                cnt+=1
            self.position.flush()
                
        elif(closeType=='lifo'):
            if debug:
                print "LIFO",row
            i = len(rows)-1
            row = rows[i]
            posShares = row['shares']        
            while(shares>posShares):
                shares-=posShares
                i-=1
                row = rows[i]
                posShares = row['shares']
            cnt=0
            i+=1
            while i<len(rows)-1:
                self.position.removeRows(rowIndexes[i]-cnt,rowIndexes[i]-cnt+1)
                self.position.flush()
                i+=1
                cnt+=1
                if debug:
                    print 'ROWREMOVED', row
            cnt=0
            for newRow in self.position.where('(symbol=="%s") & (timestamp==%i)'%(symbol,row['timestamp'])):
                if(cnt==0):
                    newShares = posShares-shares
                    newRow['shares'] = newShares
                    newRow.update()
                    if debug:
                        print 'UPDATEDROW(LIFO):', newRow
                cnt+=1
            self.position.flush()
        else:
            #invalid type
            raise TypeError("Not an existing close type '%s'." % str(newOrder.order_type))
  
    def cloneRow(self,row):
        dct = {}  
        dct['timestamp'] = row['timestamp']
        dct['symbol'] = row['symbol']
        dct['shares'] = row['shares']
        dct['open_price'] = row['open_price']     
        return dct
    
    def close(self):
        self.positionFile.close()
