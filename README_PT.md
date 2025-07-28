# Configuração do Projeto de Legendas

Este projeto envolve processamento de vídeo, geração de legendas e aplicação de marca d'água com componentes em Perl e Python. Siga as instruções abaixo para configurar o ambiente de desenvolvimento e colocar o projeto em execução.

## Requisitos Prévios

Certifique-se de ter o seguinte software instalado em seu sistema:
- **Perl** (com os módulos necessários)
- **Python** (para tarefas de legenda e marca d'água)
- **Git** (para controle de versão)

### Perl
O projeto utiliza Perl para algumas tarefas principais de processamento de vídeo. Primeiro é preciso instalar as dependências necessárias de Perl.

#### Configurando o ambiente Perl
1. **Instalar os módulos Perl**:
   O projeto usa `cpan` para gerenciar dependências. Execute:
   ```bash
   cpanm --installdeps .
   ```
   Se não possuir `cpanm`, instale com:
   ```bash
   curl -L https://cpanmin.us | perl - App::cpanminus
   ```
2. **Makefile.PL**:
   Se for a primeira configuração, rode:
   ```bash
   perl Makefile.PL
   make
   ```
   Isso compilará as dependências e configurará tudo.

#### Executando scripts Perl
Para rodar os scripts Perl:
```
prove -lv t/17.download.t
perl -Ilib bin/4.driver.pl
perl -Ilib t/18.download.t
python bin/call_captions.py /media/fritz/9766-DD0B/2025-06-18/Tim_Ballard_20250618_watermarked.mp4
```
Isso iniciará o processamento de vídeo e geração de legendas.

---

### Python
O ambiente Python cuida da geração das legendas e da inserção de marca d'água nos vídeos. Você precisará configurar o ambiente virtual e instalar as dependências.

#### Configurando o ambiente Python
1. **Criar um ambiente virtual**:
   ```bash
   python3 -m venv new-env
   ```
   Ative o ambiente:
   - **macOS/Linux**:
     ```bash
     source new-env/bin/activate
     ```
   - **Windows**:
     ```bash
     new-env\Scripts\activate
     ```
2. **Instalar dependências Python**:
   ```bash
   pip install -r requirements.txt
   ```
   Caso necessário, gere o arquivo com:
   ```bash
   pip freeze > requirements.txt
   ```
3. **Configuração**:
   Os scripts utilizam arquivos de configuração:
   - `conf/config.json` (ajuste caminhos e opções do projeto)
   - `conf/app_config.json` (rotas específicas do sistema, logs etc.)
   Procure seções marcadas com `# CUSTOMIZE` para inserir seus valores.

#### Executando scripts Python
Rode:
```
python bin/call_captions.py /media/fritz/9766-DD0B/2025-06-18/Tim_Ballard_20250618_watermarked.mp4
```
Esse script gerará legendas para os vídeos no diretório indicado.

---

## Arquivos de Configuração

### **conf/config.json**
Contém as principais configurações de processamento de vídeo, incluindo marca d'água, legendas e efeito Ken Burns.
- **video_download**: parâmetros para download de vídeos
- **watermark_config**: fonte, cores e posições da marca d'água
- **ken_burns**: duração dos slides e brilho
- **captions**: aparência, posição e timing das legendas

### **conf/app_config.json**
Define ajustes específicos para cada sistema operacional. Edite:
- **python_path**: caminho do interpretador Python
- **base_dir**: diretório base do projeto
- **log_dir**: onde ficam os logs
- **image_dir**: local das imagens usadas como marca d'água
- **logging**: nível e saída dos registros

### Valores Personalizáveis
- **Caminhos**: personalize `source_path`, `cookie_path`, `image_dir` e outros
- **Registro**: ajuste níveis de log e locais dos arquivos
- **Marca d'água**: modifique `font`, `font_size` e `position` em `watermark_config`

---

## Controle de Versões
Este projeto utiliza Git. Para clonar o repositório:
```bash
git clone https://github.com/Perl72/captions.git
```
Para atualizar seu código:
```bash
git pull origin main
```
Para enviar suas modificações:
```bash
git add .
git commit -m "Sua mensagem"
git push origin main
```

---

## Licença

Este projeto está licenciado sob a Licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

