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

| Key             | Description                                                                                |
| --------------- | ------------------------------------------------------------------------------------------ |
| fileDir         | Input directory                                                                            |
| fileExts        | Legal file extensions to rename, default is video files                                    |
| getInfoInterval | Time interval to retrieve data from javlibrary in second, do not set too small             |
| fileNameFormat  | Format of new file name, see more below                                                    |
| language        | `tw`, `cn`, `en`, `ja`                                                                     |
| saveAlbum       | Save album image in the same directory of video file                                       |
| dryRun          | Run without real execution                                                                 |
| maxFileLength   | Maximum file name length in bytes, reduce this value if "file name too long" error happens |
| minFileSizeMB   | Minimum file size(in MB) to execute                                                        |

### Tags in fileNameFormat

Recommend to use `{bangou}` in order to do rename later.

| Tags       | Description                                                     |
| ---------- | --------------------------------------------------------------- |
| {bangou}   | The serial number of jav                                        |
| {title}    | Title may include actors' name, guarantee not include bangou    |
| {tags}     | Tags in javlibrary                                              |
| {director} |                                                                 |
| {maker}    | Maker of the video, usually related to the first part of bangou |
| {actors}   |                                                                 |
| {length}   | The length of video in minutes                                  |
| {date}     | Release date                                                    |
| {rate}     | Rating in javlibrary                                            |
| {album}    | Link of album image, **not recommend to use**                   |
| {thumbs}   | Link of thumbnails, **not recommend to use**                    |

## Database

All queries will be saved in `db-{language}.json`.

You can do dry run to check the rename progress and then execute without retrieving data again.

Failed requests will also be saved, clean database if something looks wrong.

## Note

- input file name should include bangou, or rename will fail
- if there exist multiple files that have the same bangou, they will be renamed with number, ordered by original file name

## Future Work

- Execute
  - save thumbnails
  - fill video metadata in file
  - options for new folder
  - options to ask before every rename operation
- FileName
  - update different bangou
- Info
  - add info sources website
- UI
  - interface to search database

## Reference

- [javlibrary](http://javlibrary.com)
