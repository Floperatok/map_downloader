import os
import requests
import time
import datetime
import asyncio
import aiohttp
from time import sleep


async def download_tile_async(session, url, path):
	async with session.get(url) as response:
		if response.status == 200:
			with open(path, 'wb') as file:
				file.write(await response.read())
		else:
			print(f"Error {response.status} when downloading {url}")


def detect_map_start(url, map_valid_coord, zoom):
	print(f"Detecting map starting point for zoom {zoom}...")

	response = requests.get(url.format(x=map_valid_coord["y"], y=map_valid_coord["y"], z=zoom), stream=True)
	if response.status_code != 200:
		print(f"Failed to detect map starting point, make sure the coordinates you gave was valids")
		exit()

	x = map_valid_coord["x"]
	y = map_valid_coord["y"]
	while True:
		response = requests.get(url.format(x=x, y=map_valid_coord["y"], z=zoom), stream=True)
		if response.status_code != 200:
			break
		x -= 1
	
	while True:
		response = requests.get(url.format(x=map_valid_coord["x"], y=y, z=zoom), stream=True)
		if response.status_code != 200:
			break
		y -= 1

	x += 1
	y += 1
	print(f"Start: [{x},{y}]")
	return ({"x": x, "y": y})


def detect_map_dimensions(url, zoom, start):
	failed = 0
	last_good = {"x": 0, "y": 0}
	print(f"Detecting map dimensions for zoom {zoom}...")
	
	x = start["x"]
	y = start["y"]
	while True:
		response = requests.get(url.format(x=x, y=start["y"], z=zoom), stream=True)
		if response.status_code != 200:
			failed += 1
		else:
			last_good["x"] = x
		if failed > 10:
			break
		x += 1

	failed = 0
	while True:
		response = requests.get(url.format(x=start["x"], y=y, z=zoom), stream=True)
		if response.status_code != 200:
			failed += 1
		else:
			last_good["y"] = y
		if failed > 10:
			break
		y += 1
	x = last_good["x"]
	y = last_good["y"]
	if (x == 0 or y == 0):
		print(f"Failed to detect map dimensions, make sure the map you are trying to download starts at [{start["x"]},{start["y"]}]")
		exit()
	print(f"dimensions: {x-start["x"]}x{y-start["y"]}")
	x = x - start["x"]
	y = y - start["y"]
	return ({"x": x, "y": y})


async def download_map(formatted_url, zoom, map_valid_coord, output_folder):
	output_folder = f"{output_folder}/raw"


	start = detect_map_start(formatted_url, map_valid_coord, zoom)
	dimensions = detect_map_dimensions(formatted_url, zoom, start)

	file_extension = formatted_url.split(".")[-1]

	print(f"Downloading...")

	async with aiohttp.ClientSession() as session:
		tasks = []
		for x in range(dimensions["x"]):
			for y in range(dimensions["y"]):
				tile_url = formatted_url.format(x=x+start["x"], y=y+start["y"], z=zoom)
				tile_path = f"{output_folder}/{zoom}_{x}_{y}.{file_extension}"
				
				tasks.append(download_tile_async(session, tile_url, tile_path))
		await asyncio.gather(*tasks)
	print("done.")
	return (dimensions)