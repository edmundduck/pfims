from ._anvil_designer import ExpenseFileUploadFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Utils import Routing
from ...Utils.ClientCache import ClientCache
from ...Utils import Constants as const
from ...Utils.Logger import ClientLogger

logger = ClientLogger()

class ExpenseFileUploadForm(ExpenseFileUploadFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        self.button_excel_next.visible = False
        self.button_pdf_next.visible = False
        self.dropdown_filetype.visible = False
        self.flow_panel_mappingrule.visible = False
        self.flow_panel_xlstab.visible = False
        self.valerror_title.visible = False
        self.valerror_1.visible = False

    def button_nav_upload_mapping_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_upload_mapping_form(self)

    def button_nav_input_exp_click(self, **event_args):
        """This method is called when the button is clicked"""
        Routing.open_exp_input_form(self)

    def dropdown_filetype_show(self, **event_args):
        """This method is called when the DropDown is shown on the screen"""
        cache_filetype = ClientCache('generate_mapping_type_dropdown')
        self.dropdown_filetype.items = cache_filetype.get_cache()

    def dropdown_mapping_rule_change(self, **event_args):
        """This method is called when an item is selected"""
        self.flow_panel_xlstab.visible = True if self.dropdown_mapping_rule.selected_value is not None else False

    @logger.log_function
    def file_loader_1_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        cache_filetype = ClientCache('generate_mapping_type_dropdown')
        self.sheet_tabs_panel.clear()
        if file is not None:
            self.valerror_title.visible = False
            self.valerror_1.visible = False
            self.label_filename.text = f"Uploaded filename, content type: {file.name}, {file.content_type}"
            if file.content_type == "application/pdf":
                self.flow_panel_mappingrule.visible = False
                self.button_excel_next.visible = False
                self.button_pdf_next.visible = True
                self.dropdown_filetype.visible = True
                self.dropdown_filetype.selected_value = cache_filetype.get_complete_key(const.FileImportType.PDF)
            elif file.content_type in ("application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", \
                                      "application/vnd.ms-excel.sheet.macroEnabled.12", "application/x-excel", "text/csv"):
                self.button_pdf_next.visible = False
                self.dropdown_filetype.visible = True
                self.dropdown_filetype.selected_value = cache_filetype.get_complete_key(const.FileImportType.Excel)
                xls = anvil.server.call('preview_file', file=file)
                for i in xls:
                    cb = CheckBox(
                        text=i,
                        font_size=12,
                        align="left",
                        spacing_above="small",
                        spacing_below="small"
                    )
                    self.sheet_tabs_panel.add_component(cb)
                    cb.set_event_handler('change', self.enable_excel_next_button)
                self.dropdown_mapping_rule.items = anvil.server.call('generate_mapping_dropdown', self.dropdown_filetype.selected_value[0] if self.dropdown_filetype.selected_value else None)
                self.flow_panel_mappingrule.visible = True
            else:
                self.flow_panel_mappingrule.visible = False
                self.flow_panel_xlstab.visible = False
                self.dropdown_filetype.visible = False
                self.dropdown_filetype.selected_value = None
                self.button_excel_next.visible = False
                self.button_pdf_next.visible = False
                self.valerror_title.visible = True
                self.valerror_1.visible = True

    def enable_excel_next_button(self, **event_args):
        cb = event_args['sender']
        vis = False
        if cb.checked:
            vis = True
        else:
            for i in cb.parent.get_components():
                if isinstance(i, CheckBox) and i.checked:
                    vis = True
        self.button_excel_next.visible = vis

    @logger.log_function
    def button_excel_next_click(self, **event_args):
        """This method is called when the button is clicked"""
        tablist = []
        for i in self.sheet_tabs_panel.get_components():
            if isinstance(i, CheckBox) and i.checked:
                tablist.append(i.text)
        logger.info(f"{len(tablist)} tabs are chosen in {__name__}.")
        matrix = anvil.server.call('select_mapping_matrix', id=self.dropdown_mapping_rule.selected_value)
        logger.debug("matrix=", matrix)
        extra = anvil.server.call('select_mapping_extra_actions', id=self.dropdown_mapping_rule.selected_value)
        logger.debug("extra=", extra)
        df, lbls = anvil.server.call('import_file', file=self.file_loader_1.file, tablist=tablist, rules=matrix, extra=extra)
        logger.trace("df=", df)
        logger.debug("lbls=", lbls)
        Routing.open_exp_file_excel_import_form(self, data=df, labels=lbls)

    @logger.log_function
    def button_pdf_next_click(self, **event_args):
        """This method is called when the button is clicked"""
        pdf_tbl = anvil.server.call('import_pdf_file', file=self.file_loader_1.file)
        logger.debug("pdf_tbl=", pdf_tbl)
        Routing.open_exp_file_pdf_import_form(self, data=pdf_tbl)
