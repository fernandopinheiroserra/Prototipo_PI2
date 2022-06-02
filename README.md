# Prototipo_PI2

Protótipo do Projeto Integrador 2<br>
Univesp - 2022 - Turma 38<br>
Referente ao projeto Alfabetiza Já<br>

<h3> Comandos para criação do ambiente e execução do projeto</h3>
<table>
  <tr>
    <td>python3 -m venv venv</td>
    <td>Criação do ambiente virtual</td>
  </tr>
  <tr>
    <td>pip install -r requirements.txt</td>
    <td>Instalação dos pacotes necessários para executar a aplicação</td>
  </tr>
  <tr>
    <td>python -m pip install --upgrade pip</td>
    <td>Atualização do pip (opcional)</td>
  </tr>
  <tr>
    <td>flask run</td>
    <td>Execução servidor para testes</td>
  </tr>
</table>

Organização das pastas<br>
/static - Arquivos estáticos do projetos, no caso está con o CSS<br>
/Tela_html_css - Arquivos com as telas inicias (antes do protótipo em Python) em HTML e CSS<br>
/templates - Arquivso HTML, que server como templates para uso do projeto<br>
/templates/alunos - Templates para o cadastro de alunos<br>
/templates/funcionaris - Templates para o cadastro de colaboradores<br>
/templates/historicos - Templates para a tabela de históricos<br>
/templates/menus - Templates para as telas de menu<br>
/templates/mudancas - Templates para as mudanças de turma e nivel<br>
/templates/relatorios - Templates para as rotinas de relatórios<br>
/templates/turmas - Templates para o cadastro de turmas<br>
/templates/base.html - Arquivo base para os outros templates<br>

Arquivos<br>
script.sql - Script para criação do banco de dados<br>
requirements.txt - Arquivo contendo a listagem dos pacotes necessários para funcionamento do projeto<br>
app.py - Programa em Python, que contém todas as rotinas<br>
database.db - Banco de dados SQLite<br>
init_db.py - Programa em Python, que cria os bancos de dados, usando o script.sql<br>
Procfile - Arquivo do Heroku<br>
/templates/index.html - Página inicial do projeto<br>


Protótipo - telas<br>
https://www.figma.com/file/uA3eyplUGTAtrW5s8WGmTO/Projeto-Integrador?node-id=0%3A1
