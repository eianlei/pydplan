# Source code documentation

The pyplan application consists of following Python files:
1. pydplan_main.py
1. pydplan_classes.py
1. pydplan_plot.py
1. pydplan_profiletools.py
1. pydplan_buhlmann.py
1. pydplan_bars.py
1. pydplan_heat.py
1. pydplan_table.py

They have the following purpose:

file | purpose
------------ | -------------
pydplan_main.py | the PyQt5 GUI defined here, call this module to start the app
pydplan_classes.py | major classes used by the app
pydplan_plot.py | PyQt5 plotting functions, custom widgets using QPainter()
pydplan_profiletools.py | the calculation of dive profile
pydplan_buhlmann.py | Buhlmann model
pydplan_bars.py | code that implements the tab "Bars" panel
pydplan_heat.py | the heat map plotting
pydplan_table.py | TABLE view plotting


# modules
## pydplan_main.py

class pydplan_main(QMainWindow) implements the main window of the application GUI. All of the UI widgets that are used to configure something are here.

The widgets connect to a few callback handlers, but the most important one is drawNewProfile(), which recalculates the Buhlmann model using the configured dive profile.

The object self.divePlan contains all the data of a dive profile and the Buhlmann model states that are calculated for the profile.

## pydplan_classes.py
## pydplan_plot.py
## pydplan_profiletools.py
## pydplan_buhlmann.py
## pydplan_bars.py
## pydplan_heat.py
## pydplan_table.py