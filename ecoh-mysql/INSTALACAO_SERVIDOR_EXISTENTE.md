# 🚀 Instalação em Servidor Existente - Guia Completo

## 📋 Informações Necessárias

Antes de começar, tenha em mãos:

```
✅ Servidor Web:
   - IP: _________________
   - Usuário: ____________
   - Senha: ______________
   - Diretório: __________
   - Python instalado: Sim
   - httpd (Apache): Sim

✅ Servidor de Banco de Dados:
   - IP: _________________
   - Database: ___________
   - Usuário: ____________
   - Senha: ______________
   - Porta: 3306 (padrão MySQL)
```

---

## 📝 PASSO 1: Criar Tabelas no Banco de Dados

### Opção A: Usando MySQL Workbench (Recomendado - Interface Gráfica)

1. **Abrir MySQL Workbench**
2. **Criar nova conexão:**
   - Connection Name: `ECOH Database`
   - Hostname: `[IP do servidor de banco]`
   - Port: `3306`
   - Username: `[usuário do banco]`
   - Password: `[senha do banco]` (clique em "Store in Keychain")
3. **Conectar**
4. **Abrir o arquivo schema.sql:**
   - Menu: `File` → `Open SQL Script`
   - Navegar até: `ecoh-mysql/backend/schema.sql`
5. **Executar o script:**
   - Selecione o banco de dados correto no dropdown
   - Clique no ícone de raio ⚡ ou pressione `Ctrl+Shift+Enter`
6. **Verificar:**
   - No painel esquerdo, clique em "Schemas" → Seu banco → "Tables"
   - Deve aparecer 5 tabelas criadas

### Opção B: Via Linha de Comando

```bash
# No seu computador local, dentro da pasta ecoh-mysql/backend/

mysql -h [IP_DO_BANCO] -u [USUARIO] -p [NOME_DATABASE] < schema.sql

# Exemplo:
# mysql -h 192.168.1.100 -u ecoh_user -p ecoh_db < schema.sql
```

### Opção C: Copiar e Colar no phpMyAdmin (se disponível)

1. Acessar: `http://[IP_DO_BANCO]/phpmyadmin`
2. Login com suas credenciais
3. Selecionar seu banco de dados
4. Clicar na aba "SQL"
5. Abrir o arquivo `schema.sql` em um editor de texto
6. Copiar todo o conteúdo
7. Colar na caixa de texto
8. Clicar em "Executar"

---

## 📤 PASSO 2: Fazer Upload do Projeto para o Servidor

### Opção A: Usando FileZilla (Recomendado)

1. **Baixar FileZilla:** https://filezilla-project.org/download.php?type=client
2. **Configurar conexão:**
   - Host: `sftp://[IP_DO_SERVIDOR]`
   - Usuário: `[seu_usuario]`
   - Senha: `[sua_senha]`
   - Porta: `22`
3. **Conectar**
4. **Navegar no lado direito para:** `[diretório fornecido pelo TI]`
5. **No lado esquerdo:** Navegar até a pasta `ecoh-mysql` no seu PC
6. **Arrastar a pasta `backend` para o servidor**
7. **Aguardar upload completar**

### Opção B: Usando SCP (Linux/Mac)

```bash
# No seu terminal local, dentro da pasta onde está ecoh-mysql/

scp -r ecoh-mysql/backend [usuario]@[IP_SERVIDOR]:[diretorio_destino]/

# Exemplo:
# scp -r ecoh-mysql/backend usuario@192.168.1.50:/var/www/ecoh/
```

### Opção C: Usando WinSCP (Windows)

1. **Baixar WinSCP:** https://winscp.net/eng/download.php
2. **Nova Conexão:**
   - Protocolo: `SFTP`
   - Host: `[IP_DO_SERVIDOR]`
   - Usuário: `[seu_usuario]`
   - Senha: `[sua_senha]`
3. **Conectar**
4. **Arrastar pasta `backend` do PC para o servidor**

---

## ⚙️ PASSO 3: Configurar o Projeto no Servidor

### 3.1. Conectar ao Servidor via SSH

