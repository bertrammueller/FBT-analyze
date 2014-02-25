import time
import sys
import fbcommunication
import post_analysis
import trade
import notification

reload(post_analysis)

FBT_GROUP_ID = '200260546685575'
ORKAN_ID = '100001920246476'

AUDIO_FILE = 'audio/phone_ring2.wav'
N_TVK = 2 # Anzahl maximaler Teilverkaufe
LONG = 0
SHORT = 1

fbcomm = fbcommunication.FBComm(FBT_GROUP_ID, ORKAN_ID)

# Check if manual time adjustment in system arguments
if len(sys.argv) > 1:
    delta_s = int(sys.argv[1])*60 # In minutes
else:
    delta_s = 0
last_update = fbcomm.get_updatetime()-1 - delta_s

# Analysing Functions
def analyse_messages(messages, active_trade):
    analysis = post_analysis.Dax()
    for m in messages:
        if analysis.find(m['message']):
            print m['message']
            notification.play_audio(AUDIO_FILE)
            
            if active_trade:
                # Trade is still active -> close it
                # TODO: Check if previous trade was stopped out
                print 'Previous trade still active -> aborted'
                return active_trade
            else:
                # Execute trade
                longshort = analysis.get_longshort(m['message'])
                start = analysis.get_start(m['message'])
                stop = analysis.get_stop(m['message'])
                if stop > 100:
                    # The stop is denoted as distance from trade start
                    stop = (start - stop) if (longshort == LONG) else (stop - start)
                
                print '@ {}'.format(start)
                print 'Long' if longshort == LONG else 'Short'
                print 'Stop {}'.format(stop)
                print 'Executing Trade...'
                active_trade = trade.Trade(m['post_id'], 'dax', start, N_TVK, longshort, stop)
                print 'Checking if Trade is active...'
                time.sleep(0.2)
                if active_trade.is_active():
                    print 'Trade active with id ' + active_trade.trade_id
                    return active_trade
                else:
                    print 'ERROR: Trade not open'
                    return None

def analyse_comments(comments, active_trade):
    analysis = post_analysis.Dax()
    for c in comments:
        if analysis.find_tvk(c['text']):
            print 'Comment: ' + c['text']
            notification.play_audio(AUDIO_FILE)
            # Close one contract
            active_trade.close_position(1)
            if active_trade.num_contracts == 0:
                print 'Trade completed'
                return None # Trade completed
    
    return active_trade

# Main Loop
active_trade = None
while True:
    update_time = fbcomm.get_updatetime()
    if update_time > last_update:
        print 'Update: ' + time.asctime(time.localtime(update_time))
        # Messages
        messages = fbcomm.read_stream(last_update)
        active_trade = analyse_messages(messages, active_trade)
        # Comments
        if active_trade:
            comments = fbcomm.read_comments(active_trade.trade_id, last_update)
            active_trade = analyse_comments(comments, active_trade)

        last_update = fbcomm.get_updatetime()

    time.sleep(10)


