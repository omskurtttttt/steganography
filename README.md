# steganography

**steganography: Hide Messages in Text & Images**  
A Python-based tool to embed and extract secret messages using steganography techniques:  
- **Text Steganography**: Conceals data in text files using **zero-width Unicode characters**.  
- **Image Steganography**: Hides messages in images via **least significant bit (LSB)** substitution.  

**Features**:  
🔍 **Encode/Decode** messages in text (`.txt`) and images (`.png`, `.jpg`).  
📝 **Text**: Uses XOR transformations for basic obfuscation.  
🖼️ **Image**: Preserves visual quality while embedding data.  
🛠️ **CLI Interface**: Simple terminal prompts for ease of use.  

**Tech Stack**:  
- Python 3  
- OpenCV (for image processing)  
- Unicode character manipulation  

**Usage**:  
1. **Text Hiding**:  
   ```python  
   python steganography.py  
   # Choose "Text Steganography" → Encode/Decode  
   ```  
2. **Image Hiding**:  
   ```python  
   python steganography.py  
   # Choose "Image Steganography" → Encode/Decode  
   ```  

**Ideal For**:  
- Learning steganography basics.  
- Secure low-risk communication (e.g., watermarking).  

**Limitations**:  
- Text capacity depends on cover file size.  
- JPEG images may lose hidden data due to compression.  

---  

**Quick Start**:  
```bash  
git clone https://github.com/your-repo/steganography-tool.git  
pip install opencv-python  
python steganography.py  
```
