# Steganography Tool - Babila, Bonos, Lumibao, Tocayon BSCS 3B

import numpy as np
import pandas as pd
import os
import cv2
from matplotlib import pyplot as plt
import sys

# TODO: Clean up this mess later - works for now though
# Global vars (I know, I know... but it's easier)
MAX_TEXT_LEN = 1000
TERMINATOR = "111111111111"

def txt_to_bin(text):
    # converts text to binary using some zero width chars
    # found this technique on stackoverflow lol
    txt_len = len(text)
    bin_str = ''
    
    # these are the invisible chars we use
    zw_chars = {
        "00": '\u200C',  # zero width non-joiner
        "01": '\u202C',  # pop directional formatting  
        "11": '\u202D',  # left-to-right override
        "10": '\u200E'   # left-to-right mark
    }
    
    # process each character
    for i in range(txt_len):
        ascii_val = ord(text[i])
        
        # some weird transformation I found online
        if ascii_val >= 32 and ascii_val <= 64:
            new_val = ascii_val + 48
        else:
            new_val = ascii_val - 48
            
        # XOR with 170 for "encryption" (not really secure but whatever)
        encrypted_val = new_val ^ 170
        
        # convert to 8-bit binary
        bin_byte = bin(encrypted_val)[2:].zfill(8)
        
        # add prefix based on original ascii range
        if ascii_val >= 32 and ascii_val <= 64:
            prefix = "0011"
        else:
            prefix = "0110"
            
        bin_str += prefix + bin_byte
    
    # add terminator so we know where to stop decoding
    final_bin = bin_str + TERMINATOR
    
    print("Binary conversion complete!")
    print(f"Total bits: {len(final_bin)}")
    
    # read the cover text file
    try:
        with open("sample_files/sampletext.txt", "r+") as src_file:
            pass
    except FileNotFoundError:
        print("ERROR: sampletext.txt not found! Make sure it's in sample_files/")
        return
    
    # get output filename from user
    out_file = input("\nWhat should I name the steganography file? ")
    if not out_file.endswith('.txt'):
        out_file += '.txt'
    
    # process the cover text
    src_file = open("sample_files/sampletext.txt", "r+")
    stego_file = open(out_file, "w+", encoding="utf-8")
    
    # split into words - probably not the most efficient way but it works
    all_words = []
    for line in src_file:
        words_in_line = line.split()
        all_words.extend(words_in_line)
    
    # hide the binary data
    bit_pos = 0
    word_idx = 0
    
    while bit_pos < len(final_bin) and word_idx < len(all_words):
        current_word = all_words[word_idx]
        hidden_stuff = ''
        
        # process 12 bits at a time (6 pairs of 2 bits each)
        for j in range(0, 12, 2):
            if bit_pos + j + 1 >= len(final_bin):
                break
                
            bit_pair = final_bin[bit_pos + j] + final_bin[bit_pos + j + 1]
            hidden_stuff += zw_chars[bit_pair]
        
        # write word with hidden chars
        stego_file.write(current_word + hidden_stuff + " ")
        bit_pos += 12
        word_idx += 1
    
    # write the rest of the words normally
    for i in range(word_idx, len(all_words)):
        stego_file.write(all_words[i] + " ")
    
    stego_file.close()
    src_file.close()
    
    print(f"\nDone! Created '{out_file}' successfully")
    print("The message is now hidden in the text file.")

def check_text_capacity():
    # check if our message can fit in the cover text
    word_cnt = 0
    
    try:
        with open("sample_files/sampletext.txt", "r") as f:
            for line in f:
                word_cnt += len(line.split())
    except:
        print("Can't find sampletext.txt - make sure it exists!")
        return False
    
    # rough calculation - need about 6 words per character
    max_chars = word_cnt // 6
    print(f"Cover text has {word_cnt} words")
    print(f"Can hide approximately {max_chars} characters")
    
    msg = input("Enter your secret message: ")
    
    if len(msg) <= max_chars:
        print("Message fits! Encoding now...")
        txt_to_bin(msg)
        return True
    else:
        print("Message is too long! Try a shorter one.")
        return check_text_capacity()  # try again

def bin_to_dec(binary_string):
    # simple binary to decimal converter
    return int(binary_string, 2)

