from dotenv import load_dotenv
import time
import sys
import os

# pega o caminho da pasta onde o script está (ex: .../Automação_RH/scripts)
script_dir = os.path.dirname(os.path.abspath(__file__))
# pega o diretório "pai" da pasta do script (a raiz do projeto, ex: .../Automação_RH)
project_root = os.path.dirname(script_dir)
# adiciona a raiz do projeto à lista de caminhos do Python
sys.path.insert(0, project_root)

from core.logger_config import logger
try:
    from automations.daily import d1_individual_contributor
    from automations.daily import d2_work_anniversary
    logger.info("Daily automation modules imported successfully.")
except ImportError as e:
    logger.error(f"CRITICAL: Failed to import a daily automation module. Error: {e}", exc_info=True)
    sys.exit()

def main():
    """Orchestrator for DAILY HR automations."""
    start_time = time.time()
    logger.info("==========================================================")
    logger.info("  STARTING DAILY HR AUTOMATION RUN")
    logger.info("==========================================================")
    
    total_success = 0
    total_failed = 0
    
    # lista de tarefas diárias
    automation_tasks = [
        d1_individual_contributor,
        d2_work_anniversary
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
    total_time = end_time - start_time
    
    logger.info("==========================================================")
    logger.info("  DAILY HR AUTOMATION RUN FINISHED")
    logger.info(f"  - Total execution time: {total_time:.2f} seconds")
    logger.info(f"  - Total emails sent successfully: {total_success}")
    logger.info(f"  - Total emails failed: {total_failed}")
    logger.info("==========================================================")

if __name__ == "__main__":
    load_dotenv()
    main()