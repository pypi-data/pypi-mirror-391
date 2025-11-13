import os
from pygenpdf import *

def main():
    doc = Document()
    dir_now = os.path.dirname(os.path.abspath(__file__))
    doc.set_default_font(dir_now + "/liberation", "LiberationSans")
    doc.set_title("report genpdf")
    doc.set_paper_size(Size().A4())
    doc.set_head_page(Paragraph("report genpdf-rs from python").aligned(Alignment.RIGHT).styled(Style().bold().italic().with_font_size(8)))
    doc.set_margins(Margins().trbl(7,10,10,10))
    doc.set_line_spacing(1.0)             
    
    
    doc.push(Text(StyledString("Dpto Purchases", Style().with_font_size(40).bold().with_color(Color().greyscale(230)))).with_orphan(True).with_position(40,100))
    
    
    doc.render_json_file(dir_now + "/watermark_test.pdf")
    
    
if __name__=="__main__":
    main()
