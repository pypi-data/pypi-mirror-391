#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
from gui_stream.app_ui.ui.ui_pages import UiPage, TopBar
from gui_stream.app_ui.ui.widgets import (
    WidgetFiles, Orientation, WidgetScrow, WidgetExportFiles
)
from gui_stream.controller_app import Controller
from soup_files import File
import convert_stream as cs
from sheet_stream import TableDocuments, concat_table_documents


class PageConvertPdf(UiPage):
    
    def __init__(self, *, controller: Controller):
        super().__init__(controller=controller)
        self.controller: Controller = controller
        self.PAGE_ROUTE = '/home/pdf'
        self.PAGE_NAME = 'Conversão de PDF'
        self.GEOMETRY = '730x310'
        # 
        self.frameMain = ttk.Frame(self)
        self.frameMain.pack(expand=True, fill='both', padx=1, pady=1)
        
        # Frames 
        self.frameWidgets = ttk.Frame(self.frameMain)
        self.frameWidgets.pack(expand=True, fill='both')
        # Frame Scrow
        self.frameScrow = ttk.Frame(self.frameWidgets)
        self.frameScrow.pack(expand=True, fill='both', padx=1, pady=1, side=tk.LEFT)
        # Frame Export
        self.frameExport = ttk.Frame(self.frameMain)
        self.frameExport.pack(expand=True, fill='both', padx=1, pady=1)
        #
        self.w_file = WidgetFiles(
            self.frameScrow, 
            orientation=Orientation.H, 
            controller=self.controller,
            disk_files=self.select_disk_files,
        )
        self.w_file.set_button_pdf()
        self.w_file.set_button_image()
        self.w_file.set_button_folder()
        self.w_file.set_button_clear()
        #
        self.scrow: WidgetScrow = WidgetScrow(self.frameScrow, width=42, height=6)
        
        # Botão rotacionar
        self.frameRotate = ttk.Frame(self.frameScrow)
        self.frameRotate.pack(padx=1, pady=1)
        self.btn_rotate = ttk.Button(
            self.frameRotate,
            text='Rotacionar',
            command=self.execute_rotation,
            style=self.controller.buttonsTheme.value,
        )
        self.btn_rotate.pack(padx=1, pady=1, expand=True, fill='both')
        # Combo rotacionar
        self.combo_rotate = ttk.Combobox(
            self.frameRotate, 
            values=[
                    '90',
                    '180',
                    '270',
                    '-90',
                ],
        )
        self.combo_rotate.set('90')
        self.combo_rotate.pack(padx=1, pady=1)
        
        self.widgetExport: WidgetExportFiles = WidgetExportFiles(
            self.frameExport,
            controller=self.controller,
            orientation=Orientation.H,
        )
        self.widgetExport.set_button_uniq_pdf(self.export_uniq_pdf)
        self.widgetExport.set_button_image(self.export_images)
        self.widgetExport.set_button_pdf(self.export_multi_pdf)
        self.widgetExport.set_button_sheets(self.export_sheet)

        self.__pdf_stream: cs.PdfStream = None
        
    @property
    def stream_doc_pdf(self) -> cs.PdfStream:
        return self.__pdf_stream
    
    @stream_doc_pdf.setter
    def stream_doc_pdf(self, new: cs.PdfStream):
        self.__pdf_stream = new
        
    @property
    def topBar(self) -> TopBar:
        return self.controller.topBar
    
    def _create_stream_pdf(self) -> None:
        self.topBar.pbar.start()
        stream = cs.PdfStream(lib_pdf=cs.LibPDF.FITZ, pbar=self.topBar.pbar)

        # Adicionar arquivos PDF.
        stream.add_files_pdf(self.select_disk_files.get_files_pdf())
        # Adicionar arquivos de Imagem.
        stream.add_files_image(self.select_disk_files.get_files_image())
        self.stream_doc_pdf = stream
        self.topBar.set_text(f'-')
        self.topBar.pbar.stop()
    
    def export_uniq_pdf(self):
        if self.is_running():
            return
        self.thread_main_create(self._run_export_uniq_pdf)
    
    def _run_export_uniq_pdf(self):
        """
            Exportar os dados de PdfStream() para único arquivo PDF.
        """
        if self.stream_doc_pdf is None:
            self._create_stream_pdf()
        self.topBar.pbar.start()
        self.topBar.set_text(f'Exportando PDF')
        output: File = self.controller.saveDir.concat('PDF', create=True).join_file('Documento.pdf')
        self.stream_doc_pdf.to_document().to_file(output)
        self.topBar.set_text(f'Arquivo exportado em: {output.basename()}')
        self.topBar.pbar.stop()

    def export_images(self):
        if self.is_running():
            return
        self.thread_main_create(self._run_export_images)
    
    def _run_export_images(self):
        """
            Exportar os dados de PdfStream() para arquivos de imagens no disco.
        """
        if self.stream_doc_pdf is None:
            self._create_stream_pdf()
        self.topBar.pbar.start()
        
        self.topBar.set_text(f'Exportando Imagens')
        output_dir = self.controller.saveDir.concat('PDF', create=True).concat('PDF Para Imagens', create=True)
        self.stream_doc_pdf.to_files_images(output_dir)
        self.topBar.set_text(f'Imagens exportadas em: {output_dir.basename()}')
        self.topBar.pbar.stop()
    
    def export_multi_pdf(self):
        if self.is_running():
            return
        self.thread_main_create(self._run_export_multi_pdf)
    
    def _run_export_multi_pdf(self):
        """
            Exportar cada página de PdfStream() para arquivos PDF no disco.
        """
        if self.stream_doc_pdf is None:
            self._create_stream_pdf()
        self.topBar.pbar.start()
        
        self.topBar.set_text(f'Exportando arquivos em PDF')
        output_dir = self.controller.saveDir.concat('PDF', create=True).concat('PDF Dividido', create=True)
        self.stream_doc_pdf.to_files_pdf(output_dir)
        self.topBar.set_text(f'Arquivos exportado em: {output_dir.basename()}')
        self.topBar.pbar.stop()
        
    def execute_rotation(self):
        if self.is_running():
            return
        self.thread_main_create(self._run_execute_rotation)
    
    def _run_execute_rotation(self):
        """
            Executar a rotação de páginas PDF.
        """
        if self.stream_doc_pdf is None:
            self._create_stream_pdf()
        self.topBar.pbar.start()
        self.topBar.set_text(f'Rotacionando páginas, aguarde!')
        tmp_collection = cs.CollectionPagePdf(self.stream_doc_pdf.to_document().to_pages())
        tmp_collection.set_rotation(int(self.combo_rotate.get()))
        self.stream_doc_pdf.clear()
        self.stream_doc_pdf.add_pages(tmp_collection)
        self.topBar.pbar.stop()
    
    def export_sheet(self):
        if self.is_running():
            return
        self.thread_main_create(self._run_export_sheet)
    
    def _run_export_sheet(self):
        self.topBar.pbar.start()
        self.topBar.set_text(f'Exportando Planilha Excel, aguarde!')

        output: File = self.controller.saveDir.concat('Planilhas', create=True).join_file('Documentos.xlsx')
        files_pdf: list[File] = self.select_disk_files.get_files_pdf()
        try:
            _tables: list[TableDocuments] = [cs.DocumentPdf(_file).to_dict() for _file in files_pdf]
            concat_table_documents(_tables).to_data().to_excel(output.absolute(), index=False)
        except Exception as e:
            print(e)
            self.topBar.set_text(f'Falha ao tentar exportar: {output.basename()}')
        else:
            self.topBar.set_text(f'Planilha exportada em: {output.basename()}')
        self.topBar.pbar.stop()
        
        