
import os
from pathlib import Path
import logging
from lxf.services.measure_time import measure_time_async
import lxf.settings as settings
settings.set_logging_level(logging.ERROR)
settings.enable_tqdm=False
###################################################################

logger = logging.getLogger('converter')
fh = logging.FileHandler('./logs/converter.log')
fh.setLevel(settings.get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(settings.get_logging_level())
logger.addHandler(fh)
#################################################################

from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.base import BaseChunk
from docling_core.transforms.chunker.hierarchical_chunker import HierarchicalChunker, DocChunk
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
    
async def converter_to_mardown(fullfilename:str)->tuple[int,str] :
    """
    Converti un fichier en Markdown
    return un tuple : error, Mardown | error_message si error!=0 
    """
    source = Path(fullfilename)
    if source.exists() :
        try:
            # Docling Parse with EasyOCR (default)
            # -------------------------------
            # Enables OCR and table structure with EasyOCR, using automatic device
            # selection via AcceleratorOptions. Adjust languages as needed.
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = True
            pipeline_options.do_table_structure = True
            pipeline_options.table_structure_options.do_cell_matching = True
            pipeline_options.ocr_options.lang = ["fr"]
            pipeline_options.accelerator_options = AcceleratorOptions(
                num_threads=4, device=AcceleratorDevice.AUTO
            )           
            doc_converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options,backend=PyPdfiumDocumentBackend)
                    
                }
            )             
            doc = doc_converter.convert(source).document    
            # chunker:HierarchicalChunker = HierarchicalChunker()        
            # chunks = chunker.chunk(dl_doc=doc)
            # for i , chk in enumerate(chunks) :
            #     doc_chunk = DocChunk.model_validate(chk)
            #     print(f"Titre : {' '.join(doc_chunk.meta.headings)}")
            #     print(doc_chunk.text)
            return 0,doc.export_to_markdown()
        except Exception as e :
            logging.error(e)
            return -2, e
    else :
        error = f"Le fichier {fullfilename} n'existe pas."
        logger.error(error)
        return -1 , error
    