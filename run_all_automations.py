# 0_run_all_automations.py
import time
import sys
import os

# Pega o caminho absoluto da pasta onde este script está (a raiz do projeto)
# e o adiciona à lista de locais onde o Python procura por módulos.
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv
from core.logger_config import logger

try:
    from automations import a1_individual_contributor
    from automations import a2_consolidated_manager
    from automations import a3_consolidated_coordinator
    from automations import a4_work_anniversary
    logger.info("All automation modules imported successfully.")
except ImportError as e:
    logger.error(f"CRITICAL: Failed to import an automation module. Error: {e}")
    print(f"\nERRO DE IMPORTAÇÃO: {e}")
    print("Verifique se os nomes dos arquivos em 'automations/' estão corretos e se a pasta contém um arquivo '__init__.py'.\n")
    sys.exit() 

def main():
    """
    Main orchestrator to run all HR automations in sequence.
    """
    start_time = time.time()
    logger.info("==========================================================")
    logger.info("  STARTING DAILY HR AUTOMATION RUN")
    logger.info("==========================================================")
    
    total_success = 0
    total_failed = 0
    
    # Lista de automações para rodar
    automation_tasks = [
        a1_individual_contributor,
        a2_consolidated_manager,
        a3_consolidated_coordinator,
        a4_work_anniversary
    ]
    
    for task_module in automation_tasks:
        task_name = task_module.__name__
        try:
            logger.info(f"--- Orchestrator: Starting task {task_name} ---")
            success, failed = task_module.run()
            total_success += success
            total_failed += failed
            logger.info(f"--- Orchestrator: Task {task_name} finished. Results: {success} succeeded, {failed} failed. ---")
        except Exception as e:
            logger.error(f"A critical error occurred during task {task_name}: {e}", exc_info=True)

    end_time = time.time()
    total_time = end_time - time.time()
    
    logger.info("==========================================================")
    logger.info("  DAILY HR AUTOMATION RUN FINISHED")
    logger.info(f"  - Total execution time: {total_time:.2f} seconds")
    logger.info(f"  - Total emails sent successfully: {total_success}")
    logger.info(f"  - Total emails failed: {total_failed}")
    logger.info("==========================================================")

if __name__ == "__main__":
    load_dotenv()
    main()