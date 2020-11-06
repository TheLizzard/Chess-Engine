# Use the updater to reset the app by ckearing files.txt
import Networking.updater as updater
with open("files.txt", "w") as file:
    file.write("")
updated = updater.update()

# Start the updated program
import main