```bash
# Windows: Use PuTTY ou Windows Terminal
# Linux/Mac: Use terminal

ssh [usuario]@[IP_SERVIDOR]

# Exemplo:
# ssh admin@192.168.1.50
```

### 3.2. Navegar até o diretório do projeto

```bash
cd [diretorio_fornecido_pelo_TI]/backend

# Exemplo:env
# cd /var/www/ecoh/backend
```

### 3.3. Editar arquivo .env com as credenciais REAIS

```bash
nano .env
```

**Configuração do .env:**

```env
# MySQL Database Configuration - BANCO REMOTO
MYSQL_HOST=[IP_DO_SERVIDOR_BANCO]
MYSQL_PORT=3306
MYSQL_USER=[usuario_do_banco]
MYSQL_PASSWORD=[senha_do_banco]
MYSQL_DATABASE=[nome_do_banco]

# CORS Configuration - DOMÍNIO DO SERVIDOR
CORS_ORIGINS=http://[IP_OU_DOMINIO_SERVIDOR],https://[DOMINIO_SE_TIVER]

# API Configuration
API_PORT=8001
```

**Exemplo preenchido:**

```env
MYSQL_HOST=192.168.1.100
MYSQL_PORT=3306
MYSQL_USER=ecoh_user
MYSQL_PASSWORD=Senha123Forte!
MYSQL_DATABASE=ecoh_production

CORS_ORIGINS=http://192.168.1.50,http://meusite.com.br

API_PORT=8001
```

**Salvar:** `Ctrl+X`, depois `Y`, depois `Enter`

### 3.4. Criar Ambiente Virtual Python

```bash
# Verificar versão do Python
python3 --version

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Seu prompt deve mudar para algo como: (venv) usuario@servidor:~$
```

### 3.5. Instalar Dependências

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências do projeto
pip install -r requirements.txt

# Isso pode demorar 2-5 minutos
```

### 3.6. Testar Conexão com o Banco

```bash
# Criar script de teste
cat > test_db.py << 'EOF'
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = pymysql.connect(
        host=os.environ['MYSQL_HOST'],
        port=int(os.environ['MYSQL_PORT']),
        user=os.environ['MYSQL_USER'],
        password=os.environ['MYSQL_PASSWORD'],
        database=os.environ['MYSQL_DATABASE']
    )
    print("✅ Conexão com MySQL bem-sucedida!")
    
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    print(f"✅ Tabelas encontradas: {len(tables)}")
    for table in tables:
        print(f"   - {table[0]}")
    
    conn.close()
except Exception as e:
    print(f"❌ Erro: {str(e)}")
EOF

# Executar teste
python test_db.py
```

**Resultado esperado:**
```
✅ Conexão com MySQL bem-sucedida!
✅ Tabelas encontradas: 5
   - acf_schema
   - hemera_products
   - status_checks
   - sync_logs
   - webhook_events
```

### 3.7. Popular Banco com Dados Iniciais (Opcional)

```bash
# Executar seed
python seed_data.py

# Deve mostrar:
# Products synced: 5
# Graph nodes: 54
# Graph edges: 77
```

---

## 🌐 PASSO 4: Configurar Apache (httpd)

### 4.1. Instalar mod_wsgi

```bash
# Verificar se já está instalado
httpd -M | grep wsgi

# Se não aparecer nada, instalar:
sudo yum install python3-mod_wsgi   # CentOS/RHEL
# ou
sudo apt install libapache2-mod-wsgi-py3   # Ubuntu/Debian
```

### 4.2. Criar arquivo WSGI

```bash
cd [diretorio_do_projeto]/backend

cat > wsgi.py << 'EOF'
import sys
import os

# Adicionar caminho do projeto
sys.path.insert(0, os.path.dirname(__file__))

# Ativar ambiente virtual
activate_this = os.path.join(os.path.dirname(__file__), 'venv/bin/activate_this.py')
if os.path.exists(activate_this):
    exec(open(activate_this).read(), {'__file__': activate_this})

