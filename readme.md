# Pornsorter

A quick and dirty thing for sorting out wallpapers ripped from places like /r/EarthPorn. (I use [RipMe](https://github.com/RipMeApp/ripme).) Or wallpaper-size actual porn. I don't care, you filthy animal.

## Usage

python3 pornsorter.py \<dir_to_scan\> \<dir_to_move_to\>

Aspect ratios can be set with `--aspect` and minimum resolutions with
`--min_x` and `--min_y`. Use `--aspect_tol` to allow a relative tolerance for
matching aspect ratios (e.g. `0.05` for ±5%).

## Dependencies

* Pillow / PIL
