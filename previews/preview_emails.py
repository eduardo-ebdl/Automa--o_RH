import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# caminhos dinâmicos
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
PREVIEWS_OUTPUT_DIR = PROJECT_ROOT / "previews_output"

def setup_jinja_env():
    """Configura o ambiente Jinja2."""
    return Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def render_and_save(jinja_env: Environment, template_path: str, context: dict):
    """Renderiza um template e o salva, garantindo que a pasta de destino exista."""
    try:
        template = jinja_env.get_template(template_path)
        output_html = template.render(context)

        # cria um nome de arquivo seguro para o output
        safe_name = template_path.replace(os.path.sep, "_")
        output_filepath = PREVIEWS_OUTPUT_DIR / safe_name

        # garante que o diretório onde o arquivo será salvo exista
        output_filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(output_html)
        print(f"✅ Preview gerado com sucesso: {output_filepath.name}")

    except Exception as e:
        print(f"❌ Falha ao gerar preview para {template_path}: {e}")

def main():
    """Encontra todos os templates HTML e gera pré-visualizações."""
    print("--- Gerando Previews dos Templates de E-mail ---")
    
    PREVIEWS_OUTPUT_DIR.mkdir(exist_ok=True)
    jinja_env = setup_jinja_env()

    full_sample_context = {
        "primary_color": "#4A1B9A", "logo_url": "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png",
        "button_url": "#", "button_text": "Ação", "dashboard_url": "#",
        "nome": "João da Silva (Exemplo)", "horas_trabalhadas": 12.5, "data": "10/08/2025", "limite_horas": 10,
        "anos_empresa": 3, "nome_gestor": "Ana Costa (Exemplo)", "data_resumo": "10/08/2025",
        "tabela_horas": "<p><i>[Tabela de horas do time apareceria aqui]</i></p>",
        "nome_coordenador": "Juliano Chaves (Exemplo)", "nome_area": "TI (Exemplo)",
        "resumo_area": "<p><i>[Resumo da área apareceria aqui]</i></p>",
    }

    for template_file in TEMPLATES_DIR.glob("**/*.html"):
        relative_path = template_file.relative_to(TEMPLATES_DIR).as_posix()
        if "base.html" in relative_path:
            continue
        render_and_save(jinja_env, relative_path, full_sample_context)

    print("\n🎯 Previews gerados com sucesso na pasta 'previews_output/'!")

if __name__ == "__main__":
    main()