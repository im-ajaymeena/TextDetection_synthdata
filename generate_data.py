import argparse
import os
import random
import glob
import numpy as np
import pathlib
from pilmoji import Pilmoji
from input_data.twemoji_list import twemoji_list

from PIL import Image, ImageDraw, ImageFont, ImageStat


from wordart_gen import wordart_gen_func
import get_non_overlapped_rect
from img_add_texture import add_texture

# fix seed for consistency in generated data
random.seed(0)

def list_files_recursively(directory):
    for item in directory.iterdir():
        # print(type(item), item)
        if item.is_file():
            yield item
        elif item.is_dir():
            yield from list_files_recursively(item)
    return

def start_generation(
        image_path, 
        text_samples_path, 
        output_path, 
        font_list, 
        wordart_probablility, 
        visualize_annotation,
        save_annotation_flag
        ):
    # Load text samples
    with open(text_samples_path, 'r', encoding='utf-8') as f:
        text_samples = f.read().splitlines()
    
    # Loop over images
    for i, image_path in enumerate(list_files_recursively(pathlib.Path(image_path))):
        # Load image
        img = Image.open(image_path).convert("RGBA")
        img.thumbnail((1280, 1280))
        img_width, img_height = img.size

        aspect_ratio = img_width/img_height
        if aspect_ratio < 1 or aspect_ratio > 21/9:
            continue

        min_dim = min(img_width, img_height)

        # text outline thickness random with custom prob
        min_max_thickness = [2, 20]
        thick_range = np.arange(*min_max_thickness, 1, dtype=float)

        # get probability distribution for thickness inversly proportional to the thickness
        thick_prob = thick_range[::-1]**4
        thick_prob /= np.sum(thick_prob)
        thick_param = np.random.choice(thick_range, p=list(thick_prob))

        # adjust thickness accordint to image dimension (width, height)
        outline_thickness = int(0.001 * min_dim * thick_param)

        # number of lines of text to add over image
        num_lines = np.random.choice([1, 2, 3, 4, 5, 10,], p=[
                                    0.05, 0.25, 0.3, 0.2, 0.15, 0.05], size=(1))[0]
        overlapp_ck_annotations = []
        annotations = []
        annotations_yolo = []

        # add texture to image with 10% probability
        if random.random() < 0.1:
            r, g, b, a = img.split()
            rgb_image = Image.merge('RGB', (r, g, b))
            augmented_img = add_texture(rgb_image, None)
            r, g, b = augmented_img.split()
            img = Image.merge('RGBA', (r, g, b, a))
        
        # Instead of simple plain text use Microsoft WordArt like text over images with 10% probability
        text_is_wordart = random.random() < wordart_probablility

        if not(text_is_wordart):
            for _ in range(num_lines):
                # get text of each randomly picked line to be superimposed on image
                text = random.choice(text_samples)
                print("text: ", text)
                    
                # Generate random font parameters
                font_size = int(0.01 * min_dim * (1+np.random.normal(10, 4)))
                thickness = int(0.01 * min_dim * np.random.normal(30, 4))*font_size

                font_path = random.choice(font_list)
                print(font_path)

                m = int(0.02 * min_dim)  # margin


                font = ImageFont.truetype(font_path, size=font_size)

                try:
                    text_bbox = font.getmask(text).getbbox()
                    original_text_size = text_bbox[2] - \
                        text_bbox[0], text_bbox[3]-text_bbox[1]
                except:
                    # sometimes the fonts are not supported or give no text_box
                    continue


                # set text direction ttb : top to bottom | rtl: right to left                            
                if random.random() < 0.3:
                    text_direction = 'ttb'
                    text_size = original_text_size[1], original_text_size[1]*len(text)
                else:
                    text_direction = 'rtl'
                    text_size = original_text_size
                
                # if the text size is too large to be fit inside image ignore the text and continue with another sample
                if img_width - text_size[0] - 3*m < 0 or img_height - text_size[1] - 3*m < 0:
                    continue

                # texts Overlap check we'll try to add the text multiple times at different locations and each time check if there is
                # overlap with existing texts, if we couldnt find after 10 iteration, this text will get ignored
                #-------------------------------------------------------------------------------------------------------
                #------------------------COORDINATE SELECTION WITH OVERLAP CHECKING BEGINS-------------------------------
                #-------------------------------------------------------------------------------------------------------
                loop_count = 0
                while loop_count < 10:
                    loop_count += 1

                    #chose coordinate for multi-line, case when more than one text in image
                    text_x = text_y = None
                    if len(overlapp_ck_annotations) > 0:
                        ax, ay, aw, ah, _ = overlapp_ck_annotations[-1]
                        # check if the x axis & y axis both are fine for right-bottom corner
                        if ax + aw + text_size[0] + 3*m < img_width and random.random() < 0.8:
                            if ay + ah + text_size[1] + 3*m < img_height:
                                if ax+aw-text_size[0] > 3:
                                    if random.random() > 0.5:
                                        text_x = ax
                                    else:
                                        text_x = ax+aw-text_size[0]
                                else:
                                    text_x = ax
                                    
                                text_y = ay+ah+3*m
                        # check if the x axis & y axis both are fine for left-above corner
                        elif ax - text_size[0] - 3*m  > 0:
                            if ay - text_size[1] - 3*m >  0:
                                text_x = ax-text_size[0]-3*m
                                text_y = ay + ah - text_size[1]


                    m = int(0.02 * min_dim)  # margin

                    if text_x == None or text_y == None:
                        # for placing font text at corner
                        if font_size < int(0.01 * min_dim * (6)) and len(text) < 4:
                            rand = random.random()
                            if rand < 0.2:
                                text_x = random.randint(0, 2*m)
                                text_y = random.randint(0, 2*m)
                            elif rand < 0.4:
                                text_x = img_width - text_size[0] - 2*m
                                text_y = random.randint(m, 2*m)
                            else:
                                text_x = random.randint(m, img_width - text_size[0] - 2*m)
                                text_y = random.randint(m, img_height - text_size[1] - 2*m)
                        else:
                                text_x = random.randint(m, img_width - text_size[0] - 2*m)
                                text_y = random.randint(m, img_height - text_size[1] - 2*m)
                    
                    # since we are superimposing multiple text while selecting the coordinates we need to make sure they are not overlapped 
                    # for the current text check if it's overlapped with any other text already present in list overlapp_ck_annotations,
                    overlap = False
                    for annotation in overlapp_ck_annotations:
                        ax, ay, aw, ah, _ = annotation

                        if (text_x+text_size[0]+m < ax or ax+aw+m < text_x or text_y+text_size[1]+m < ay or ay+ah+m < text_y):
                            pass
                        else:
                            overlap = True
                            break

                    if not overlap:
                        break

                # if overlap do not use that text
                if overlap:
                    continue

                #-------------------------------------------------------------------------------------------------------
                #------------------------COORDINATE SELECTION WITH OVERLAP CHECKING ENDS-------------------------------
                #-------------------------------------------------------------------------------------------------------


                # Do we want colored text
                colored = False
                if random.random() < 0.5:
                    colored = True

                # do we want text background (basically a rectangular background behind text)
                rect_bk = False
                if random.random() < 0.2:
                    rect_bk = True
                
                # we would like to check if the text color is not significantly similar to the color area of image around it, since if text and image 
                # area has same color, the text might not be visible (for example -> black image & black font color -> text not visible)
                # we check this by calculating contrast among image region and randomly selected text color 
                loop_count = 0
                while loop_count < 20:
                    loop_count += 1
                    # Check the contrast ratio between the font color and the background color
                    # Crop image to the region where the text is going to be added
                    text_region = img.crop(
                        (text_x, text_y, text_x + text_size[0], text_y + text_size[1]))

                    # Compute the mean background color of the text region
                    bg_color = ImageStat.Stat(text_region).mean

                    #transparent
                    font_is_bigger = font_size > int(0.01 * min_dim * (14))
                    make_transparent_text = random.random() < 0.2 and font_is_bigger
                    if make_transparent_text:
                        alpha=random.randint(100, 128)
                        transparent_text_img = Image.new("RGBA", img.size, (255, 255, 255, 0))
                        draw_transparent_text = ImageDraw.Draw(transparent_text_img)
                    else:
                        alpha=255

                    if colored:
                        font_color = (random.randint(0, 255), random.randint(
                            0, 255), random.randint(0, 255), alpha)  # Random font color
                        outline_color = (random.randint(0, 255), random.randint(
                            0, 255), random.randint(0, 255), alpha)  # Random outline color
                    else:

                        rgb_values = text_region.getdata()
                        num_pixels = len(rgb_values)
                        sum_rgb = [sum(x) for x in zip(*rgb_values)]
                        mean_pixel_value = tuple(
                            map(int, [x / num_pixels for x in sum_rgb]))

                        font_color = (0, 0, 0)
                        outline_color = (0, 0, 0)
                        outline_thickness = 0

                        if sum(mean_pixel_value) / 3 < 128:
                            font_color = (200, 200, 200, alpha)
                        else:
                            font_color = (0, 0, 0, alpha)

                    # Compute the luminance of the font color
                    L1 = 0.2126 * font_color[2] + 0.7152 * \
                        font_color[1] + 0.0722 * font_color[0]
                    # Compute the luminance of the background color
                    L2 = 0.2126 * bg_color[2] + 0.7152 * \
                        bg_color[1] + 0.0722 * bg_color[0]
                    contrast_ratio = (max(L1, L2) + 0.05) / (min(L1, L2) + 0.05)
                    if contrast_ratio >= 6.5:
                        break

                    #agar rect_bk he toh ek hi baa bohot he loop
                    if not(rect_bk):
                        break


                draw = ImageDraw.Draw(img)

                # get rectanglular coordinates for drawn text
                x1, y1, x2, y2 = draw.textbbox((text_x, text_y), text,
                                            font=font, direction=text_direction)
                
                # bouding box to represent the drawn text
                x1 -= 3+outline_thickness
                y1 -= 3+outline_thickness
                x2 += 3+outline_thickness
                y2 += 3+outline_thickness
                
                if x1 < 0 or y1 < 0 or x2 > img_width or y2 > img_height:
                    continue

                # draw the text with either transparent or no transparency
                if make_transparent_text:
                    draw_transparent_text.text((text_x, text_y), text, font=font,
                            fill=outline_color, stroke_width=outline_thickness, direction=text_direction)
                    img = Image.alpha_composite(img, transparent_text_img)
                else:
                    draw.text((text_x, text_y), text, font=font,
                            fill=outline_color, stroke_width=outline_thickness, direction=text_direction)
                
                #shadow / boder of text
                if random.random() < 0.1:
                    draw.text((int(text_x*1.005), int(text_y*1.005)), text, font=font,
                            fill=(192, 192, 192), direction=text_direction)
                


                #rectangle box around text
                if rect_bk:
                    rect_fill = (255-font_color[0], 255-font_color[1], 255-font_color[2])
                    radius = random.randint(-4, int(original_text_size[1]*0.8))
                    radius = max(0, radius)
                    radius = min(int(original_text_size[1]*0.5), radius)

                    rec_pad=min(0.02, m/2)
                    wp = x2-x1
                    try:
                        draw.rounded_rectangle(
                            (int(x1-wp*rec_pad), int(y1-wp*rec_pad), int(x2+wp*rec_pad), int(y2+wp*rec_pad)), fill=rect_fill, radius=radius)
                    except:
                        pass
                
                # for augmentation we add emojis nearby texts
                add_emoji = random.random() < 0.3 and font_size < int(0.01 * min_dim * (7))

                if add_emoji:
                    emoji = " ".join(random.sample(twemoji_list, random.randint(1,3)))
                    try:
                        with Pilmoji(img) as pilmoji:
                            pilmoji.text((text_x, text_y), text+emoji, font=font,
                                        fill=font_color, direction=text_direction)
                    except:
                        draw.text((text_x, text_y), text, font=font,
                                fill=font_color, direction=text_direction)
                else:
                    draw.text((text_x, text_y), text, font=font,
                            fill=font_color, direction=text_direction)
                

                xc = (x1+x2)/2
                yc = (y1+y2)/2
                w = int((x2-x1)*1.01)
                h = int((y2-y1)*1.01)

                # Add annotation in a image to list
                overlapp_ck_annotations.append((x1, y1, w, h, text))
                annotations.append((x1, y1, w, h, text))

                assert overlapp_ck_annotations == annotations

                xcN, wN = format(xc/img_width, '.6f'), format(w/img_width, '.6f')
                ycN, hN = format(yc/img_height, '.6f'), format(h/img_height, '.6f')

                category = 0 if text_direction == "rtl" else 1
                if len(text) == 1:
                    category = 3
                annotations_yolo.append((category, xcN, ycN, wN, hN))


            # visualize superimposed text with the bounding box
            if visualize_annotation and len(annotations):
                img_for_visualize = img.copy()
                draw_visualize = ImageDraw.Draw(img_for_visualize)

                for annotation in annotations:
                    x1, y1, w, h, _ = annotation
                    draw_visualize.rectangle((x1, y1, x1+w, y1+h), outline=(255, 255, 255), width=2)
                
                img_for_visualize.show()
                input("Press Enter to continue...")
        else:
            # ----------------------------------- use WordArt to draw text on images ------------------------------------------------
            text_sizes = []
            text_images = []
            raw_text_list = []
            text_direction_list = []
            for j in range(num_lines):
                text = random.choice(text_samples)
                try:
                    text_image, wordart_style = wordart_gen_func.generate_wordart_image(text)
                except:
                    continue

                # text = "to get approximate text size with font size later we will reszie word art according to this"
                font_size = int(0.01 * min_dim * (1+random.randint(12, 18)))
                font_path = random.choice(font_list)
                font = ImageFont.truetype(font_path, size=font_size)

                try:
                    text_bbox = font.getmask(text).getbbox()
                except OSError:
                    continue

                original_text_size = text_bbox[2] - \
                    text_bbox[0], text_bbox[3]-text_bbox[1]

                # if its stact the word art is in top to bottom
                if "stack" in wordart_style:
                    text_direction = 'ttb'
                    text_size = original_text_size[1], original_text_size[1]*len(text)
                else:
                    text_direction = 'rtl'
                    text_size = original_text_size
                
                if text_size[0]*1.2 > img_width or text_size[1]*1.2 > img_height:
                    continue

                text_sizes.append(text_size)
                text_image.thumbnail(original_text_size)
                text_images.append(text_image)
                raw_text_list.append(text)
                text_direction_list.append(text_direction)

            if text_sizes:    
                field_size = ((40,40), (img_width-40, img_height-40))
                non_overlapped_boxs = get_non_overlapped_rect.generate_box(field_size, text_sizes)
                
                if non_overlapped_boxs == None:
                    # couldnt adjust the boxes to fit in the image in non-overlapping manner
                    continue

                for text_image, non_overlapped_box, raw_text, text_direction in zip(text_images, non_overlapped_boxs, raw_text_list, text_direction_list):
                    (x, y), (w, h) = non_overlapped_box
                    img.paste(text_image, (x, y), text_image)

                    xc = x + w/2
                    yc = y + h/2
                    w = int(w*1.01)
                    h = int(h*1.01)

                    xcN, wN = format(xc/img_width, '.6f'), format(w/img_width, '.6f')
                    ycN, hN = format(yc/img_height, '.6f'), format(h/img_height, '.6f')
                
                    annotations.append((x, y, w, h, raw_text))
                    category = 0 if text_direction == "rtl" else 1
                    if len(raw_text) == 1:
                        category = 3
                    annotations_yolo.append((category, xcN, ycN, wN, hN))
                
                # visualize superimposed text with the bounding box
                if visualize_annotation and len(non_overlapped_boxs):
                    img_for_visualize = img.copy()
                    draw_visualize = ImageDraw.Draw(img_for_visualize)

                    for text_image, non_overlapped_box in zip(text_images, non_overlapped_boxs):
                        (x, y), (w, h) = non_overlapped_box
                        draw_visualize.rectangle((x, y, x+text_image.size[0], y+text_image.size[1]), outline=(255, 255, 255), width=2)

                    img_for_visualize.show()
                    input("Press Enter to continue...")
                

        
        # if no annotation/bounding-box proceed to next iteration
        if len(annotations) == 0:
            continue
            

        print(annotations)
        if len(annotations) > 0 and save_annotation_flag:

            ## Save image with superimposed text
            annotated_image_name = os.path.join(
                output_path, f'{i}'.zfill(4)+'.png')
            img.save(annotated_image_name)
            # continue

            ## Save ground for the text label & location to text file
            annotation_file_name = os.path.join(
                output_path, f'{i}'.zfill(4)+'_custom_format'+'.txt')
            
            annotation_file_name_yolo = os.path.join(
                output_path, f'{i}'.zfill(4)+'.txt')
            
            with open(annotation_file_name, 'w') as f:
                for annotation in annotations[:-1]:
                    f.write(
                        f'{annotation[0]},{annotation[1]},{annotation[2]},{annotation[3]},{annotation[4]}\n')
                annotation = annotations[-1]
                f.write(
                    f'{annotation[0]},{annotation[1]},{annotation[2]},{annotation[3]},{annotation[4]}')

            with open(annotation_file_name_yolo, 'w') as f:
                for annotation in annotations_yolo[:-1]:
                    f.write(
                        f'{annotation[0]} {annotation[1]} {annotation[2]} {annotation[3]} {annotation[4]}\n')
                annotation = annotations_yolo[-1]
                f.write(
                    f'{annotation[0]} {annotation[1]} {annotation[2]} {annotation[3]} {annotation[4]}')