def extract_hidden_text():
    # decode the hidden message from stego file
    # reverse mapping of the zero width chars
    char_map = {
        '\u200C': "00",
        '\u202C': "01", 
        '\u202D': "11",
        '\u200E': "10"
    }
    
    stego_filename = input("Enter the steganography file name: ")
    
    if not os.path.exists(stego_filename):
        print("File not found!")
        return
    
    extracted_bits = ""
    
    # read the file and extract hidden bits
    with open(stego_filename, "r", encoding="utf-8") as f:
        content = f.read()
        
        for char in content:
            if char in char_map:
                extracted_bits += char_map[char]
                
            # stop if we hit the terminator
            if extracted_bits.endswith(TERMINATOR):
                break
    
    if not extracted_bits.endswith(TERMINATOR):
        print("No hidden message found or file is corrupted!")
        return
    
    # remove terminator
    extracted_bits = extracted_bits[:-12]
    
    # decode the message
    decoded_msg = ""
    
    # process 12 bits at a time (4 prefix + 8 data)
    for i in range(0, len(extracted_bits), 12):
        if i + 11 >= len(extracted_bits):
            break
            
        prefix = extracted_bits[i:i+4]
        data_byte = extracted_bits[i+4:i+12]
        
        # reverse the encoding process
        decrypted = bin_to_dec(data_byte) ^ 170
        
        if prefix == "0110":
            original_ascii = decrypted + 48
        elif prefix == "0011":
            original_ascii = decrypted - 48
        else:
            continue  # skip invalid prefixes
            
        decoded_msg += chr(original_ascii)
    
    print(f"\nHidden message found: '{decoded_msg}'")

# IMAGE STEGANOGRAPHY FUNCTIONS

def convert_to_binary(data):
    # convert various data types to binary
    # this function is kinda messy but it works
    
    if type(data) == str:
        # string to binary
        result = ''.join([format(ord(c), "08b") for c in data])
        return result
    elif type(data) == bytes or type(data) == np.ndarray:
        # bytes/array to binary list
        return [format(byte, "08b") for byte in data]
    elif type(data) == int or type(data) == np.uint8:
        # single number to binary
        return format(data, "08b")
    else:
        print("ERROR: Unsupported data type!")
        return None

def hide_data_in_image(img):
    # LSB steganography - hide data in least significant bits
    secret_msg = input("Enter the message to hide: ")
    
    if not secret_msg:
        print("No message entered!")
        return
    
    # add delimiter to mark end of message
    secret_msg += '*^*^*'  # weird delimiter but it works
    
    output_name = input("Enter output image filename: ")
    if not any(output_name.endswith(ext) for ext in ['.jpg', '.png', '.bmp']):
        output_name += '.png'  # default to PNG
    
    # check if message fits in image
    total_pixels = img.shape[0] * img.shape[1]
    max_chars = (total_pixels * 3) // 8  # 3 color channels, 8 bits per char
    
    if len(secret_msg) > max_chars:
        print(f"Message too long! Max characters: {max_chars}")
        return
    
    # convert message to binary
    binary_msg = convert_to_binary(secret_msg)
    print(f"Message converted to {len(binary_msg)} bits")
    
    data_index = 0
    
    # iterate through image pixels
    for row in range(img.shape[0]):
        for col in range(img.shape[1]):
            pixel = img[row][col]
            
            # get RGB values as binary
            r_bin = convert_to_binary(pixel[0])
            g_bin = convert_to_binary(pixel[1]) 
            b_bin = convert_to_binary(pixel[2])
            
            # modify LSB of each channel if we have data left
            if data_index < len(binary_msg):
                # modify red channel LSB
                new_r = r_bin[:-1] + binary_msg[data_index]
                img[row][col][0] = int(new_r, 2)
                data_index += 1
                
            if data_index < len(binary_msg):
                # modify green channel LSB  
                new_g = g_bin[:-1] + binary_msg[data_index]
                img[row][col][1] = int(new_g, 2)
                data_index += 1
                
            if data_index < len(binary_msg):
                # modify blue channel LSB
                new_b = b_bin[:-1] + binary_msg[data_index]
                img[row][col][2] = int(new_b, 2)
                data_index += 1
            
            # break if all data is hidden
            if data_index >= len(binary_msg):
                break
        
        if data_index >= len(binary_msg):
            break
    
    # save the modified image
    success = cv2.imwrite(output_name, img)
    if success:
        print(f"Message hidden successfully in '{output_name}'!")
    else:
        print("Failed to save image!")

