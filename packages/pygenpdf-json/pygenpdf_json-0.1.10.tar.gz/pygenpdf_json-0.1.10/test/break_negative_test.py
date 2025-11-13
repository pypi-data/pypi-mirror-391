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
    
    
    layout_horizontal = TableLayout([2,1,2]).styled(Style().with_font_size(11).with_color(Color().greyscale(100)))
    layout_horizontal.set_cell_decorator(FrameCellDecorator().with_line_style(True, True, True, LineStyle().with_thickness(.1).with_color(Color().greyscale(150))))
 
    
    layout_horizontal.push_row([Paragraph("test").aligned(Alignment.CENTER),Paragraph("break").aligned(Alignment.CENTER),Paragraph("negative").aligned(Alignment.CENTER)])    
    
    doc.push(layout_horizontal)
            
    layout_ver1 = VerticalLayout().padded(1)\
                                .styled(Style().bold().with_color(Color().greyscale(20)))\
                                .framed_trbl(
                                            LineStyle().with_thickness(.1).with_color(Color().greyscale(150)),
                                            False, True, False, True
                                            )
    
    layout_ver1.element(Paragraph("test").aligned(Alignment.CENTER))\
                .element(Paragraph("break").aligned(Alignment.CENTER))\
                 .element(Paragraph("negative").aligned(Alignment.CENTER))
             
    doc.push(Break(-0.1))
    doc.push(VerticalLayout().element(layout_ver1))
    
    layout_horizontal2 = TableLayout([1,1]).styled(Style().with_font_size(11).with_color(Color().greyscale(100)))
    layout_horizontal2.set_cell_decorator(FrameCellDecorator().with_line_style(True, True, True, LineStyle().with_thickness(.1).with_color(Color().greyscale(150))))                
    
    layout_horizontal2.push_row([Paragraph("test break").aligned(Alignment.CENTER),
                                 Paragraph("negative").aligned(Alignment.CENTER)])    
    
    doc.push(Break(-0.1))
    doc.push(layout_horizontal2)
    
    
    doc.render_json_file(dir_now + "/break_negative_test.pdf")
    
    
if __name__=="__main__":
    main()
