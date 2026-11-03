# tar

Sample notes for trying crib. Paths and names are made up.

## Extract an archive
`tar xf archive.tar`

## Extract into another folder
`tar xf archive.tar -C /tmp/unpacked`

## Create a gzip archive
Add -v to see each file as it goes in.
`tar czf backup.tgz projects/`

## List what is inside without extracting
`tar tf backup.tgz`
