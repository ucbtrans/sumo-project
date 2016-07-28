This is an example of platooning on the Huntington-Colorado network. The functions are stored in the platoon_functions file and called in runner-platooning.

Settings.py contains the global variables used in both platoon_functions and runner-platooning. In order to properly use these in conjunction, the global variables must be initialized and defined in settings.py to prevent an duplicate variables. In the remaining files, settings must be imported (import settings) at the beginning of the file.

Finally, in the runner file, two calls must be made. The runner must import settings, initialize the variables by calling settings, and then import the remaining functions that use the variables. Hence, the runner must contain the following string of lines...

...

import settings

settings.init() #initializes the global variables

from platoon_functions import * #import all the functions

...


runner-platooning is an example of how to implement platooning on the network.
