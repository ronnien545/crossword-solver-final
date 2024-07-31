import torch
import datasets
from datasets import load_from_disk,Dataset 
import sys
from transformers import AutoTokenizer, TFAutoModel
import os
import logging
import threading
import copy
import csv

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow info messages
logging.getLogger("tensorflow").setLevel(logging.ERROR)  # Suppress TensorFlow warning messages
logging.getLogger("keras").setLevel(logging.ERROR)

model_ckpt = "all-mpnet-base-v2"
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

model = AutoTokenizer.from_pretrained("bert-base-uncased") 
#loads a empty dataset to set load_dataset 
load_dataset = Dataset.from_dict({"text": [], "label": []}) 

tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
model = TFAutoModel.from_pretrained(model_ckpt, from_pt=True)

load_dataset = load_from_disk("total_concatenated")
load_dataset.load_faiss_index('embeddings', 'total_concatenated.faiss')


def cls_pooling(model_output):
    #get final hidden state of output embedding
    return model_output.last_hidden_state[:, 0]

def get_embeddings(text_list):
    #get embedding given a list of text
    encoded_input = tokenizer(
        text_list, padding=True, truncation=True, return_tensors="tf"
    )
    encoded_input = {k: v for k, v in encoded_input.items()}
    model_output = model(**encoded_input)
    return cls_pooling(model_output)

# Define the input and output file paths
input_file = 'nytcrosswords.csv'
#output_file = 'outputnytnew2.csv'

# Define the range of rows to keep (134,870 to 235,090)
start_row = 1
end_row = 636058

# Open the input CSV file for reading and the output CSV file for writing
with open(input_file, 'r', newline='', encoding='latin-1') as csvfile_in:
    # Create CSV reader and writer objects
    reader = csv.reader(csvfile_in)

    # Read and write the header
    header = next(reader)

    # Read and write the selected rows within the specified range
    tot = 0
    clueright= 0
    for i, row in enumerate(reader, start=1):
        # print(i)
        # print("The clue right")
        # print(clueright)
        # print("the tot right")
        # print(tot)
        # print("Dividing the answer")
        if start_row <= i <= end_row:
            question_embedding = get_embeddings([row[2]]).numpy()[0]
            scores, samples = load_dataset.get_nearest_examples(
             "embeddings", question_embedding, k=5
            )
            print(i)
            if samples['Word'][0] == row[1]:
              clueright+=1
            tot+=1
        else:
          break
    
    print(clueright)
    print(tot)
    print(tot/clueright)


