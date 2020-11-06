# Use the updater to reset the app by clearing
# files.txt and updating the program
import Networking.updater as updater
with open("files.txt", "w") as file:
    file.write("")
updated = updater.update()

# Start the updated program
import main