# Importar aplicação
from server import app as application
EOF
```

### 4.3. Configurar VirtualHost do Apache

**Criar arquivo de configuração:**

```bash
sudo nano /etc/httpd/conf.d/ecoh.conf
# ou
sudo nano /etc/apache2/sites-available/ecoh.conf
```

**Conteúdo:**

```apache
<VirtualHost *:80>
    ServerName [SEU_DOMINIO_OU_IP]
    
    # Diretório do projeto
    DocumentRoot [CAMINHO_COMPLETO]/backend
    
    # Logs
    ErrorLog /var/log/httpd/ecoh_error.log
    CustomLog /var/log/httpd/ecoh_access.log combined
    
    # Configuração WSGI para FastAPI
    WSGIDaemonProcess ecoh python-home=[CAMINHO_COMPLETO]/backend/venv python-path=[CAMINHO_COMPLETO]/backend
    WSGIProcessGroup ecoh
    WSGIScriptAlias /api [CAMINHO_COMPLETO]/backend/wsgi.py
    
    # Permissões
    <Directory [CAMINHO_COMPLETO]/backend>
        Require all granted
    </Directory>
    
    # Variáveis de ambiente (IMPORTANTE!)
    SetEnv MYSQL_HOST [IP_DO_BANCO]
    SetEnv MYSQL_PORT 3306
    SetEnv MYSQL_USER [usuario]
    SetEnv MYSQL_PASSWORD [senha]
    SetEnv MYSQL_DATABASE [database]
</VirtualHost>
```

**Exemplo preenchido:**

```apache
<VirtualHost *:80>
    ServerName 192.168.1.50
    
    DocumentRoot /var/www/ecoh/backend
    
    ErrorLog /var/log/httpd/ecoh_error.log
    CustomLog /var/log/httpd/ecoh_access.log combined
    
    WSGIDaemonProcess ecoh python-home=/var/www/ecoh/backend/venv python-path=/var/www/ecoh/backend
    WSGIProcessGroup ecoh
    WSGIScriptAlias /api /var/www/ecoh/backend/wsgi.py
    
    <Directory /var/www/ecoh/backend>
        Require all granted
    </Directory>
    
    SetEnv MYSQL_HOST 192.168.1.100
    SetEnv MYSQL_PORT 3306
    SetEnv MYSQL_USER ecoh_user
    SetEnv MYSQL_PASSWORD Senha123Forte!
    SetEnv MYSQL_DATABASE ecoh_production
</VirtualHost>
```

### 4.4. Ativar Configuração

```bash
# CentOS/RHEL - já está ativo automaticamente

# Ubuntu/Debian - precisa ativar
sudo a2ensite ecoh
sudo a2enmod wsgi
```

### 4.5. Testar Configuração

```bash
# Testar sintaxe
sudo apachectl configtest
# ou
sudo httpd -t

# Deve retornar: Syntax OK
```

### 4.6. Reiniciar Apache

```bash
sudo systemctl restart httpd
# ou
sudo systemctl restart apache2

# Verificar status
sudo systemctl status httpd
```

---

## ✅ PASSO 5: Testar a API

### 5.1. Teste Local no Servidor

```bash
# Ainda conectado via SSH

# Teste 1: API respondendo
curl http://localhost/api/

# Deve retornar:
# {
#   "message": "CAS Tecnologia Ecosystem API - MySQL Edition",
#   "version": "2.0.0-mysql",
#   ...
# }

# Teste 2: Listar produtos
curl http://localhost/api/products

# Teste 3: Ver grafo
curl http://localhost/api/graph/complete
```

### 5.2. Teste do Seu Computador

```bash
# No seu navegador:
http://[IP_DO_SERVIDOR]/api/

# Ou no terminal:
curl http://[IP_DO_SERVIDOR]/api/
```

---

## 🔍 PASSO 6: Verificação Final

### Checklist Completo

```bash
# No servidor, criar script de verificação
cat > /tmp/check_ecoh.sh << 'EOF'
#!/bin/bash

echo "🔍 Verificando instalação ECOH..."
echo ""

