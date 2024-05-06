## Generate Synthetic data with text over images with ground truth for text location and labels.

<br>

### Generate data cmd
```bash
# before running the script, make sure to have input_data, checkout ./input_data
bash generate_data_cmd.sh
```


### Description of directories:
- `./fonts/` list of font to be used for rendering text on images
- `./input_data/` scripts to get/create input data (raw-images & sample text) 
check `./input_data/README.md` for more information
- the data will get saved in `./output/`, there are some samples output data
- `./wordart_gen/` docker-client based script to generate Microsoft-wordart like text graphics
being used inside main script `generate_data.py`



## Things to consider while adding new fonts
- Some fonts might only render part of text
- Some fonts might not render at all and give blocks like representation
- before adding new fonts make sure they can render the text

## Input Output Ex
<div style="display: flex;">
    <img src="input_data/raw_images/image_pixalbay_p2_5.jpg" alt="First Image" style="width: 30%;  margin-right: 10px;;">
    <img src="output/0002.png" alt="Second Image" style="width: 30%;">
</div>

<br>

```
## ground truth annotations text file with bounding boxes x1, y1, w, h, label format
56,266,1172,68,なズ殿諏プをつプ楡む柿之vヒあ梅覇ゴ
1054,557,132,116,城
522,618,493,59,染う胡フ辺局ゼ森れ
193,376,1010,112,亜中政ねうテジさぎゲ
62,445,113,81,バ
```

<br>

## Also support WordArt like text 
![](wordart_gen/output/wordart-tilt-.png)