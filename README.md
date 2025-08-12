# Automação de Processos de RH com Python

## Resumo

Esse projeto é a refatoração de um sistema de alertas inicialmente feito com o power-automate. A ideia é implementar um sistema de monitoramento das automações (fluxo;alertas) com diversas melhorias.
No momento possui uma integração com google sheets onde encaminha as logs de envios para uma planilha dentro do workspace do google.
Trabalhando tambem em uma integracao com streamlit para analises a partir dos dados do google sheets

##  Funcionalidades (Features)

- **Alertas de Horas Extras (para RH):**
  - `Diário:` Envio de alerta individual para o colaborador que excedeu alguma regra (por exemplo, execução total do permitido)
  - `Semanal:` Envio de resumo consolidado para o gestor com a lista do seu time com a regra de limite de execução permitida.
  - `Semanal:` Envio de resumo consolidado para o coordenador com a lista da sua área com a regra de limite de execução permitida.
- **Comunicações de RH:**
  - `Diário:` Envio de e-mail comemorativo no aniversário de empresa de cada funcionário (ex> pessoa entrou dia 15/08/24, se rodar no dia 15/08/25 vai enviar um email de parabens por 1 ano, etc..)  .
  - `Diário:` Envio de lembrete para o gestor sobre o fim do período de experiência de um colaborador (em desenvolvimento).
- **Monitoramento e Auditoria:**
  - Registro de todas as ações em arquivos de log diários e rotacionados.
  - Integração com Google Sheets para manter um log histórico de auditoria e dashboards de status diário.
- **Templates Profissionais:**
  - E-mails em HTML com CSS, utilizando um sistema de templates com Jinja2 para garantir consistência visual e facilidade de manutenção.

## Arquitetura do Projeto

O projeto segue uma arquitetura de software profissional baseada no princípio da Separação de Responsabilidades para garantir manutenibilidade e escalabilidade.
-- em desenvolvimento

```
AUTOMAÇÃO_RH/
│
├── 📂 automations/         # Contém a lógica específica de cada automação (diária, semanal).
├── 📂 config/              # Centraliza todas as configurações da aplicação.
├── 📂 core/                # O "motor" reutilizável do projeto.
├── 📂 data/                # Arquivos de dados de entrada (ex: contributors.csv).
├── 📂 logs/                # Armazena os arquivos de log gerados a cada execução.
├── 📂 scripts/             # Orquestradores, os pontos de entrada para executar os fluxos.
├── 📂 templates/           # Modelos de e-mail em HTML (Jinja2).
├── .env                    # Arquivo LOCAL com senhas e segredos (ignorado pelo Git).
└── run_daily_tasks.py      # Exemplo de script orquestrador.
```

### Detalhes da Pasta `core/`
A pasta `core` é o coração da aplicação, contendo toda a lógica reutilizável:
-   `core/data_loader.py`: Responsável por carregar, processar e validar os dados brutos da fonte de entrada (ex: arquivo `.csv`).
-   `core/business_rules.py`: Contém a "inteligência" e as regras de negócio centrais. Suas funções recebem os dados já carregados e retornam listas de funcionários que atendem a critérios específicos.
-   `core/email_sender.py`: O "operário" de baixo nível para e-mails. Sua única tarefa é receber uma lista de e-mails já prontos e enviá-los em paralelo.
-   `core/email_service.py`: A camada de serviço de alto nível para e-mails. Ele orquestra a criação das mensagens, renderizando os templates antes de passar a lista para o `email_sender` enviar.
-   `core/gsheets_client.py`: O "cliente" de baixo nível para o Google Sheets. Lida com a autenticação e as operações básicas da API.
-   `core/gsheets_service.py`: A camada de serviço para a planilha. Contém funções de negócio como `log_dataframe_to_sheet`.
-   `core/logger_config.py`: Configura o sistema de logging para todo o projeto.
-   `core/utils.py`: Uma "caixa de ferramentas" com funções utilitárias reutilizáveis por todo o projeto.

## Como Executar (ainda nao foi revisado)

### Pré-requisitos
- Python 3.10+
- Um ambiente virtual (`.venv`)

### 1. Configuração do Ambiente
Clone o repositório e instale as dependências:
```bash
git clone [https://github.com/seu-usuario/automacao_rh.git](https://github.com/seu-usuario/automacao_rh.git)
cd automacao_rh
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuração das Credenciais
- **E-mail e App:** Copie o arquivo `.env.example` para um novo arquivo chamado `.env` e preencha com suas credenciais de e-mail (usando uma "Senha de App" do Google).
- **Google Sheets:** Siga o guia para criar uma Conta de Serviço no Google Cloud, baixe o arquivo de credencial JSON e salve-o na raiz do projeto como `google_credentials.json`. Lembre-se de compartilhar sua planilha com o e-mail da conta de serviço.

### 3. Execução
Os scripts principais estão na pasta `scripts/`. Para executar um fluxo, use:
```bash
# para rodar as tarefas diárias
python scripts/run_daily_tasks.py

# para rodar as tarefas semanais
python scripts/run_weekly_tasks.py
```

## 🗺️ Roadmap de Melhorias Futuras

Este projeto serve como uma base robusta para a construção de uma pipeline de dados de ponta a ponta, utilizando tecnologias modernas de mercado.

- [ ] **Fase 1: Data Lakehouse e Ingestão**
    - [ ] Migrar a fonte de dados de CSV para tabelas no **Databricks Delta Lake**.
    - [ ] Gerar dados e atualizar diariamente com groq/pandas

- [ ] **Fase 2: Transformação e Qualidade de Dados**
    - [ ] Implementar um projeto **dbt** para modelar e transformar os dados brutos em tabelas analíticas limpas.
    - [ ] Adicionar testes de qualidade de dados com **`dbt tests`** e validação de schema em Python com **`Pandera`**.

- [ ] **Fase 3: Conteinerização da Aplicação**
    - [ ] Implementar uma suíte de testes unitários com **`pytest`** para a lógica da aplicação Python.
    - [ ] Empacotar a aplicação completa (automações, core, etc.) em uma imagem **Docker**.

- [ ] **Fase 4: Orquestração e CI/CD**
    - [ ] Configurar **GitHub Actions** para automação de testes (CI) e build da imagem Docker (CD).
    - [ ] Desenvolver uma DAG no **Apache Airflow** para orquestrar a execução do `dbt` e do container Docker da aplicação.

- [ ] **Fase 5: Visualização e Ação**
    - [ ] Criar um dashboard interativo com **Streamlit** conectado diretamente ao Databricks para visualização de KPIs.
    - [ ] Manter e expandir o sistema de notificações por e-mail como a camada de "ação" da pipeline.
     


## Responsaveis

Eduardo Lima  
Victor Castro
