import json
import os
import pandas as pd
from tqdm import tqdm
import numpy as np

def generate_excel_from_metadata(params):
    """
    Reads metadata from JSON files and generates Excel files with img_path names formatted 
    as done in the original code (without actual cropping or saving images).
    :param params: global parameters, used to find location of the dataset and json file
    :return: None
    """
    walkDirs = ['train', 'val', 'test']
    train_excel_data = []
    test_excel_data = []
    paramsDict = vars(params)
    keysToKeep = ['image_format', 'target_img_size', 'metadata_length', 'category_names']
    paramsDict = {keepKey: paramsDict[keepKey] for keepKey in keysToKeep}

    for currDir in walkDirs:
        isTrain = (currDir == 'train') or (currDir == 'val')
        if isTrain:
            outDir = params.directories['train_data']
        else:
            outDir = params.directories['test_data']

        for root, dirs, files in tqdm(os.walk(os.path.join(params.directories['dataset'], currDir))):
            if len(files) > 0:
                slashes = [i for i, ltr in enumerate(root) if ltr == '/']

            for file in files:
                if file.endswith('_rgb.json'):
                    json_file_path = os.path.join(root, file)
                    jsonData = json.load(open(json_file_path))
                    timestamp = jsonData['timestamp']
                    
                    # Assume image file has the same base name as the JSON file but different extension
                    image_base_name = file.replace('.json', '')
                    image_format = paramsDict['image_format']  # Ensure the correct image format is used
                    imgFile = image_base_name + '.' + image_format

                    if 'bounding_boxes' in jsonData and isinstance(jsonData['bounding_boxes'], list):
                        for bb in jsonData['bounding_boxes']:
                            category = bb.get('category', 'Unknown')  # Get category or default to 'Unknown'
                            box = bb.get('box', None)  # Get bounding box
                            bb_id = bb.get('ID', 0)  # Get bounding box ID
                            
                            # Construct output path based on category, bounding box ID, and directory structure
                            outBaseName = f"{category}_{bb_id}"

                            if isTrain:
                                currOut = os.path.join(outDir, root[slashes[-3] + 1:], outBaseName)
                            else:
                                currOut = os.path.join(outDir, root[slashes[-2] + 1:], outBaseName)

                            img_path = os.path.join(currOut, imgFile)

                            # Collect metadata for Excel generation
                            if isTrain:
                                train_excel_data.append({
                                    'img_path': img_path,  # Use constructed img_path
                                    'timestamp': timestamp,
                                    'category': category
                                })
                            else:
                                test_excel_data.append({
                                    'img_path': img_path,  # Use constructed img_path
                                    'timestamp': timestamp,
                                    'category': category
                                })

    # Generate Excel files from collected metadata
    generate_excel_files(train_excel_data, 'train')
    generate_excel_files(test_excel_data, 'test')

def generate_excel_files(data, data_type):
    """
    Generate an Excel file from a list of dictionaries containing 'img_path', 'timestamp', and 'category'.
    :param data: List of dictionaries with image details.
    :param data_type: 'train' or 'test' to label the file accordingly.
    :return: None
    """
    df = pd.DataFrame(data)
    
    # Set the Excel file path
    excel_path = f'processed_images_metadata_{data_type}.xlsx'
    df.to_excel(excel_path, index=False)
    
    print(f"Excel file for {data_type} created at {excel_path}")
