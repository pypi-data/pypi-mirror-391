class GranuleTxt:
	"""Container for a granule boundary from a text file, similar to granule_locator.Granule."""
	def __init__(self, boundary_points, frame_idx, granule_id=0):
		self.boundary_points = boundary_points  # List of (x, y) tuples
		self.frame_idx = frame_idx
		self.granule_id = granule_id
		self.num_points = len(boundary_points)
		self.properties = {
			"frame": frame_idx,
			"granule_id": granule_id,
			"num_points": self.num_points,
			"centroid_x": self._centroid()[0],
			"centroid_y": self._centroid()[1],
		}
		self.image_centre = (self.properties["centroid_x"], self.properties["centroid_y"])

	def _centroid(self):
		if not self.boundary_points:
			return (0.0, 0.0)
		x = [p[0] for p in self.boundary_points]
		y = [p[1] for p in self.boundary_points]
		return (sum(x) / len(x), sum(y) / len(y))

	def to_dataframe(self):
		df = pd.DataFrame(self.boundary_points, columns=["x", "y"])
		df["frame"] = self.frame_idx
		df["granule_id"] = self.granule_id
		return df
#!/usr/bin/env python

"""
Extract the boundary points of a granule from a text file and process them to generate Fourier terms.

Each text file contains a single granule. The first line gives the number of points per frame, the second line is ignored, and the third line onwards are the xyz coordinates as tab-separated values. The z coordinate is ignored.
"""

import argparse
from pathlib import Path
import pandas as pd
import h5py
import platform
import pickle as pkl
import warnings
import tqdm
import os

from flickerprint.common.configuration import config
import flickerprint.version as version
import flickerprint.common.boundary_extraction as be

def parse_arguments():
	parser = argparse.ArgumentParser(description="Process granule boundary points from text file.")
	parser.add_argument("--input", type=Path, help="Path to input text file or directory of text files.", default=None)
	parser.add_argument("-o", "--output", type=Path, default=".", help="Directory for the output files.")
	parser.add_argument("-q", "--quiet", action="store_true", help="Suppress progress bar.")
	args = parser.parse_args()
	return args

def main(input_txt: Path = None, output_dir: Path = ".", quiet: bool = False):
	print(f"\n================\nText Processing\n================\n")

	config_location = Path(output_dir) / "config.yaml"
	print(f"\nConfiguration file location: {config_location}")
	config.refresh(config_location)

	if input_txt is None:
		raise ValueError("No input text file provided.")
	input_txt = Path(input_txt)

	if input_txt.is_dir():
		files = list(input_txt.glob("*.txt"))
		if not files:
			raise FileNotFoundError(f"No text files found in {input_txt}.")
		print(f"Text directory: {str(input_txt)}")
		print(f"Number of text files to process: {len(files)}\n")
		for idx, file in enumerate(files):
			process_single_txt(file, output_dir, quiet, idx)
	else:
		process_single_txt(input_txt, output_dir, quiet)

	print(f"\n\nText boundary analysis complete\n------------------------------\n")

def process_single_txt(input_txt: Path, output_dir: Path, quiet: bool = False, _pbar_pos: int = 0):
	config_location = Path(output_dir) / "config.yaml"
	config.refresh(config_location)
	output_dir = Path(output_dir)

	validate_args(input_txt, output_dir, quiet)

	print(f"#{_pbar_pos+1} Working on text file: {input_txt}")
	disable_bar = True if quiet else None
	process_bar = tqdm.tqdm([input_txt], disable=disable_bar, position=_pbar_pos, unit="file", desc=f"#{_pbar_pos+1}")


	# Read the text file and parse boundary points for each frame
	with open(input_txt, "r") as f:
		lines = [line.strip() for line in f if line.strip()]

	frame_idx = 0
	i = 0
	granule_objs = []
	frame_point_counts = []
	while i < len(lines):
		try:
			num_points = int(lines[i])
		except Exception:
			warnings.warn(f"Could not parse number of points at line {i+1} in {input_txt}.")
			break
		frame_point_counts.append(num_points)
		i += 2  # Skip the next line (ignored)
		boundary_points = []
		for j in range(num_points):
			if i + j >= len(lines):
				warnings.warn(f"Unexpected end of file when reading points for frame {frame_idx} in {input_txt}.")
				break
			parts = lines[i + j].split("\t")
			if len(parts) < 2:
				continue
			x, y = float(parts[0]), float(parts[1])
			boundary_points.append((x, y))
		granule = GranuleTxt(boundary_points, frame_idx, granule_id=0)
		granule_objs.append(granule)
		i += num_points
		frame_idx += 1

	if not granule_objs:
		print(f"No valid frames found in {input_txt}.")
		return

	# Use BoundaryExtraction for each frame
	boundary_method = "intensity"
	boundaries = [be.BoundaryExtraction(granule, boundary_method) for granule in granule_objs]
	# Collect Fourier terms for all frames
	fourier_terms = be.collect_fourier_terms(boundaries, None, None, False, output_dir)

	# Save results
	save_name = f"fourier/{input_txt.stem}"
	save_path = output_dir / (save_name + ".h5")
	frame_data = {
		"num_frames": len(granule_objs),
		"frame_point_counts": frame_point_counts,
		"input_path": str(input_txt.resolve()),
	}
	hdf_save_path = save_path.with_suffix(".h5")
	print(f"\n#{_pbar_pos+1} Fourier file save location: {hdf_save_path}\n")
	write_hdf(hdf_save_path, fourier_terms, frame_data)

def validate_args(input_txt: Path, output_dir: Path, quiet: bool = False):
	if not input_txt.exists():
		raise FileNotFoundError(f"Provided text file does not exist: {input_txt}")
	if not output_dir.is_dir():
		raise IOError(f"Provided output_dir is not directory: {output_dir}")

def write_hdf(save_path: Path, fourier_frames: pd.DataFrame, frame_data):
	if platform.system()=="Darwin" and "ARM64" in platform.version():
		try:
			fourier_frames.to_hdf(save_path, key="fourier", mode="w", complib="bzip2")
			with h5py.File(save_path, "a") as f:
				fourier_hdf = f["fourier"]
				for key, val in frame_data.items():
					fourier_hdf.attrs[key] = val
				config_yaml, _ = config._aggregate_all()
				fourier_hdf.attrs["config"] = config_yaml
				fourier_hdf.attrs["version"] = version.__version__
		except:
			config_yaml, config_summary = config._aggregate_all()
			file = open(f'{str(save_path)[:-3]}.pkl', 'wb')
			pkl.dump({'fourier': fourier_frames, "frame_data": frame_data, "configuration": config_yaml, "version": version.__version__}, file=file)
	else:
		fourier_frames.to_hdf(save_path, key="fourier", mode="w", complib="bzip2")
		with h5py.File(save_path, "a") as f:
			fourier_hdf = f["fourier"]
			for key, val in frame_data.items():
				fourier_hdf.attrs[key] = val
			config_yaml, _ = config._aggregate_all()
			fourier_hdf.attrs["config"] = config_yaml
			fourier_hdf.attrs["version"] = version.__version__

if __name__ == "__main__":
	args = parse_arguments()
	main(args.input, args.output, args.quiet)
