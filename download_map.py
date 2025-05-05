from download_tiles import download_map
from merge_tiles import merge_tiles
import os, sys, json, asyncio


def hex_to_rgb(hex_color):
	hex_color = hex_color.lstrip('#')
	r = int(hex_color[0:2], 16)
	g = int(hex_color[2:4], 16)
	b = int(hex_color[4:6], 16)
	return f"{r} {g} {b} 255"

def is_valid_hex_color(hex_color):
	if hex_color[0] != '#' or len(hex_color) != 7:
		return False
	try:
		int(hex_color[1:], 16)
	except ValueError:
		return False
	return True

def user_confirmation():
	while True:
		confirmation = input("Confirm ? [Y/n]: ")
		confirmation = confirmation.lower().strip()
		if confirmation == "y" or confirmation == "yes" or confirmation == "":
			break
		elif confirmation == "n" or confirmation == "no":
			exit()


JPG_COMPRESSION = 90

game_name = []
formatted_url = []
zoom = []
output_folder = []
background_color = []
map_valid_coord = []


if len(sys.argv) != 2:
	print("Usage: python download_map.py [conf_file.json]")
	exit()
try:
	f = open(sys.argv[1], "r", encoding="UTF-8")
	data = json.load(f)
	for i in range(len(data["maps"])):
		game_name.append(data["maps"][i]["game_name"])
		formatted_url.append(data["maps"][i]["formatted_url"])
		zoom.append(data["maps"][i]["zoom"])
		output_folder.append(data["maps"][i]["output_folder"])
		background_color.append(data["maps"][i]["background_color"])
		map_valid_coord.append(data["maps"][i]["map_valid_coord"])
except OSError:
	print(f"Error: {sys.argv[1]} not found")
	exit()
except json.JSONDecodeError:
	print(f"Invalid json document at {sys.argv[1]}")
	exit()


for i in range(len(game_name)):
	# DEFAULT VALUES
	if output_folder[i] == "":
		output_folder[i] = f"maps/{game_name[i]}"
	if background_color[i] == "":
		background_color[i] = "#000000"

	# ERROR CHECKING
	if game_name[i] == "":
		print(f"ERROR: game_name cannot be empty")
		exit()
	if zoom[i] == "":
		print(f"ERROR: zoom cannot be empty")
	try:
		int(zoom[i])
	except ValueError:
		print(f"ERROR: '{game_name[i]}' invalid zoom: {zoom[i]}")
		exit()
	if formatted_url[i].find("{x}") == -1:
		print(f"ERROR: x variable not found in {formatted_url[i]}")
		exit()
	if formatted_url[i].find("{y}") == -1:
		print(f"ERROR: y variable not found in {formatted_url[i]}")
		exit()
	if formatted_url[i].find("{z}") == -1:
		print(f"ERROR: z variable not found in {formatted_url[i]}")
		exit()
	if not is_valid_hex_color(background_color[i]):
		print(f"ERROR: '{game_name[i]}' invalid color: {background_color[i]}")
		exit()
	if map_valid_coord[i]["x"] == "" or map_valid_coord[i]["y"] == "":
		print(f"ERROR: '{game_name[i]}' please enter map valid coordinates")
		exit()
	try: 
		int(map_valid_coord[i]["x"])
		int(map_valid_coord[i]["y"])
	except ValueError:
		print(f"ERROR: '{game_name[i]}' invalid coordinates: {map_valid_coord[i]["x"]},{map_valid_coord[i]["y"]}")
		exit()

	# SUMMARY
	print(f"MAP {i + 1}")
	print(f"Game name             = {game_name[i]}")
	print(f"URL                   = {formatted_url[i]}")
	print(f"Zoom                  = {zoom[i]}")
	print(f"Output folder         = {output_folder[i]}")
	print(f"Background color      = {background_color[i]}")
	print(f"Map valid coordinates = [{map_valid_coord[i]["x"]},{map_valid_coord[i]["y"]}]")
	print("\n")

user_confirmation()

# FOLDERS CREATION
for i in range(len(game_name)):
	if os.path.exists(output_folder[i]):
		print(f"\nWARNING: {output_folder[i]} folder already exists. It will be overwritten.")
		user_confirmation()
		os.system(f"rm -rf {output_folder[i]}")
	os.makedirs(output_folder[i])
	os.makedirs(f"{output_folder[i]}/raw")
	os.makedirs(f"{output_folder[i]}/tiles")

# DOWNLOADING...
for i in range(len(game_name)):
	print(f"{game_name[i].capitalize()}")
	dimensions = asyncio.run(download_map(formatted_url[i], zoom[i], map_valid_coord[i], output_folder[i]))
	merge_tiles(output_folder[i], formatted_url[i].split(".")[-1], zoom[i], dimensions)
	print("Creating tiles...")
	os.system(f"""vips dzsave {output_folder[i]}/full_image.png {output_folder[i]}/tiles --layout google --background \"{hex_to_rgb(background_color[i])}\" --centre --suffix .png --tile-size 256""")
	print(f"Converting png tiles to jpg with compression level = {JPG_COMPRESSION}")
	os.system(f"""find {output_folder[i]}/tiles -name "*.png" -exec bash -c 'magick "$0" -background "{background_color[i]}" -flatten -quality {JPG_COMPRESSION} "${{0%.png}}.jpg"' {{}} \\;""")
	os.system(f"""find {output_folder[i]}/tiles -name "*.png" -exec rm -f {{}} \\;""")
	print("\n")
