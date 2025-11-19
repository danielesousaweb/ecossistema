# ⚡ Quick Start - Configuração Rápida do Servidor

## 🚀 Instalação em 5 Minutos

### 1️⃣ Instalar Dependências (Ubuntu/Debian)

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar tudo de uma vez
sudo apt install -y python3.11 python3.11-venv python3-pip \
                    mariadb-server mariadb-client \
                    nginx supervisor git curl
```

### 2️⃣ Configurar MySQL

```bash
# Iniciar MySQL
sudo systemctl start mariadb
sudo systemctl enable mariadb

# Criar banco e usuário
sudo mysql << 'SQL'
CREATE DATABASE ecoh_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ecoh_user'@'localhost' IDENTIFIED BY 'SenhaSuperSegura123!';
GRANT ALL PRIVILEGES ON ecoh_db.* TO 'ecoh_user'@'localhost';
FLUSH PRIVILEGES;
SQL
```

### 3️⃣ Instalar Aplicação

```bash
# Criar diretório
sudo mkdir -p /opt/ecoh-mysql
sudo chown $USER:$USER /opt/ecoh-mysql

# Fazer upload e extrair
cd /opt
unzip ecoh-mysql.zip
cd ecoh-mysql/backend

# Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4️⃣ Configurar Ambiente

```bash
# Editar .env
nano /opt/ecoh-mysql/backend/.env
```

Altere a senha:
```env
MYSQL_PASSWORD=SenhaSuperSegura123!
```

### 5️⃣ Inicializar Banco

```bash
# Criar tabelas
mysql -u ecoh_user -p'SenhaSuperSegura123!' ecoh_db < schema.sql

# Popular com dados iniciais
cd /opt/ecoh-mysql/backend
source venv/bin/activate
python seed_data.py
```

### 6️⃣ Configurar Supervisor

```bash
# Criar configuração
sudo tee /etc/supervisor/conf.d/ecoh.conf > /dev/null << 'CONF'
[program:ecoh-backend]
directory=/opt/ecoh-mysql/backend
command=/opt/ecoh-mysql/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/ecoh/backend.err.log
stdout_logfile=/var/log/ecoh/backend.out.log
environment=MYSQL_HOST="localhost",MYSQL_PORT="3306",MYSQL_USER="ecoh_user",MYSQL_PASSWORD="SenhaSuperSegura123!",MYSQL_DATABASE="ecoh_db"
CONF

# Criar diretório de logs
sudo mkdir -p /var/log/ecoh
sudo chown www-data:www-data /var/log/ecoh

# Iniciar
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ecoh-backend
```

### 7️⃣ Configurar Nginx

```bash
# Criar configuração
sudo tee /etc/nginx/sites-available/ecoh > /dev/null << 'NGINX'
server {
    listen 80;
    server_name _;

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
NGINX

# Ativar
sudo ln -s /etc/nginx/sites-available/ecoh /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8️⃣ Testar

```bash
# Backend
curl http://localhost:8001/api/

# Através do Nginx
curl http://localhost/api/

# Ver produtos
curl http://localhost/api/products | jq
```

---

## 🔧 Comandos Úteis

### Gerenciar Serviço Backend

```bash
# Status
sudo supervisorctl status ecoh-backend

# Reiniciar
sudo supervisorctl restart ecoh-backend

# Parar
sudo supervisorctl stop ecoh-backend

# Ver logs
sudo tail -f /var/log/ecoh/backend.out.log
sudo tail -f /var/log/ecoh/backend.err.log
```

### Gerenciar MySQL

```bash
# Status
sudo systemctl status mariadb

# Conectar
mysql -u ecoh_user -p ecoh_db

# Ver produtos
mysql -u ecoh_user -p ecoh_db -e "SELECT sku, title FROM hemera_products;"

# Backup
mysqldump -u ecoh_user -p ecoh_db > backup.sql
```

### Gerenciar Nginx

```bash
# Status
sudo systemctl status nginx

# Testar config
sudo nginx -t

# Reiniciar
sudo systemctl reload nginx

# Ver logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🔒 Segurança Básica

```bash
# Firewall
sudo ufw enable
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 3306

# Permissões
sudo chown -R www-data:www-data /opt/ecoh-mysql
sudo chmod 640 /opt/ecoh-mysql/backend/.env
```

---

## 📊 Verificação de Saúde

```bash
# Script de verificação
cat > /tmp/check.sh << 'CHECK'
#!/bin/bash
echo "🔍 Verificando serviços..."
echo ""

# MySQL
if sudo systemctl is-active --quiet mariadb; then
    echo "✅ MySQL: Rodando"
else
    echo "❌ MySQL: Parado"
fi

# Backend
if sudo supervisorctl status ecoh-backend | grep -q RUNNING; then
    echo "✅ Backend: Rodando"
else
    echo "❌ Backend: Parado"
fi

# Nginx
if sudo systemctl is-active --quiet nginx; then
    echo "✅ Nginx: Rodando"
else
    echo "❌ Nginx: Parado"
fi

echo ""
echo "🌐 Testando API..."
if curl -s http://localhost:8001/api/ | grep -q "MySQL Edition"; then
    echo "✅ API: Respondendo"
else
    echo "❌ API: Não responde"
fi

echo ""
echo "📊 Contagem de produtos:"
mysql -u ecoh_user -p'SenhaSuperSegura123!' ecoh_db -N -e "SELECT COUNT(*) FROM hemera_products;"
CHECK

bash /tmp/check.sh
```

---

## 🆘 Problemas Comuns

### Backend não inicia

```bash
# Ver erro específico
sudo tail -50 /var/log/ecoh/backend.err.log

# Testar manualmente
cd /opt/ecoh-mysql/backend
source venv/bin/activate
python -m server
```

### Erro de conexão MySQL

```bash
# Verificar se MySQL está rodando
sudo systemctl status mariadb

# Testar credenciais
mysql -u ecoh_user -p'SenhaSuperSegura123!' ecoh_db -e "SELECT 1;"

# Ver logs MySQL
sudo tail -f /var/log/mysql/error.log
```

### Porta 8001 já em uso

```bash
# Ver o que está usando
sudo lsof -i :8001

# Parar processo anterior
sudo supervisorctl stop ecoh-backend
sudo kill -9 $(sudo lsof -t -i:8001)

# Reiniciar
sudo supervisorctl start ecoh-backend
```

---

## 📦 Variáveis de Ambiente

Arquivo: `/opt/ecoh-mysql/backend/.env`

```env
# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=ecoh_user
MYSQL_PASSWORD=SuaSenhaAqui
MYSQL_DATABASE=ecoh_db

# CORS (ajustar para produção)
CORS_ORIGINS=https://seudominio.com

# API
API_PORT=8001
```

---

## 🎯 Próximos Passos

1. ✅ Configurar domínio no DNS
2. ✅ Instalar SSL com Let's Encrypt
3. ✅ Configurar backup automático
4. ✅ Implementar monitoramento
5. ✅ Copiar frontend (se houver)

---

**Tempo estimado**: 5-10 minutos  
**Dificuldade**: Fácil  
**Testado em**: Ubuntu 20.04, 22.04
