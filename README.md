# Steganography Tool

A simple Python-based steganography tool for hiding secret messages in text and image files.

## Features

- **Text Steganography**: Hide messages in plain text files using zero-width characters
- **Image Steganography**: Embed secret data in images using LSB (Least Significant Bit) technique

## Requirements

- Python 3.x
- NumPy
- Pandas
- OpenCV (cv2)
- Matplotlib

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/steganography-tool.git
   cd steganography-tool
   ```

2. Install required packages:
   ```
   pip install numpy pandas opencv-python matplotlib
   ```

3. Create a `sample_files` directory with:
   - `sampletext.txt`: A text file to use as carrier for text steganography
   - `sampleimage.jpg`: An image to use as carrier for image steganography

## Usage

Run the program:
```
python steganography.py
```

### Text Steganography

1. Select "Text Steganography" from the main menu
2. Choose "Encode message" to hide a message in text
3. Enter your secret message (limited by carrier text size)
4. Enter filename for the output steganography file

To decode:
1. Select "Text Steganography" from the main menu
2. Choose "Decode message"
3. Enter the name of the steganography file to extract the hidden message

### Image Steganography

1. Select "Image Steganography" from the main menu
2. Choose "Encode message" to hide a message in an image
3. Enter your secret message
4. Enter filename for the output image with hidden data

To decode:
1. Select "Image Steganography" from the main menu
2. Choose "Decode message"
3. Enter the path to the image containing hidden data

## Important Notes

- For text steganography, maximum message length = (number of words in carrier text) ÷ 6
- For image steganography, maximum data = (width × height × 3) ÷ 8 bytes
