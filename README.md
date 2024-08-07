# DeformVOS



## datasets prepare 

We unify the file structure of file like `VOST` , as follow in `./datasets`:

```
- ROVES_summary
	- ROVES_week_0 
    	- JPEGIMages
      		- seq_0
        		- 0000000.jpg
        		...
      		- seq_1
      		...
    	-  Annotations
     		 - seq_0
        		- 0000000.png
       	 	    ...
      		 - seq_1
      		 ...
    	- Videos
      		-seq_0.mp4
      		-seq_1.mp4
    		...
		-challenge_label.json
	...
        
        
- VOST (just_like ROVES_week_0)

- ...
```

tip: This folder `datasets` should be linked in the every method folder in  `./methods` 

​	for example, in CFBI， `datasets -> ../../datasets/`

​	In order to share the datasets in different which make it convenient to manager the datasets



## tool introduction

in the `./tool`

- `merge_signle_video.py`:  merge the mask and image into a video  , args:
  - `images_folder`:  a folder contains images: `001.jpg`  , `002.jpg`, ...
  - `masks_folder`:  a folder contains masks: `001.png`  , `002.png`, ...
  - `output_video`： `*.mp4`
- `merge_png2video.py`: process the dataset whose file structure just like `VOST`, get the merge videos folder
  - `images_folder`:  a folder contains the images of seqs:  just like `ROVES_summary/ROVES_week_0/JPEGIMages `
  - `masks_folder`:  a folder contains he masks of  seqs: `ROVES_summary/ROVES_week_0/Annotations`
  - `output_video`：a target folder contains  merge videos : `exp/merge_videos`
- `align_direction.py`: If you find the width of your video is more than its height , it will rotate it 90 degree  counterclockwisely.

