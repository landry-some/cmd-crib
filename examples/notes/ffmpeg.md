# ffmpeg

## Cut a clip without re-encoding
Start at 1:30, keep 20 seconds.
`ffmpeg -ss 00:01:30 -i input.mp4 -t 20 -c copy clip.mp4`

## Extract audio as mp3
`ffmpeg -i talk.mp4 -vn -q:a 2 talk.mp3`

## Make a gif from a short video
```sh
ffmpeg -i demo.mp4 -vf "fps=10,scale=480:-1" demo.gif
```
