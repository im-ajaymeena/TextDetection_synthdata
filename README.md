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


## WordArt like text 
![](wordart_gen/output/wordart-tilt-.png)