# JAV-Info

> A simple tool to rename local video files, download album image and thumbnails images using jav unique id(bangou)

## Demo

- ![Demo](demo.gif)

## Usage

Download Windows(.exe) version at release or using Python

### Python Requirement

- Python3.6 or newer
- install following python packages

```
pip install requests
pip install beautifulsoup4
pip install colorama
```

Usage: `python main.py`

## Config

Change config in `config.json`

| Key             | Description                                                                                                 |
| --------------- | ----------------------------------------------------------------------------------------------------------- |
| fileDir         | Input directory                                                                                             |
| fileExts        | Legal file extensions to rename, default is video files                                                     |
| getInfoInterval | Time interval to retrieve data from source website in second, do not set too small                          |
| fileNameFormat  | Format of new file name, see more below                                                                     |
| language        | `tw`, `cn`, `en`, `ja` for javlibrary, english only in javdb                                                |
| saveAlbum       | Save album image in the same directory of video file                                                        |
| saveThumb       | Save thumbnails in the same directory of video file                                                         |
| dryRun          | Run without real execution                                                                                  |
| maxFileLength   | Maximum file name length in bytes, reduce this value if "file name too long" error happens                  |
| minFileSizeMB   | Minimum file size(in MB) to execute                                                                         |
| renameCheck     | Ask before every rename operation                                                                           |
| ignoreWords     | Ignore list of words in filename to prevent parse bangou error, e.g., "1080p-123.mp4" will parse as `p-123` |
| retryFailedDB   | Retrieve failed data in database from source website again                                                  |
| javdbToken      | some queries from javdb needs token, login to javdb and get `remember_me_token` in cookie as token          |

### Tags in fileNameFormat

Recommend to include `{bangou}` in order to do further rename.

| Tags       | Description                                                     |
| ---------- | --------------------------------------------------------------- |
| {bangou}   | The serial number of jav                                        |
| {title}    | Title may include actors' name, guarantee not include bangou    |
| {tags}     | Tags in source website                                          |
| {director} |                                                                 |
| {maker}    | Maker of the video, usually related to the first part of bangou |
| {actors}   |                                                                 |
| {duration} | The length of video in minutes                                  |
| {date}     | Release date                                                    |
| {rating}   | Rating in source website                                        |
| {album}    | Link of album image, **not recommend to use**                   |
| {thumbs}   | Link of thumbnails, **not recommend to use**                    |
| {link}     | Link of information source, **not recommend to use**            |

## Database

All queries will be saved in `db-{language}.json`.

You can do dry run to check the rename progress and then execute without retrieving data again.

Failed requests will also be saved, so clean the database if something went wrong.

## Note

- Input filename should include bangou, or it cannot be renamed
- If there exist multiple files that have the same bangou, they will be renamed with serial number, ordered by original file name

## Future Work

- Execute
  - fill video metadata in file
  - options for new folder
- FileName
  - fit various types of bangou
- Database
  - use other method instead directly loading into memory
- UI
  - interface to search local database
- Add makefile
- Config
  - verbose output
- Crawler
  - find database which has chinese title

## Source Website

- [javlibrary](http://javlibrary.com)
- [javdb](http://javdb.com)
