This folder is needed to store preview images for user-generated
entries.

The folder needs to be writeable by the web application process.

The application will create several levels of sub-directories in
order to allow for fast file system accesses to the individual
files.

The preview images for an entry with the ID 1234 resides here:

static/thumbs/4/3/2/1234/

The sub-folder path is made from the last three digits of the numeric
id, in reversed order. The last sub folder is named after the ID itself.

Different preview image formats have different file names.

* 'pv.png' stands for the standard preview image used on the browse page
* 'og.png' is a format specifically sized for use on Facebook (meta og:image tag)

