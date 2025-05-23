# Steganography Tool - Babila, Bonos, Lumibao, Tocayon BSCS 3B

import numpy as np
import pandas as pd
import os
import cv2
from matplotlib import pyplot as plt

# hide text in other text using invisible characters
def encode_text_to_binary(text):
    text_length = len(text)
    binary_string = ''
    # these are invisible unicode characters
    zero_width_codes = {"00": '\u200C', "01": '\u202C', "11": '\u202D', "10": '\u200E'}
    
    # convert each letter to binary
    for i in range(text_length):
        char_code = ord(text[i])
        if 32 <= char_code <= 64:
            transformed = char_code + 48
        else:
            transformed = char_code - 48
        encrypted = transformed ^ 170  # simple encryption
        binary_byte = bin(encrypted)[2:].zfill(8)
        prefix = "0011" if 32 <= char_code <= 64 else "0110"
        binary_string += prefix + binary_byte
    
    final_binary = binary_string + "111111111111"  # end marker
    print(f"Converted binary: {final_binary}")
    print(f"Binary length: {len(final_binary)}")
    
    # read the cover file
    source_file = open("sample_files/sampletext.txt", "r+")
    output_filename = input("\nEnter steganography file name (with extension): ")
    stego_file = open(output_filename, "w+", encoding="utf-8")
    
    # get all words from file
    words = []
    for line in source_file:
        words += line.split()
    
    # hide binary in spaces between words
    bit_index = 0
    while bit_index < len(final_binary):
        current_word = words[bit_index // 12]
        hidden_chars = ''
        
        for j in range(0, 12, 2):
            if bit_index + j + 1 >= len(final_binary):
                break
            bits = final_binary[bit_index + j] + final_binary[bit_index + j + 1]
            hidden_chars += zero_width_codes[bits]
        
        stego_file.write(current_word + hidden_chars + " ")
        bit_index += 12
    
    # write remaining words normally
    for remaining in range(len(words) - (len(final_binary)//12), len(words)):
        stego_file.write(words[remaining] + " ")
    
    stego_file.close()
    source_file.close()
    print("\nSteganography file created successfully")

# check if message fits in cover text
def prepare_text_encoding():
    word_count = 0
    with open("sample_files/sampletext.txt", "r") as file:
        for line in file:
            word_count += len(line.split())
    
    max_words = word_count // 6
    print(f"Max encodable words: {max_words}")
    
    user_input = input("Enter message to encode: ")
    if len(user_input) <= max_words:
        print("Message can be hidden")
        encode_text_to_binary(user_input)
    else:
        print("Message too long. Try again.")
        prepare_text_encoding()

# convert binary to number
def binary_to_decimal(binary_str):
    return int(binary_str, 2)

# extract hidden message from stego file
def decode_hidden_text():
    reverse_codes = {'\u200C': "00", '\u202C': "01", '\u202D': "11", '\u200E': "10"}
    stego_file = input("Enter stego file name: ")
    
    extracted_bits = ""
    with open(stego_file, "r", encoding="utf-8") as file:
        for line in file:
            for word in line.split():
                for char in word:
                    if char in reverse_codes:
                        extracted_bits += reverse_codes[char]
                if extracted_bits.endswith("111111111111"):
                    break
    
    # turn binary back to text
    decoded_message = ""
    for i in range(0, len(extracted_bits)-12, 12):
        prefix = extracted_bits[i:i+4]
        byte = extracted_bits[i+4:i+12]
        
        if prefix == "0110":
            decoded = (binary_to_decimal(byte) ^ 170) + 48
        elif prefix == "0011":
            decoded = (binary_to_decimal(byte) ^ 170) - 48
        decoded_message += chr(decoded)
    
    print(f"Decoded message: {decoded_message}")

# convert different data types to binary
def message_to_binary(message):
    if isinstance(message, str):
        return ''.join(format(ord(c), "08b") for c in message)
    elif isinstance(message, (bytes, np.ndarray)):
        return [format(byte, "08b") for byte in message]
    elif isinstance(message, (int, np.uint8)):
        return format(message, "08b")
    else:
        raise TypeError("Unsupported input type")

# hide text in image using LSB method
def encode_image_data(image):
    secret_data = input("Enter data to encode: ") + '*^*^*'
    if not secret_data:
        raise ValueError("No data entered")
    
    output_filename = input("Enter output image name: ")
    max_bytes = (image.shape[0] * image.shape[1] * 3) // 8
    
    if len(secret_data) > max_bytes:
        raise ValueError("Data too large for image")
    
    binary_data = message_to_binary(secret_data)
    bit_index = 0
    
    # change last bit of each color
    for row in image:
        for pixel in row:
            r, g, b = message_to_binary(pixel)
            if bit_index < len(binary_data):
                pixel[0] = int(r[:-1] + binary_data[bit_index], 2)
                bit_index += 1
            if bit_index < len(binary_data):
                pixel[1] = int(g[:-1] + binary_data[bit_index], 2)
                bit_index += 1
            if bit_index < len(binary_data):
                pixel[2] = int(b[:-1] + binary_data[bit_index], 2)
                bit_index += 1
    
    cv2.imwrite(output_filename, image)
    print(f"Image saved as {output_filename}")

# get hidden data from image
def decode_image_data(image):
    binary_stream = ""
    for row in image:
        for pixel in row:
            r, g, b = message_to_binary(pixel)
            binary_stream += r[-1] + g[-1] + b[-1]
    
    # convert back to text
    decoded = ''.join([chr(int(binary_stream[i:i+8], 2)) for i in range(0, len(binary_stream), 8)])
    if '*^*^*' in decoded:
        print(f"Hidden message: {decoded.split('*^*^*')[0]}")

# text menu
def text_steg_menu():
    while True:
        print("\n╔════════════════════════════════════╗")
        print("║       TEXT STEGANOGRAPHY MENU      ║")
        print("╠════════════════════════════════════╣")
        print("║ 1. Encode message                  ║")
        print("║ 2. Decode message                  ║")
        print("║ 3. Return to main menu             ║")
        print("╚════════════════════════════════════╝")
        choice = int(input("Enter choice [1-3]: "))
        
        if choice == 1:
            prepare_text_encoding()
        elif choice == 2:
            decode_hidden_text()
        elif choice == 3:
            break

# image menu
def image_steg_menu():
    while True:
        print("\n╔════════════════════════════════════╗")
        print("║      IMAGE STEGANOGRAPHY MENU      ║")
        print("╠════════════════════════════════════╣")
        print("║ 1. Encode message                  ║")
        print("║ 2. Decode message                  ║")
        print("║ 3. Return to main menu             ║")
        print("╚════════════════════════════════════╝")
        choice = int(input("Enter choice [1-3]: "))
        
        if choice == 1:
            img = cv2.imread("sample_files/sampleimage.jpg")
            encode_image_data(img)
        elif choice == 2:
            img_path = input("Enter image path: ")
            img = cv2.imread(img_path)
            decode_image_data(img)
        elif choice == 3:
            break

# main menu
def main_menu():
    while True:
        print("\n╔════════════════════════════════════╗")
        print("║         MAIN STEGANOGRAPHY MENU    ║")
        print("╠════════════════════════════════════╣")
        print("║ 1. Image Steganography             ║")
        print("║ 2. Text Steganography              ║")
        print("║ 3. Exit                            ║")
        print("╚════════════════════════════════════╝")
        choice = int(input("Enter choice [1-3]: "))
        
        if choice == 1:
            image_steg_menu()
        elif choice == 2:
            text_steg_menu()
        elif choice == 3:
            print("Exiting program...")
            return

# run program
if __name__ == "__main__":
    main_menu()