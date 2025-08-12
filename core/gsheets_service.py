import pandas as pd
from core.gsheets_client import gsheets_client # Corrigido para gsheets_client em vez de sheets_client
from core.logger_config import logger
import config


def carregar_dados_funcionarios(spreadsheet_id, worksheet_name) -> pd.DataFrame | None:
    """
    Lê os dados da planilha e retorna como DataFrame do pandas.
    Retorna None em caso de erro.
    """
    try:
        worksheet = gsheets_client.get_worksheet(spreadsheet_id, worksheet_name)

        if not worksheet:
            return None

        data = worksheet.get_all_values()
        if not data or len(data) < 2: # garante que há cabeçalho e pelo menos uma linha de dados
            logger.warning(f"Nenhum dado encontrado na worksheet '{worksheet_name}'.")
            return pd.DataFrame() # retorna um DF vazio para consistência

        df = pd.DataFrame(data[1:], columns=data[0])
        logger.info(f"Planilha '{worksheet_name}' carregada com sucesso ({len(df)} registros).")
        return df

    except Exception as e:
        logger.error(f"Erro ao carregar dados da worksheet '{worksheet_name}': {e}", exc_info=True)
        return None


def log_dataframe_to_sheet(df: pd.DataFrame, spreadsheet_id: str, worksheet_name: str, mode: str = 'append') -> bool:
    """
    Registra um DataFrame em uma aba específica do Google Sheets.

    Args:
        df: O DataFrame a ser registrado.
        spreadsheet_id: O ID da planilha.
        worksheet_name: O nome da aba.
        mode: 'append' para adicionar linhas ou 'overwrite' para limpar e escrever.
    """
    try:
        if df.empty:
            logger.info(f"DataFrame for '{worksheet_name}' is empty. No action taken.")
            return True
        
        data_only_rows = df.astype(str).values.tolist()

        if mode == 'overwrite':
            # Para sobrescrever, a lista completa inclui os cabeçalhos
            data_rows_with_headers = [df.columns.tolist()] + data_only_rows
            success = gsheets_client.clear_and_write_rows(spreadsheet_id, worksheet_name, data_rows_with_headers)
        else: # O padrão é 'append'
            headers = df.columns.tolist()
            # Garante os cabeçalhos primeiro, depois adiciona apenas os dados
            gsheets_client.ensure_headers(spreadsheet_id, worksheet_name, headers)
            success = gsheets_client.append_rows(spreadsheet_id, worksheet_name, data_only_rows)

        if success:
            logger.info(f"DataFrame successfully logged to worksheet '{worksheet_name}' in '{mode}' mode.")
        
        return success

    except Exception as e:
        logger.error(f"Failed to log DataFrame to worksheet '{worksheet_name}': {e}", exc_info=True)
        return False