A simple tool to rename video files by jav unique id(bangou).

## Requirement

- Python3.5 or newer
- install following python packages

```
pip install requests
pip install beautifulsoup4
pip install colorama
```

## Usage

`python main.py`

## Config

Change config in `config.json`

| Key  | Description|
|------|------|
|fileDir | Input file directory, related path |
|fileExts | Legal input file extensions|
|getInfoInterval | Time interval to retrieve data from javlibrary in second, do not set too small |
|fileNameFormat | Format of new file name, see more below |
|language | `tw`, `cn`, `en`, `ja` |
|saveAlbum | Save album image in the same directory of video file|
|dryRun | Run without real execution |
|maxFileLength | Maximum file name length in bytes, reduce this value if you meets "file name too long" error |

### Tags in fileNameFormat

Recommend to use `{bangou}` in order to do rename later.

| Tags    | Description              |
|----------|--------------------------|
| {bangou} | The serial number of jav |
| {title}  | Title may include actors' name, but not include bangou |
| {tags}   | Tags in javlibrary |
| {director} |  |
| {maker}  | Maker of the video, usually related to the first part of bangou |
| {actors} | |
| {length} | The length of video in minutes |
| {date}   | Release date |
| {rate}   | Rating in javlibrary |
| {album}  | Link of album image, **not recommend to use** |
| {thumbs} | Link of thumbnails, **not recommend to use** |

## Database

Any query will be saved in `db-{language}.json` in order to save time.

You can do dry run to see the result and then execute without retrieving data again.

## Reference

- [javlibrary](http://javlibrary.com)
