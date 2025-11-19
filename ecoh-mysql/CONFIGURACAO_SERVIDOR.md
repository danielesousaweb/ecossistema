# 🖥️ Configuração do Servidor - ECOH MySQL Edition

## 📋 Requisitos Mínimos do Servidor

### Hardware Recomendado

```
┌─────────────────────┬──────────────┬──────────────┬──────────────┐
│ Componente          │ Mínimo       │ Recomendado  │ Produção     │
├─────────────────────┼──────────────┼──────────────┼──────────────┤
│ CPU                 │ 2 cores      │ 4 cores      │ 8+ cores     │
│ RAM                 │ 2 GB         │ 4 GB         │ 8+ GB        │
│ Disco               │ 20 GB        │ 50 GB        │ 100+ GB SSD  │
│ Banda               │ 10 Mbps      │ 100 Mbps     │ 1 Gbps       │
└─────────────────────┴──────────────┴──────────────┴──────────────┘
```

### Sistema Operacional

- **Ubuntu 20.04 LTS** ou superior
- **Debian 11** ou superior
- **CentOS 8** ou superior
- **RHEL 8** ou superior

---

## 🔧 Instalação Passo a Passo

### 1️⃣ Atualizar Sistema

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 2️⃣ Instalar Python 3.11+

```bash
# Ubuntu/Debian
sudo apt install -y python3.11 python3.11-venv python3-pip

# CentOS/RHEL
sudo yum install -y python3.11 python3-pip

# Verificar instalação
python3.11 --version
```

### 3️⃣ Instalar MySQL/MariaDB 10.11+

#### Opção A: MariaDB (Recomendado)

```bash
# Ubuntu/Debian
sudo apt install -y mariadb-server mariadb-client

# CentOS/RHEL
sudo yum install -y mariadb-server mariadb

# Iniciar serviço
sudo systemctl start mariadb
sudo systemctl enable mariadb

# Verificar status
sudo systemctl status mariadb
```

#### Opção B: MySQL 8.0

```bash
# Ubuntu/Debian
wget https://dev.mysql.com/get/mysql-apt-config_0.8.24-1_all.deb
sudo dpkg -i mysql-apt-config_0.8.24-1_all.deb
sudo apt update
sudo apt install -y mysql-server

# CentOS/RHEL
sudo yum install -y mysql-server

# Iniciar serviço
sudo systemctl start mysqld
sudo systemctl enable mysqld
```

### 4️⃣ Configurar Segurança MySQL

```bash
sudo mysql_secure_installation
```

**Responda as perguntas:**
- Set root password? **Y** (escolha uma senha forte)
- Remove anonymous users? **Y**
- Disallow root login remotely? **Y**
- Remove test database? **Y**
- Reload privilege tables? **Y**

### 5️⃣ Criar Banco de Dados e Usuário

```bash
# Conectar ao MySQL
sudo mysql -u root -p

# No console MySQL, execute:
CREATE DATABASE ecoh_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER 'ecoh_user'@'localhost' IDENTIFIED BY 'SuaSenhaForteAqui123!';

GRANT ALL PRIVILEGES ON ecoh_db.* TO 'ecoh_user'@'localhost';

FLUSH PRIVILEGES;

EXIT;
```

### 6️⃣ Verificar Conexão

```bash
mysql -u ecoh_user -p ecoh_db
# Digite a senha e você deve entrar no banco
```

---

## 📦 Instalação da Aplicação

### 1️⃣ Copiar Projeto para o Servidor

```bash
# Criar diretório
sudo mkdir -p /opt/ecoh-mysql
sudo chown $USER:$USER /opt/ecoh-mysql

# Fazer upload do projeto
scp ecoh-mysql.zip usuario@servidor:/opt/
cd /opt
unzip ecoh-mysql.zip
cd ecoh-mysql
```

### 2️⃣ Criar Ambiente Virtual

```bash
cd /opt/ecoh-mysql/backend

# Criar venv
python3.11 -m venv venv

# Ativar venv
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip
```

### 3️⃣ Instalar Dependências

```bash
# Dentro do venv ativado
pip install -r requirements.txt
```

### 4️⃣ Configurar Variáveis de Ambiente

```bash
# Editar arquivo .env
nano /opt/ecoh-mysql/backend/.env
```

**Configuração do `.env`:**

```env
# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=ecoh_user
MYSQL_PASSWORD=SuaSenhaForteAqui123!
MYSQL_DATABASE=ecoh_db

# CORS Configuration (ajustar para seu domínio em produção)
CORS_ORIGINS=https://seudominio.com,https://www.seudominio.com

# API Configuration
API_PORT=8001
```

### 5️⃣ Criar Schema do Banco