# 1. Banco de dados
echo "1️⃣ Testando conexão MySQL..."
python3 << PYEOF
import pymysql, os
from dotenv import load_dotenv
load_dotenv('/var/www/ecoh/backend/.env')
try:
    conn = pymysql.connect(
        host=os.environ['MYSQL_HOST'],
        user=os.environ['MYSQL_USER'],
        password=os.environ['MYSQL_PASSWORD'],
        database=os.environ['MYSQL_DATABASE']
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM hemera_products")
    count = cursor.fetchone()[0]
    print(f"   ✅ Conectado! {count} produtos no banco")
    conn.close()
except Exception as e:
    print(f"   ❌ Erro: {e}")
PYEOF

echo ""

# 2. Apache
echo "2️⃣ Verificando Apache..."
if systemctl is-active --quiet httpd || systemctl is-active --quiet apache2; then
    echo "   ✅ Apache rodando"
else
    echo "   ❌ Apache parado"
fi

echo ""

# 3. API
echo "3️⃣ Testando API..."
if curl -s http://localhost/api/ | grep -q "MySQL Edition"; then
    echo "   ✅ API respondendo"
else
    echo "   ❌ API não responde"
fi

echo ""
echo "✅ Verificação completa!"
EOF

chmod +x /tmp/check_ecoh.sh
/tmp/check_ecoh.sh
```

---

## 🆘 Solução de Problemas

### Erro: "Connection refused" ao acessar API

```bash
# Verificar se Apache está rodando
sudo systemctl status httpd

# Ver logs de erro
sudo tail -50 /var/log/httpd/ecoh_error.log
sudo tail -50 /var/log/httpd/error_log

# Reiniciar Apache
sudo systemctl restart httpd
```

### Erro: "Access denied for user"

```bash
# Verificar credenciais no .env
cat /var/www/ecoh/backend/.env

# Testar conexão manualmente
mysql -h [IP_BANCO] -u [USUARIO] -p [DATABASE]

# Verificar se IP do servidor web tem permissão no MySQL
# No servidor de banco, execute:
mysql -u root -p
GRANT ALL PRIVILEGES ON [database].* TO '[usuario]'@'[IP_SERVIDOR_WEB]' IDENTIFIED BY '[senha]';
FLUSH PRIVILEGES;
```

### Erro: "ModuleNotFoundError: No module named 'xxx'"

```bash
# Reativar venv e reinstalar
cd /var/www/ecoh/backend
source venv/bin/activate
pip install -r requirements.txt
```

### API não responde após configuração

```bash
# 1. Verificar permissões
sudo chown -R apache:apache /var/www/ecoh
# ou
sudo chown -R www-data:www-data /var/www/ecoh

# 2. Verificar SELinux (CentOS/RHEL)
sudo setenforce 0   # Temporário para teste
# Se funcionar, configurar SELinux corretamente

# 3. Verificar firewall
sudo firewall-cmd --list-all
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
```

---

## 📊 Comandos Úteis

### Ver Logs em Tempo Real

```bash
# Logs do Apache
sudo tail -f /var/log/httpd/ecoh_error.log

# Logs do sistema
sudo journalctl -f

# Logs do MySQL (no servidor de banco)
sudo tail -f /var/log/mysql/error.log
```

### Reiniciar Serviços

```bash
# Apache
sudo systemctl restart httpd

# Recarregar configuração Apache (sem downtime)
sudo systemctl reload httpd
```

### Atualizar Código

```bash
cd /var/www/ecoh/backend

# Fazer backup
cp -r . ../backend_backup_$(date +%Y%m%d)

# Atualizar código (via git ou upload)
# ...

# Reinstalar dependências se necessário
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar Apache
sudo systemctl restart httpd
```

---

## 📝 Resumo dos Caminhos Importantes

```
Servidor Web:
  Projeto: [seu_diretorio]/backend/
  .env: [seu_diretorio]/backend/.env
  venv: [seu_diretorio]/backend/venv/
  Logs Apache: /var/log/httpd/ecoh_error.log
  Config Apache: /etc/httpd/conf.d/ecoh.conf

Servidor de Banco:
  Host: [IP_fornecido_pelo_TI]
  Database: [nome_fornecido_pelo_TI]
  Tabelas: 5 (criadas pelo schema.sql)

Acesso:
  API: http://[IP_SERVIDOR]/api/
  Docs: http://[IP_SERVIDOR]/api/docs (se ativado)
```

---

**✅ Instalação Completa!**

Qualquer dúvida, consulte os logs ou entre em contato com seu TI.