def parse_arguments():
    parser = argparse.ArgumentParser(description='Process image and text data.')

    ## Input/Output Paths
    parser.add_argument('--raw_image_path', type=str, default='./input_data/raw_images',
                        help='Path to the directory containing the input images')
    parser.add_argument('--text_samples_path', type=str, default='./input_data/text/japanese.txt',
                        help='Path to the text samples file')
    parser.add_argument('--texture_imgs_path', type=str, default='./input_data/texture_images',
                        help='Path to the textures to be placed on image')
    parser.add_argument('--output_path', type=str, default='output',
                        help='Path to save output images and annotations')
    
    ## if you want to save the output data
    parser.add_argument('--save_annotation',  action='store_true', default=False,
                help='save the annotations')
    
    ## Fonts to be used
    parser.add_argument('--font_path', type=str, default='fonts',
                        help='font directory')
    
    ## probablity of using wordart type text, for reference check -> https://www.makewordart.com/
    parser.add_argument('--wordart_prob', type=float, default=0,
                    help='probablity of text to be wordart')
    
    ## if you want to visualize the annotations
    parser.add_argument('--visualize',  action='store_true', default=False,
                help='visualize the annotations')



    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_arguments()

    font_list = glob.glob(f'{args.font_path}/*.ttf')
    start_generation(
        args.raw_image_path, 
        args.text_samples_path, 
        args.output_path, 
        font_list, 
        args.wordart_prob, 
        args.visualize,
        args.save_annotation
        )