```bash
# Importar schema
mysql -u ecoh_user -p ecoh_db < /opt/ecoh-mysql/backend/schema.sql

# Verificar tabelas criadas
mysql -u ecoh_user -p ecoh_db -e "SHOW TABLES;"
```

### 6️⃣ Popular Banco com Dados Iniciais

```bash
cd /opt/ecoh-mysql/backend
source venv/bin/activate
python seed_data.py
```

---

## ⚙️ Configuração MySQL para Produção

### Editar Configuração MySQL

```bash
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
# ou
sudo nano /etc/my.cnf
```

### Configurações Recomendadas

```ini
[mysqld]
# Performance
max_connections = 200
innodb_buffer_pool_size = 2G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2

# Character set
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# Network
bind-address = 127.0.0.1
port = 3306
max_allowed_packet = 64M

# Query cache (desabilitado no MySQL 8.0+)
# query_cache_type = 0

# Logs
log_error = /var/log/mysql/error.log
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2

# Binary logs (para backup/replicação)
log_bin = /var/log/mysql/mysql-bin.log
expire_logs_days = 7
max_binlog_size = 100M
```

### Reiniciar MySQL

```bash
sudo systemctl restart mariadb
# ou
sudo systemctl restart mysqld
```

---

## 🚀 Configuração do Uvicorn (Backend)

### Opção 1: Systemd Service (Recomendado para Produção)

**Criar arquivo de serviço:**

```bash
sudo nano /etc/systemd/system/ecoh-backend.service
```

**Conteúdo:**

```ini
[Unit]
Description=ECOH Backend API
After=network.target mariadb.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/ecoh-mysql/backend
Environment="PATH=/opt/ecoh-mysql/backend/venv/bin"
Environment="MYSQL_HOST=localhost"
Environment="MYSQL_PORT=3306"
Environment="MYSQL_USER=ecoh_user"
Environment="MYSQL_PASSWORD=SuaSenhaForteAqui123!"
Environment="MYSQL_DATABASE=ecoh_db"
ExecStart=/opt/ecoh-mysql/backend/venv/bin/uvicorn server:app \
    --host 0.0.0.0 \
    --port 8001 \
    --workers 4 \
    --log-level info

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Ativar e iniciar:**

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar auto-start
sudo systemctl enable ecoh-backend

# Iniciar serviço
sudo systemctl start ecoh-backend

# Verificar status
sudo systemctl status ecoh-backend

# Ver logs
sudo journalctl -u ecoh-backend -f
```

### Opção 2: Supervisor

```bash
# Instalar supervisor
sudo apt install -y supervisor

# Criar configuração
sudo nano /etc/supervisor/conf.d/ecoh-backend.conf
```

**Conteúdo:**

```ini
[program:ecoh-backend]
directory=/opt/ecoh-mysql/backend
command=/opt/ecoh-mysql/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/ecoh/backend.err.log
stdout_logfile=/var/log/ecoh/backend.out.log
environment=MYSQL_HOST="localhost",MYSQL_PORT="3306",MYSQL_USER="ecoh_user",MYSQL_PASSWORD="SuaSenhaForteAqui123!",MYSQL_DATABASE="ecoh_db"
```

**Criar diretório de logs:**

```bash
sudo mkdir -p /var/log/ecoh
sudo chown www-data:www-data /var/log/ecoh
```

