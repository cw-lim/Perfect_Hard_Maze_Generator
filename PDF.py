import os
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter

def add_page_numbers_to_pdf(input_pdf, output_pdf):
    # Load the input PDF
    pdf_reader = PdfReader(input_pdf)
    pdf_writer = PdfWriter()
    
    # Create an in-memory buffer for page numbers
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    
    num_pages = len(pdf_reader.pages)
    
    # Draw page numbers on a separate page
    for i in range(num_pages):
        can.drawString(530, 20, str(i + 1))  # Position of the page number (adjust as needed)
        can.showPage()
    
    can.save()
    packet.seek(0)
    
    # Merge page numbers with the original PDF
    page_number_pdf = PdfReader(packet)
    
    for i in range(num_pages):
        page = pdf_reader.pages[i]
        page.merge_page(page_number_pdf.pages[i])
        pdf_writer.add_page(page)
    
    with open(output_pdf, "wb") as f_out:
        pdf_writer.write(f_out)

def resize_image_with_margins(image, a4_size, margins):
    # Resize image to fit within A4 size minus margins while maintaining aspect ratio
    a4_width, a4_height = a4_size
    margin_left, margin_top, margin_right, margin_bottom = margins

    # Calculate the width and height available for the image
    available_width = a4_width - margin_left - margin_right
    available_height = a4_height - margin_top - margin_bottom

    img_width, img_height = image.size

    # Calculate the scaling factor
    scale = min(available_width / img_width, available_height / img_height)
    
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)

    # Resize the image
    image = image.resize((new_width, new_height), Image.LANCZOS)
    return image

def combine_pngs_to_pdf(input_folder, output_pdf):
    images = [os.path.join(input_folder, f) for f in sorted(os.listdir(input_folder)) if f.lower().endswith('.png')]
    image_list = []
    
    # Define A4 dimensions and margins (in points)
    a4_width, a4_height = map(int, A4)  # Convert A4 dimensions to integers
    margins = (50, 50, 50, 50)  # (left, top, right, bottom) margins in points
    
    for image_path in images:
        image = Image.open(image_path)
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        # Resize the image to fit within A4 size minus margins
        image = resize_image_with_margins(image, (a4_width, a4_height), margins)
        # Create a new image with A4 size and paste the resized image onto it
        a4_image = Image.new('RGB', (a4_width, a4_height), (255, 255, 255))
        
        # Calculate position to center the image within the margins
        margin_left, margin_top, _, _ = margins
        left = margin_left
        top = margin_top
        
        a4_image.paste(image, (left, top))
        image_list.append(a4_image)
    
    # Check if there are any images to process
    if not image_list:
        raise ValueError("No PNG images found in the specified directory.")
    
    # Save images to a PDF in-memory
    pdf_bytes = BytesIO()
    image_list[0].save(pdf_bytes, format='PDF', save_all=True, append_images=image_list[1:])
    pdf_bytes.seek(0)
    
    # Write the PDF with page numbers
    temp_pdf_path = "temp_images.pdf"
    with open(temp_pdf_path, "wb") as temp_pdf:
        temp_pdf.write(pdf_bytes.read())
    
    add_page_numbers_to_pdf(temp_pdf_path, output_pdf)
    
    # Clean up temporary file
    os.remove(temp_pdf_path)

# Usage
input_folder = "perfect_hard_mazes_70_by_100"
output_pdf = "perfect_hard_mazes_70_by_100.pdf"
combine_pngs_to_pdf(input_folder, output_pdf)