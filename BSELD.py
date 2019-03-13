# import BSE and dark_pool modules
import BSE
import dark_pool

import sys

def experiment3():

    start_time = 0.0
    end_time = 180.0

    range1 = (10,190)
    range2 = (200,300)

    supply_sched = [ {'from':0, 'to':60, 'ranges':[range1], 'stepmode':'fixed'},
                  {'from':60, 'to':120, 'ranges':[range2], 'stepmode':'fixed'},
                  {'from':120, 'to':180, 'ranges':[range1], 'stepmode':'fixed'}]
    demand_sched = supply_sched

    order_sched = {'sup':supply_sched, 'dem':demand_sched, 'interval':30, 'timemode':'drip-fixed'}

    buyers_spec = [('ZIP',40)]
    sellers_spec = buyers_spec
    traders_spec = {'sellers':sellers_spec, 'buyers':buyers_spec}

    # run a sequence of trials, one session per trial

    n_trials = 1
    tdump=open('avg_balance.csv','w')
    trial = 1
    if n_trials > 1:
            dump_all = False
    else:
            dump_all = True
            
    while (trial<(n_trials+1)):
            trial_id = 'trial%04d' % trial
            BSE.market_session(trial_id, start_time, end_time, traders_spec, order_sched, tdump, dump_all)
            tdump.flush()
            trial = trial + 1
    tdump.close()

    sys.exit('Done Now')

def main():
	experiment3()

if __name__ == "__main__":
	main();