**Ativar:**

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ecoh-backend
sudo supervisorctl status
```

---

## 🌐 Configuração Nginx (Reverse Proxy)

### Instalar Nginx

```bash
sudo apt install -y nginx
```

### Criar Configuração do Site

```bash
sudo nano /etc/nginx/sites-available/ecoh
```

**Conteúdo:**

```nginx
# Backend API
upstream ecoh_backend {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name seudominio.com www.seudominio.com;

    # Logs
    access_log /var/log/nginx/ecoh_access.log;
    error_log /var/log/nginx/ecoh_error.log;

    # Backend API
    location /api/ {
        proxy_pass http://ecoh_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Frontend (se você tiver)
    location / {
        root /opt/ecoh-mysql/frontend/build;
        try_files $uri $uri/ /index.html;
        
        # Cache static files
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Limites
    client_max_body_size 10M;
}
```

### Ativar Site

```bash
# Criar symlink
sudo ln -s /etc/nginx/sites-available/ecoh /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Recarregar nginx
sudo systemctl reload nginx
```

### Configurar SSL com Let's Encrypt

```bash
# Instalar certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seudominio.com -d www.seudominio.com

# Testar renovação automática
sudo certbot renew --dry-run
```

---

## 🔒 Segurança do Servidor

### 1️⃣ Firewall (UFW)

```bash
# Habilitar UFW
sudo ufw enable

# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Bloquear acesso direto ao MySQL (apenas localhost)
sudo ufw deny 3306/tcp

# Verificar status
sudo ufw status
```

### 2️⃣ Fail2Ban

```bash
# Instalar
sudo apt install -y fail2ban

# Configurar
sudo nano /etc/fail2ban/jail.local
```

**Adicionar:**

```ini
[sshd]
enabled = true
port = 22
maxretry = 5
bantime = 3600

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
```

**Reiniciar:**

```bash
sudo systemctl restart fail2ban
```

### 3️⃣ Permissões de Arquivos

```bash
# Definir proprietário
sudo chown -R www-data:www-data /opt/ecoh-mysql

# Permissões seguras
sudo chmod -R 750 /opt/ecoh-mysql
sudo chmod 640 /opt/ecoh-mysql/backend/.env
```

---

## 📊 Monitoramento

### 1️⃣ Logs da Aplicação

```bash
# Backend logs (systemd)
sudo journalctl -u ecoh-backend -f

# Backend logs (supervisor)
tail -f /var/log/ecoh/backend.out.log

# Nginx logs
tail -f /var/log/nginx/ecoh_access.log
tail -f /var/log/nginx/ecoh_error.log

# MySQL logs
tail -f /var/log/mysql/error.log
```

### 2️⃣ Status dos Serviços

```bash
# Backend
sudo systemctl status ecoh-backend
# ou
sudo supervisorctl status ecoh-backend

# MySQL
sudo systemctl status mariadb

# Nginx
sudo systemctl status nginx
```

### 3️⃣ Monitorar MySQL

```bash
# Conexões ativas
mysql -u root -p -e "SHOW PROCESSLIST;"

# Status do servidor
mysql -u root -p -e "SHOW STATUS;"

# Uso de disco
du -sh /var/lib/mysql/

# Performance
mysql -u root -p -e "SHOW ENGINE INNODB STATUS\G"
```

---

## 🔄 Backup Automatizado

### Script de Backup

```bash
sudo nano /opt/ecoh-mysql/backup.sh
```

**Conteúdo:**

```bash
#!/bin/bash

# Configurações
BACKUP_DIR="/backup/ecoh"
DATE=$(date +%Y%m%d_%H%M%S)
MYSQL_USER="ecoh_user"
MYSQL_PASS="SuaSenhaForteAqui123!"
MYSQL_DB="ecoh_db"

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup do banco de dados
mysqldump -u $MYSQL_USER -p$MYSQL_PASS $MYSQL_DB > $BACKUP_DIR/ecoh_db_$DATE.sql

# Compactar
gzip $BACKUP_DIR/ecoh_db_$DATE.sql

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup concluído: $BACKUP_DIR/ecoh_db_$DATE.sql.gz"
```

**Tornar executável:**

```bash
sudo chmod +x /opt/ecoh-mysql/backup.sh
```

### Agendar com Cron

```bash
sudo crontab -e
```

**Adicionar:**

```cron
# Backup diário às 2h da manhã
0 2 * * * /opt/ecoh-mysql/backup.sh >> /var/log/ecoh/backup.log 2>&1
```

---

## 🧪 Verificação Final

### Checklist Pré-Produção

```bash
# ✅ 1. MySQL rodando
sudo systemctl status mariadb

# ✅ 2. Banco criado
mysql -u ecoh_user -p ecoh_db -e "SELECT COUNT(*) FROM hemera_products;"

# ✅ 3. Backend rodando
sudo systemctl status ecoh-backend

# ✅ 4. API respondendo
curl http://localhost:8001/api/

# ✅ 5. Nginx rodando
sudo systemctl status nginx

# ✅ 6. Firewall configurado
sudo ufw status

# ✅ 7. SSL ativo (se configurado)
curl -I https://seudominio.com

# ✅ 8. Backup funcionando
ls -lh /backup/ecoh/
```

---

## 📞 Troubleshooting

### Backend não inicia

```bash
# Ver logs completos
sudo journalctl -u ecoh-backend -n 100

# Testar manualmente
cd /opt/ecoh-mysql/backend
source venv/bin/activate
python -c "import server"
```

### MySQL não conecta

```bash
# Verificar socket
ls -l /var/run/mysqld/mysqld.sock

# Testar conexão
mysql -u ecoh_user -p -h 127.0.0.1 ecoh_db

# Ver logs
sudo tail -f /var/log/mysql/error.log
```

### Porta 8001 ocupada

```bash
# Ver o que está usando
sudo lsof -i :8001

# Matar processo
sudo kill -9 <PID>
```

---

## 📊 Recursos Adicionais

- **Documentação MySQL**: https://dev.mysql.com/doc/
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Nginx Docs**: https://nginx.org/en/docs/
- **Let's Encrypt**: https://letsencrypt.org/

---

**Última atualização**: 2025-11-18  
**Versão**: 2.0.0-mysql
