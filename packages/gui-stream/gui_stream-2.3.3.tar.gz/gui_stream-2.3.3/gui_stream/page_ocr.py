#!/usr/bin/env python3
#
from __future__ import annotations
from typing import List
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from gui_stream.app_ui import AbstractNotifyProvider
from gui_stream.controller_app import Controller
from gui_stream.app_ui.ui.ui_pages import UiPage
from gui_stream.app_ui.ui.widgets import (
    WidgetFiles, WidgetScrow, Orientation, ProgressBarAdapter
)
from gui_stream.app_ui.ui.ui_pages import TopBar
import convert_stream as cs
import ocr_stream as ocr
from soup_files import File


#========================================================#
# Reconhecer Texto em PDF
#========================================================#
class PageRecognizePDF(UiPage):
    def __init__(self, *, controller: Controller):
        super().__init__(controller=controller)
        self.controller: Controller = controller
        # Inscreverse no objeto notificador
        self.controller.controller_conf.add_observer(self)
        self.PAGE_ROUTE = '/home/ocr'
        self.PAGE_NAME = 'OCR Documentos'
        self.GEOMETRY = "630x345"
        self.reconized_pages: set[cs.PageDocumentPdf] = set()
        
        self.frameWidgets = ttk.Frame(self)
        self.frameWidgets.pack(expand=True, fill='both', padx=1, pady=1)
        # Frame para os botões de input
        self.frameInputFiles = ttk.Frame(
            self.frameWidgets,
            style=self.controller.appTheme.value,
        )
        self.frameInputFiles.pack(side=tk.LEFT, expand=True, fill='both', padx=2, pady=3)

        self.widget_input = WidgetFiles(
            self.frameInputFiles,
            controller=self.controller,
            orientation=Orientation.V,
            disk_files=self.select_disk_files,
        )
        self.widget_input.set_button_image()
        self.widget_input.set_button_pdf()
        self.widget_input.set_button_folder()
        self.widget_input.set_button_clear()

        # Frame a direita
        self.frame_r = ttk.Frame(self.frameWidgets, style=self.controller.appTheme.value)
        self.frame_r.pack(expand=True, padx=3, pady=2)

        # botões de ação
        self.frame_btns = ttk.Frame(self.frame_r)
        self.frame_btns.pack(expand=True, fill='both', padx=1, pady=1)
        # Botão exportar lote
        self.btn_export_multi = ttk.Button(
            self.frame_btns,
            text='Exportar lote PDF',
            command=self.recognize_to_pdfs,
            style=self.controller.buttonsTheme.value,
            width=16,
        )
        self.btn_export_multi.pack(side=tk.LEFT, padx=1, pady=1, expand=True)

        # Botão exportar único PDF.
        self.btn_export_uniq = ttk.Button(
            self.frame_btns,
            text='Exportar único PDF',
            command=self.recognize_to_uniq_pdf,
            style=self.controller.buttonsTheme.value,
            width=16,
        )
        self.btn_export_uniq.pack(padx=1, pady=1, expand=True)
        # Container Scrollbar
        self.frame_scrow = ttk.Frame(self.frame_r)
        self.frame_scrow.pack(expand=True, fill='both', padx=1, pady=1)
        self.scrow: WidgetScrow = WidgetScrow(self.frame_scrow, height=12)

        self.controller.windowButtons.append(self.btn_export_uniq)
        self.controller.windowButtons.append(self.btn_export_multi)
        self.controller.windowFrames.extend(
            [
                self.frameInputFiles,
                self.frame_btns,
            ]
        )

    @property
    def topBar(self) -> TopBar:
        return self.controller.topBar
    
    @property
    def pbar(self) -> ProgressBarAdapter:
        return self.controller.topBar.pbar

    def recognize_to_pdfs(self):
        if not self.get_binary_tess().exists():
            messagebox.showerror('Erro', 'Instale o tesseract para prosseguir!')
            return
        if self.is_running():
            messagebox.showwarning('Erro', 'Existe outra operação em andamento, aguarde!')
            return
        if (self.select_disk_files.num_files_image < 1) and (self.select_disk_files.num_files_pdf < 1):
            messagebox.showinfo('Selecione documentos', 'Selecione uma imagem ou PDF para prosseguir!')
            return
        self.thread_main_create(self._run_recognize_to_pdfs)
        
    def _run_recognize_to_pdfs(self):
        """
            Reconhecer os arquivos PDF e Imagens adicionadas e exportar para PDFs individuais.
        """
        self.pbar.start()
        files_image = self.select_disk_files.get_files_image()
        max_images = len(files_image)
        rec = ocr.RecognizeImage(self.controller.binary)
        # Reconhecer imagens.
        for num, file_img in enumerate(files_image):
            output_path: File = self.controller.controller_conf.save_dir.join_file(f'{file_img.name()}.pdf')
            if output_path.path.exists():
                self.update_text_scrow(f'[PULANDO]: o arquivo já existe: {output_path.basename()}')
                continue

            prog = (num / max_images) * 100
            self.pbar.update(
                prog, 
                f'Reconhecendo imagem: {num+1} de {max_images} {file_img.basename()}'
            )
            self.update_text_scrow(f'Reconhecendo imagem: {num+1} de {max_images} {file_img.basename()}')
            img = cs.ImageObject.create_from_file(file_img)
            img.set_landscape()
            tmp_doc: cs.DocumentPdf = rec.image_recognize(img).to_document()
            self.pbar.update(prog, f'Exportando: {output_path.basename()}')
            tmp_doc.to_file(output_path)
            del tmp_doc
            
        # Reconhecer os arquivos PDF
        rec_pdf = ocr.RecognizePdf(self.controller.binary)
        list_pdfs = self.select_disk_files.get_files_pdf()
        max_pdf = len(list_pdfs)
        pdf_stream = cs.PdfStream(pbar=self.pbar)
        pdf_stream.clear()
        for n, file_pdf in enumerate(list_pdfs):
            progress_files = ((n+1)/max_pdf) * 100
            self.pbar.update(
                progress_files, 
                f'Adicionando arquivo: {n+1} de {max_pdf} {file_pdf.basename()}'
            )
            self.update_text_scrow(f'Adicionando arquivo: {n+1} de {max_pdf} {file_pdf.basename()}')
            ocr_doc: cs.DocumentPdf = rec_pdf.recognize_document(cs.DocumentPdf(file_pdf))
            pdf_stream.add_document(ocr_doc)
            pdf_stream.to_files_pdf(self.controller.controller_conf.save_dir, prefix=file_pdf.name())
            pdf_stream.clear()
        self.pbar.update(100, 'Operação finalizada!')
        self.pbar.stop()
        self.thread_main_stop()

    def recognize_to_uniq_pdf(self):
        if not self.get_binary_tess().exists():
            messagebox.showerror('Erro', 'Instale o tesseract para prosseguir!')
            return
        if self.is_running():
            messagebox.showwarning('Erro', 'Existe outra operação em andamento, aguarde!')
            return
        if (self.select_disk_files.num_files_image < 1) and (self.select_disk_files.num_files_pdf < 1):
            messagebox.showinfo('Selecione documentos', 'Selecione uma imagem ou PDF para prosseguir!')
            return
        self.thread_main_create(self._run_recognize_uniq_pdf)

    def _run_recognize_uniq_pdf(self):
        self.pbar.start()
        _stream = cs.PdfStream(pbar=self.pbar)
        rec_pdf: ocr.RecognizePdf = ocr.RecognizePdf(self.controller.binary)
        rec_image: ocr.RecognizeImage = ocr.RecognizeImage(self.controller.binary)

        # Reconhecer as imagens e converter em páginas PDF para adicionar ao documento
        files_image: list[File] = self.select_disk_files.get_files_image()
        max_images: int = len(files_image)
        for num_image, file in enumerate(files_image):
            prog: float = ((num_image+1)/max_images) * 100
            self.pbar.update(prog, f'Reconhecendo imagem: {num_image+1} de {max_images}')
            self.update_text_scrow(f'Reconhecendo imagem: {num_image+1} de {max_images}')
            # Converter o arquivo em imagem e aplicar o OCR
            im = cs.ImageObject.create_from_file(file)
            document = rec_image.image_recognize(im).to_document()
            _stream.add_document(document)
        
        # Reconhecer PDF.
        list_files_pdf: list[File] = self.select_disk_files.get_files_pdf()
        max_pdf: int = len(list_files_pdf)
        for num_pdf, file in enumerate(list_files_pdf):
            prog: float = (num_pdf/max_pdf) * 100
            self.pbar.update(prog, f'Reconhecendo PDF: {num_pdf} de {max_pdf}')
            _stream.add_file_pdf(file)
            # Reconhecer cada página
            tmp_doc = rec_pdf.recognize_document(cs.DocumentPdf(file))
            _stream.add_document(tmp_doc)

        # Salvar o documento
        output_path: File = self.controller.controller_conf.save_dir.join_file('DocumentoOCR.pdf')
        if output_path.path.exists():
            # Renomear o arquivo repetido
            _count: int = 1
            while True:
                output_path = self.controller.controller_conf.save_dir.join_file(f'DocumentoOCR-({_count}).pdf')
                if not output_path.path.exists():
                    break
                _count += 1
        self.pbar.update_text(f'Salvando: {output_path.basename()}')
        self.update_text_scrow(f'Salvando: {output_path.basename()}')
        _stream.to_document().to_file(output_path)
        self.pbar.update(100, 'Operação finalizada!')
        self.pbar.stop()
        self.thread_main_stop()
        
    def get_binary_tess(self) -> ocr.BinTesseract:
        return self.controller.binary

    def get_recognize_image(self) -> ocr.RecognizeImage:
        return ocr.RecognizeImage(bin_tess=self.get_binary_tess())

    def update_text_scrow(self, value: str):
        # Adicionar textos
        self.scrow.update_text(value)
        
    def update_current_scrow_values(self, values: List[str], include_info=None):
        self.scrow.update_texts(values, include_info)
            
    def clear_current_scrow_bar(self):
        self.scrow.clear()  # Limpa todos os itens
        
    def receiver_notify(self, notify_provide: AbstractNotifyProvider = None):
        pass
        
    def set_size_screen(self):
        self.controller.geometry(self.GEOMETRY)
        self.controller.title(self.PAGE_NAME)

    def update_state(self):
        pass
