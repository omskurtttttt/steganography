# Steganography Tool - Bonos, Lumibao, Tocayon BSCS 3B

import numpy as np
import pandas as pd
import os
import cv2
from matplotlib import pyplot as plt

# Text Steganography Functions
def encode_text_to_binary(text):
    """
    Converts input text to binary using zero-width characters for steganography.
    Uses special Unicode characters to hide binary data between words in text.
    """
    text_length = len(text)
    binary_string = ''
    zero_width_codes = {"00": '\u200C', "01": '\u202C', "11": '\u202D', "10": '\u200E'}
    
    # Convert each character to binary with special prefixes
    for i in range(text_length):
        char_code = ord(text[i])
        if 32 <= char_code <= 64:
            transformed = char_code + 48
        else:
            transformed = char_code - 48
        encrypted = transformed ^ 170  # XOR encryption with key 170
        binary_byte = bin(encrypted)[2:].zfill(8)
        prefix = "0011" if 32 <= char_code <= 64 else "0110"
        binary_string += prefix + binary_byte
    
    final_binary = binary_string + "111111111111"  # Add terminator sequence
    print(f"Converted binary: {final_binary}")
    print(f"Binary length: {len(final_binary)}")
    
    # Open source text file and create output steganography file
    source_file = open("sample_files/sampletext.txt", "r+")
    output_filename = input("\nEnter steganography file name (with extension): ")
    stego_file = open(output_filename, "w+", encoding="utf-8")
    
    # Split source text into words
    words = []
    for line in source_file:
        words += line.split()
    
    # Hide binary data in zero-width characters between words
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
    
    # Write remaining words
    for remaining in range(len(words) - (len(final_binary)//12), len(words)):
        stego_file.write(words[remaining] + " ")
    
    stego_file.close()
    source_file.close()
    print("\nSteganography file created successfully")

# Text encoding preparation function
def prepare_text_encoding():
    """
    Prepares the text encoding process by checking if the message can fit in the carrier text.
    """
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

# Binary conversion helper function
def binary_to_decimal(binary_str):
    """
    Converts binary string to decimal integer.
    """
    return int(binary_str, 2)

# Text decoding function
def decode_hidden_text():
    """
    Extracts hidden text from a steganography file by identifying zero-width characters.
    """
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
    
    # Convert binary back to text
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

# Image Steganography Functions
def message_to_binary(message):
    """
    Converts different types of input to binary representation.
    Handles strings, bytes, numpy arrays, and integers.
    """
    if isinstance(message, str):
        return ''.join(format(ord(c), "08b") for c in message)
    elif isinstance(message, (bytes, np.ndarray)):
        return [format(byte, "08b") for byte in message]
    elif isinstance(message, (int, np.uint8)):
        return format(message, "08b")
    else:
        raise TypeError("Unsupported input type")

# Image encoding function
def encode_image_data(image):
    """
    Hides text data in an image using LSB (Least Significant Bit) steganography.
    Adds a terminator sequence to mark the end of hidden data.
    """
    secret_data = input("Enter data to encode: ") + '*^*^*'
    if not secret_data:
        raise ValueError("No data entered")
    
    output_filename = input("Enter output image name: ")
    max_bytes = (image.shape[0] * image.shape[1] * 3) // 8
    
    if len(secret_data) > max_bytes:
        raise ValueError("Data too large for image")
    
    binary_data = message_to_binary(secret_data)
    bit_index = 0
    
    # Modify the LSB of each color channel to hide data
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

# Image decoding function
def decode_image_data(image):
    """
    Extracts hidden data from an image by reading the LSB of each color channel.
    Stops at the terminator sequence '*^*^*'.
    """
    binary_stream = ""
    for row in image:
        for pixel in row:
            r, g, b = message_to_binary(pixel)
            binary_stream += r[-1] + g[-1] + b[-1]
    
    # Convert binary to characters
    decoded = ''.join([chr(int(binary_stream[i:i+8], 2)) for i in range(0, len(binary_stream), 8)])
    if '*^*^*' in decoded:
        print(f"Hidden message: {decoded.split('*^*^*')[0]}")

# Menu Systems
def text_steg_menu():
    """
    Menu interface for text steganography operations.
    """
    while True:
        print("\n╔════════════════════════════════════╗")
        print("║       TEXT STEGANOGRAPHY MENU      ║")
        print("╠════════════════════════════════════╣")
        print("║ 1. Encode message                 ║")
        print("║ 2. Decode message                 ║")
        print("║ 3. Return to main menu            ║")
        print("╚════════════════════════════════════╝")
        choice = int(input("Enter choice [1-3]: "))
        
        if choice == 1:
            prepare_text_encoding()
        elif choice == 2:
            decode_hidden_text()
        elif choice == 3:
            break

# Image steganography menu
def image_steg_menu():
    """
    Menu interface for image steganography operations.
    """
    while True:
        print("\n╔════════════════════════════════════╗")
        print("║      IMAGE STEGANOGRAPHY MENU      ║")
        print("╠════════════════════════════════════╣")
        print("║ 1. Encode message                 ║")
        print("║ 2. Decode message                 ║")
        print("║ 3. Return to main menu            ║")
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

# Main menu function
def main_menu():
    """
    Main program menu that provides entry points to different steganography methods.
    """
    while True:
        print("\n╔════════════════════════════════════╗")
        print("║         MAIN STEGANOGRAPHY MENU    ║")
        print("╠════════════════════════════════════╣")
        print("║ 1. Image Steganography            ║")
        print("║ 2. Text Steganography             ║")
        print("║ 3. Exit                           ║")
        print("╚════════════════════════════════════╝")
        choice = int(input("Enter choice [1-3]: "))
        
        if choice == 1:
            image_steg_menu()
        elif choice == 2:
            text_steg_menu()
        elif choice == 3:
            print("Exiting program...")
            return

# Program entry point
if __name__ == "__main__":
    main_menu()