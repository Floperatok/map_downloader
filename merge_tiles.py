import os, sys
from PIL import Image


def merge_tiles(path, files_extension, zoom, dimensions):
	input_folder = f"{path}/raw"
	output_file_path = f"{path}/full_image.png"

	tile = Image.open(f"{input_folder}/{zoom}_0_0.{files_extension}")
	tile_size = tile.width
	
	width = dimensions["x"] * tile_size
	height = dimensions["y"] * tile_size

	print("Merging tiles")
	print(f"Full image dimensions: {width}x{height}")
	full_image = Image.new('RGBA', (width, height))

	for x in range(dimensions["x"]):
		for y in range(dimensions["y"]):
			tile_path = f"{input_folder}/{zoom}_{x}_{y}.{files_extension}"
			if os.path.exists(tile_path):
				tile_image = Image.open(tile_path)
				px = x * tile_size
				py = y * tile_size
				full_image.paste(tile_image, (px, py))
			else:
				print(f"Missing tile : {tile_path}")
	
	print("Saving the full image...")
	full_image.save(output_file_path)
	print(f"Tiles merged in {output_file_path}")

if __name__ == "__main__":
	if len(sys.argv) != 5:
		print("Usage: input_folder files_extension zoom dimensions")
		exit()
	merge_tiles(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
	# merge_tiles("maps/hitman/miami", "jpg", "16", {"x": 255, "y": 255})