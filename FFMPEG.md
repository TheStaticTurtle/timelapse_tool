# FFMpeg cheatsheet
This is my cheat sheet not especially made for others but you might find it useful

## Combine images
``
ffmpeg -i shot%05d.jpg -r 30 -vcodec h264_qsv  -crf 15 -x264-params "nal-hrd=cbr" -b:v 8M output.mp4
``
## Speed correction
### BLEND
``
ffmpeg -i output.mp4 -vf "tblend=average,framestep=2,tblend=average,framestep=2,setpts=0.25*PTS" -r 30 -vcodec h264_qsv  -crf 15 -x264-params "nal-hrd=cbr" -b:v 8M outputBLEND.mp4
``

``
ffmpeg -i output.mp4 -vf "tblend=average,framestep=3,setpts=0.33333*PTS" -r 30 -vcodec h264_qsv  -crf 15 -x264-params "nal-hrd=cbr" -b:v 8M outputBLEND4.mp4
``

## Effects
### ZOOM
```ffmpeg -i input.mp4 -filter:v “zoompan=z='if(lte(in,1),1.2,max(pzoom-0.0001,1))’:d=1:x=’iw/2-(iw/zoom/2)’:y=’ih/2-(ih/zoom/2)’:s=2560x1920:fps=30" output.mp4```