def extract_data_from_image(img):
    # extract hidden data from image LSBs
    binary_data = ""
    
    # extract LSBs from all pixels
    for row in range(img.shape[0]):
        for col in range(img.shape[1]):
            pixel = img[row][col]
            
            # get LSB from each color channel
            r_bin = convert_to_binary(pixel[0])
            g_bin = convert_to_binary(pixel[1])
            b_bin = convert_to_binary(pixel[2])
            
            binary_data += r_bin[-1]  # red LSB
            binary_data += g_bin[-1]  # green LSB  
            binary_data += b_bin[-1]  # blue LSB
    
    # convert binary back to text
    decoded_text = ""
    for i in range(0, len(binary_data), 8):
        if i + 7 < len(binary_data):
            byte = binary_data[i:i+8]
            try:
                char = chr(int(byte, 2))
                decoded_text += char
            except:
                break  # invalid character, probably reached end
    
    # find the delimiter
    if '*^*^*' in decoded_text:
        hidden_message = decoded_text.split('*^*^*')[0]
        print(f"\nHidden message: '{hidden_message}'")
    else:
        print("No hidden message found or delimiter missing!")

# MENU FUNCTIONS

def text_menu():
    # text steganography submenu
    while True:
        print("\n" + "="*40)
        print("    TEXT STEGANOGRAPHY")
        print("="*40)
        print("1. Hide message in text")
        print("2. Extract hidden message")  
        print("3. Back to main menu")
        print("="*40)
        
        try:
            choice = int(input("Choose option (1-3): "))
        except ValueError:
            print("Please enter a valid number!")
            continue
        
        if choice == 1:
            check_text_capacity()
        elif choice == 2:
            extract_hidden_text()
        elif choice == 3:
            break
        else:
            print("Invalid choice! Try again.")

def image_menu():
    # image steganography submenu  
    while True:
        print("\n" + "="*40)
        print("    IMAGE STEGANOGRAPHY")
        print("="*40)
        print("1. Hide message in image")
        print("2. Extract hidden message")
        print("3. Back to main menu")
        print("="*40)
        
        try:
            choice = int(input("Choose option (1-3): "))
        except ValueError:
            print("Please enter a valid number!")
            continue
            
        if choice == 1:
            # use default sample image
            try:
                img = cv2.imread("sample_files/sampleimage.jpg")
                if img is None:
                    print("ERROR: Cannot load sample image!")
                    print("Make sure 'sampleimage.jpg' exists in sample_files/")
                    continue
                hide_data_in_image(img)
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == 2:
            img_path = input("Enter path to steganography image: ")
            try:
                img = cv2.imread(img_path)
                if img is None:
                    print("Cannot load image! Check the path.")
                    continue
                extract_data_from_image(img)
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == 3:
            break
        else:
            print("Invalid choice! Try again.")

def main():
    # main program loop
    print("*" * 50)
    print("  STEGANOGRAPHY TOOL v1.0")
    print("  By: Babila, Bonos, Lumibao, Tocayon")
    print("  BSCS 3B - Information Security Project")
    print("*" * 50)
    
    while True:
        print("\n" + "="*40)
        print("         MAIN MENU")
        print("="*40)
        print("1. Image Steganography")
        print("2. Text Steganography") 
        print("3. Exit Program")
        print("="*40)
        
        try:
            choice = int(input("Select option (1-3): "))
        except ValueError:
            print("Please enter a number between 1-3!")
            continue
        except KeyboardInterrupt:
            print("\n\nProgram interrupted by user.")
            sys.exit(0)
        
        if choice == 1:
            image_menu()
        elif choice == 2:
            text_menu()
        elif choice == 3:
            print("\nThanks for using our steganography tool!")
            print("Goodbye!")
            break
        else:
            print("Invalid option! Please choose 1, 2, or 3.")

# run the program
if __name__ == "__main__":
    main()