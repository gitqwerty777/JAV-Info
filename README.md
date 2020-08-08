## Requirement

- Python3.5 or newer
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
|maxFileLength | maximum file name length in bytes, reduce this value if you meets `file name too long` error |

### Tags in fileNameFormat

Recommend to use {bangou} in file name in order to rename later.

| label    | description              |
|----------|--------------------------|
| {bangou} | the serial number of jav |
| {title}  | title may include actors' name, but not include bangou |
| {tags}   | tags in [javlibrary](http://www.javlibrary.com/) |
| {director} |  |
| {maker}  | maker of the video, usually related to the first part of bangou |
| {actors} | |
| {length} | the length in minutes of video |
| {date}   | release date |
| {rate}   | rating in [javlibrary](http://www.javlibrary.com/) |
| {album}  | album image link, **not recommend to use** |
| {thumbs} | thumbnail's link, **not recommend to use** |

## db-{language}.json

Any query will be saved in `db-{language}.json` in order to save time.

You can do dry run to see the result and then execute without retrieving data again.
