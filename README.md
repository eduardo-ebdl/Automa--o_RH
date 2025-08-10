pastas = 

automations

- a1 = alerta individual caso a pessoa tenha atingido a regra predefinida
- a2 = alerta para o gestor, com colaboradores do seu time que atingiram a regra
- a3 = mesma coisa do a2, porem para o coordenador com colaboradores da area
- a4 = alerta quando a pessoa faz um ano+ de empresa

core

- business rules = 
- data loader = 
- email sender = 
- google sheets client = 
- logger config =

data

- arquivo csv

logs

- arquivo de log por execucao (dia)

templates

- padrao de texto html estilizado com css para osa textos dos emails -- padrao por automacao 


---------------------------

ideias: 

realizar o  mesmo sistema de alertas com o power automate so que com python -- com potenciais melhorias, como logs e aviso de erros

orquestrar com docker + airflow // ou apenas airflow

otimizar os codigos -- facilitar manutencoes, ajustes, etc..

---------------------------

potenciais melhorias

> logs (acho q tem muita log, diminuir e deixar as realmente necessarias)
> logger ainda seria a melhor opcao? --duvida-- muito codigo
> jinja2 parece ser complexo- ver alternativas
> tentar reduzir a estrutura do codigo em uns 30% -- simplificar, facilitar manutencao e ajustes
> enriquecer os dados, por mais dados para nao consultar sempre do mesmo arquivo -- 
> ver como seria integracao caso os dados passem a vir de um snowflake ou databricks -- descobrir como seria, como implementar, e se consigo fazer testes
> definir uma paleta de cores
> terminar de documentar tudo em ingles
> procurar referencias na internet, buscar inspiracoes
> dedicar um pouco de tempo para seguranca \
> github actions
> pytest
> validar dados com pandas
> docker
> cli
> banco de dados
> otimizarw acesso api e retries
> doc
> airflow
> streamlit