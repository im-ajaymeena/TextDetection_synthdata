### This directory contains all the scripts to create the images and text which will get superimposed on the images

## Summary for creating input data: 
- download images to -> `./raw_images`
    - `python get_pixalbay_images.py`
- generate text file with 
    - `python generate_random_text_lines.py`

## Detailed description
To get/download the raw images
- get_pixalbay_images.py -> images from https://pixabay.com/
- get_unsplash_images.py -> images from https://unsplash.com/
- get_huggingface_images_examples.py -> images from some huggingface dataset it also creates subdirectory based on image categories (the script would need modification according to the dataset schema)

Its better to resize the images to same width for uniformality -> use resize_images_to_1280.py


To generate text which will get used to create dataset:
- generate_random_text_lines.py -> given a list of characters it creates a files containing multiple lines of random words/strings
- some existing dataset of text can be used such as raw_en_jp_text.0.parquet -> visualize using visualize_parquet.py

twemoji_list.py -> contains emojis from twitter to be used which creating the dataset
