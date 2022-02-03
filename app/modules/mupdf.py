import io
import sys
import fitz
from os import path, mkdir
from tempfile import mkdtemp
from datetime import date
from PIL import Image


def get_meta(file) -> [list, None]:
    '''
    Get metadata from file
    '''
    try:
        with fitz.open(file) as doc:
            meta = doc.metadata
    except:
        return None
    return meta

def get_book_info(file) -> tuple:
    '''
    Get title, authors and date from book file
    '''
    pages = 0
    try:
        with fitz.open(file) as doc:
            meta = doc.metadata
            pages = doc.page_count
    except Exception as err:
        return (None, None, None, pages)
    title, authors, date_ = meta["title"], meta["author"], meta["creationDate"]
    except_ = ["unknown", "untitled", ""]
    title = None if any([(i == title.lower()) for i in except_]) else title
    authors = None if any([(i == authors.lower()) for i in except_]) else authors
    date_ = None if any([(i == date_.lower()) for i in except_]) else date_
    authors_out = []
    if authors:
        # Split multiple authors
        authors = authors.split(",") if "," in authors else [authors]
        # Create seq (first name, last name) by space
        for author in authors:
            try:
                f_name, l_name = author.split(" ", 1)
            except:
                f_name = l_name = None
            authors_out.append([f_name, l_name] if all([f_name, l_name])
                else [author, "Unknown"])
    if date_:
        try:
            date_ = date_.split("D:")[1]
            iso = "-".join([date_[:4], date_[4:6], date_[6:8]])
            date_ = date.fromisoformat(iso)
        except:
            pass
    return (title, authors_out, date_, pages)

def get_toc(file) -> [list, None]:
    '''
    Get book's table of content
    '''
    try:
        with fitz.open(file) as doc:
            toc = doc.get_toc()
    except:
        return None
    return toc

def get_data(file) -> [list, None]:
    '''
    Get text from book file
    '''
    try:
        with fitz.open(file) as doc:
            page = doc.load_page(0)
            text = page.get_text("text")
    except:
        return None
    return text

def get_pdf_images(file, page = 0) -> [list, None]:
    '''
    Get images from pdf file
    '''
    try:
        doc = fitz.open(file)
    except:
        return None
    img_num = 0
    p_no = page
    images = []
    tmp_path = path.normpath(mkdtemp(prefix="book_img_"))
    pixmap, path_join = fitz.Pixmap, path.join
    for img in doc.get_page_images(0):
        tmp_file = pix = None
        xref = img[0]
        pix = pixmap(doc, xref)
        tmp_file = path_join(tmp_path, ''.join(
            ["img_", str(p_no), "_", str(img_num), ".png"]))
        pix = pix if pix.n - pix.alpha < 4 else pixmap(fitz.csRGB, pix)
        pix.save(tmp_file)
        img_num += 1
        images.append(tmp_file)

    doc.close()
    doc = None
    return images

def get_cover_img(file, max_size = None,
    prefix = "img_from_book_") -> [str, None]:
    '''
    Get cover image from book, convert it to RGB, resize by max_size
    '''
    try:
        doc = fitz.open(file)
    except Exception as err:
        return None
    page_ = doc.load_page(0)
    d = page_.get_text("dict")
    imgblock = None
    for b in d["blocks"]:
        if b["type"] == 1 and b["width"] > 128:
            imgblock = b
            break

    if not imgblock:
        return None

    try:
        im = Image.open(io.BytesIO(imgblock["image"]))
    except:
        return None
    if not im.mode == "RGB":
        im = im.convert("RGB")
    if max_size:
        im.thumbnail((max_size[0], max_size[1]))
    tmp_path = path.normpath(mkdtemp(prefix=prefix))
    tmp_cover = path.join(tmp_path, "cover.png")
    im.save(tmp_cover)

    doc.close()
    doc = None

    return tmp_cover

def convert_to_pdf(file, out_path = None) -> None:
    '''
    Convert book to pdf
    '''
    if not (list(map(int, fitz.VersionBind.split("."))) >= [1,14,0]):
        raise SystemExit("need PyMuPDF v1.14.0+")

    try:
        doc = fitz.open(file)
    except Exception as err:
        return
    b = doc.convert_to_pdf()  # convert to pdf
    pdf = fitz.open("pdf", b)  # open as pdf

    toc = doc.get_toc()  # table of contents of input
    pdf.set_toc(toc)  # simply set it for output
    meta = doc.metadata  # read and set metadata
    if not meta["producer"]:
        meta["producer"] = ''.join(["PyMuPDF v", fitz.VersionBind])

    if not meta["creator"]:
        meta["creator"] = "PyMuPDF PDF converter"
    meta["modDate"] = fitz.get_pdf_now()
    meta["creationDate"] = meta["modDate"]
    pdf.set_metadata(meta)

    # Process the links
    for pinput in doc:  # iterate through input pages
        try:
            links = pinput.get_links()  # get list of links
            pout = pdf[pinput.number]  # read corresp. output page
            for l in links:  # iterate though the links
                if l["kind"] == fitz.LINK_NAMED:  # we do not handle named links
                    continue
                pout.insert_link(l)  # simply output the others
        except:
            pass

    # save the conversion result
    tmp_file = ''.join([path.split(file)[1], ".pdf"])
    if out_path:
        if not path.exists(out_path):
            mkdir(out_path)
        tmp_file = path.join(out_path, tmp_file)
    pdf.save(tmp_file, garbage=4, deflate=True)
    doc.close()
    pdf.close()
