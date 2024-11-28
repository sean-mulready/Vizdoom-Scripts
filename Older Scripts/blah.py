import os
import vizdoom

# Find the path to the installed vizdoom package
vizdoom_path = os.path.dirname(vizdoom.__file__)
print(vizdoom_path)
