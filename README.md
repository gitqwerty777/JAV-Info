## Requirement

- Python3.5
- install following python packages

```
pip install beautifulsoup4
pip install colorama
```

## Usage

`python getInfo.py`

## config.json

| key  | description|
|------|------|
|fileDir | input file directory, related path |
|fileExts | legal input file extensions|
|getInfoInterval | time interval(second) to retrieve data from [javlibrary](http://www.javlibrary.com/), do not set too small |
|fileNameFormat | the format of new file name, see below |
|language | `tw`, `cn`, `en`, `ja` |
|saveAlbum | save album image in the same directory of video file|
|dryRun | run without real execution |

### Tags in fileNameFormat

| label    | description              |
|----------|--------------------------|
| {bangou} | the serial number of jav |
| {title}  | |
| {tags}  | tags in [javlibrary](http://www.javlibrary.com/) |
| {director}  |  |
| {maker}  | maker of the video, usually related to the first part of bangou |
| {actors}  | |
| {length} | the length of video |
| {date} | release date |
| {album} | album image |
| {thumbs} | thumbnails |
| {rate} | rating in [javlibrary](http://www.javlibrary.com/) |

## db.json

Any query will be saved in `db.json` in order to save time.

You can do dry run to see the result and then execute without retrieving data again.
