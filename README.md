# Dark Pool Simulator

For my final year project, I created a simulator of a financial exchange that is based on the London Stock Exchange's Turquoise Plato trading service. Turquoise Plato is a dark pool exchange. The simulator includes an implementation of the Block Discovery service which is used for facilitating the trading of larger block orders. I also created a simple trading algorithm based on the Giveaway trading algorithm that can operate in the simulator.

The simulator is intended to be an extension to the Bristol Stock Exchange (BSE). BSE is a lit pool simulator that is used for the testing of automated trading algorithms.

The simulator is written in Python 2.7. The `dark_pool` folder contains the implementation.

## Simulator Details:

- The exchange has a single tradable security.
- A trader can have at most 1 order in the exchange at any point in time. 
- The price of the security in each trade is meant to be determined by the mid-price on a coupled lit pool. It is currently set to a fixed value.
- The simulator is single threaded. 
- It is intended to be run in batch mode, writing data to CSV files for subsequent analysis, rather than having a GUI.
- traders receive customer orders specifying a quantity to traded and a limit price. The goal of the trader is to maximise the margin that they can make on each trade.
- The supply and demand schedules of customer orders can be customised.


For more information, see [thesis.pdf](https://github.com/gchurch/DarkPoolSimulator/blob/master/thesis.pdf). 
