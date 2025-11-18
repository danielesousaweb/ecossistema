# 🚀 Guia de Instalação no Servidor - Tech Mesh Sync

**Guia Passo-a-Passo Completo (Estilo Professor Paciente)**

Assumindo: Ubuntu 22.04 LTS em servidor com acesso SSH

---

## 📋 Pré-Requisitos do Servidor

Você vai precisar de:
- ✅ Servidor Linux (Ubuntu 22.04 LTS recomendado)
- ✅ Acesso SSH com usuário sudo
- ✅ Domínio DNS apontando para o servidor (ex: `techmesh.seudominio.com`)
- ✅ Pelo menos 2GB RAM, 20GB disco
- ✅ Portas abertas: 80 (HTTP), 443 (HTTPS), 22 (SSH)

---

## 🛠️ PASSO 1: Instalar Dependências Base

### 1.1 Atualizar Sistema

```bash
# Conectar via SSH
ssh usuario@seu-servidor.com

# Atualizar pacotes
sudo apt update
sudo apt upgrade -y
```

### 1.2 Instalar Git

```bash
sudo apt install -y git curl wget build-essential
```

### 1.3 Instalar Node.js (via fnm - recomendado)

```bash
# Instalar fnm (Fast Node Manager)
curl -fsSL https://fnm.vercel.app/install | bash

# Reiniciar shell
source ~/.bashrc

# Instalar Node 18 (versão do projeto)
fnm install 18
fnm use 18

# Verificar instalação
node -v  # deve mostrar v18.x.x
npm -v   # deve mostrar versão do npm
```

**Alternativa com nvm:**
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
```

### 1.4 Instalar MongoDB

```bash
# Importar chave pública
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

# Adicionar repositório
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Instalar
sudo apt update
sudo apt install -y mongodb-org

# Iniciar e habilitar
sudo systemctl start mongod
sudo systemctl enable mongod

# Verificar
sudo systemctl status mongod
```

### 1.5 Instalar Nginx

```bash
sudo apt install -y nginx

# Iniciar e habilitar
sudo systemctl start nginx
sudo systemctl enable nginx

# Verificar
sudo systemctl status nginx
```

### 1.6 Instalar Certbot (SSL Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 1.7 Instalar PM2 (Process Manager)

```bash
sudo npm install -g pm2
```

---

## 📦 PASSO 2: Clonar e Configurar Projeto

### 2.1 Criar Diretório

```bash
# Criar diretório do projeto
sudo mkdir -p /var/www/tech-mesh-sync

# Dar permissão ao seu usuário
sudo chown -R $USER:$USER /var/www/tech-mesh-sync

# Entrar no diretório
cd /var/www/tech-mesh-sync
```

### 2.2 Clonar Repositório

```bash
# Clonar (substitua pela URL real)
git clone https://github.com/seu-usuario/tech-mesh-sync.git .

# Se houver submódulos
git submodule update --init --recursive
```

### 2.3 Configurar Variáveis de Ambiente

**Backend (.env):**

```bash
# Criar arquivo .env no backend
cd /var/www/tech-mesh-sync/backend
nano .env
```

Adicionar:
```env
# MongoDB
MONGO_URL=mongodb://localhost:27017
DB_NAME=tech_mesh_sync

# CORS
CORS_ORIGINS=https://techmesh.seudominio.com

# Unopim (quando tiver credenciais reais)
UNOPIM_DB_TYPE=mysql
UNOPIM_DB_HOST=unopim-host.com
UNOPIM_DB_PORT=3306
UNOPIM_DB_NAME=unopim
UNOPIM_DB_USER=sync_user
UNOPIM_DB_PASSWORD=senha_segura

# Webhook
UNOPIM_WEBHOOK_SECRET=gerar-segredo-aleatorio-aqui
```

**Frontend (.env):**

```bash
cd /var/www/tech-mesh-sync/frontend
nano .env
```

Adicionar:
```env
REACT_APP_BACKEND_URL=https://techmesh.seudominio.com
```

---

## 🗄️ PASSO 3: Configurar Banco de Dados

### 3.1 Criar Database no MongoDB

```bash
# Conectar ao MongoDB
mongosh

# Dentro do MongoDB shell
use tech_mesh_sync

# Criar usuário (opcional mas recomendado)
db.createUser({
  user: "techmesh_user",
  pwd: "senha_super_segura_aqui",
  roles: [{ role: "readWrite", db: "tech_mesh_sync" }]
})

# Sair
exit
```

### 3.2 Popular com Dados Mock

```bash
cd /var/www/tech-mesh-sync/backend

# Instalar dependências Python (se usar Python backend)
pip3 install -r requirements.txt

# Rodar seed
python3 seed_data.py
```

**Saída esperada:**
```
============================================================
DATABASE SEEDED SUCCESSFULLY
============================================================
Products synced: 5
New fields detected: 23
Graph nodes: 54
Graph edges: 77
Clusters: 9
============================================================
```

---

## 🚀 PASSO 4: Instalar Dependências e Build

### 4.1 Backend

```bash
cd /var/www/tech-mesh-sync/backend

# Se Node.js backend (FastAPI usa Python)
# Instalar dependências Python
pip3 install -r requirements.txt

# OU se for Node.js
npm ci
npm run build  # se necessário
```

### 4.2 Frontend

```bash
cd /var/www/tech-mesh-sync/frontend

# Instalar dependências
npm ci

# Build para produção
npm run build

# Resultado: pasta /build com arquivos estáticos
```

---

## 🔧 PASSO 5: Configurar PM2 (Backend)

### 5.1 Criar Arquivo de Configuração PM2

```bash
cd /var/www/tech-mesh-sync
nano ecosystem.config.js
```

Adicionar:
```javascript
module.exports = {
  apps: [
    {
      name: 'techmesh-backend',
      cwd: '/var/www/tech-mesh-sync/backend',
      script: 'uvicorn',
      args: 'server:app --host 0.0.0.0 --port 8001',
      interpreter: 'python3',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production'
      }
    }
  ]
};
```

### 5.2 Iniciar com PM2

```bash
# Iniciar aplicação
pm2 start ecosystem.config.js

# Verificar status
pm2 status

# Ver logs
pm2 logs techmesh-backend

# Salvar configuração
pm2 save

# Habilitar startup automático
pm2 startup
# Copiar e executar o comando que aparecer
```

**Verificar se backend está rodando:**
```bash
curl http://localhost:8001/api/topicos
# Deve retornar JSON com tópicos
```

---

## 🌐 PASSO 6: Configurar Nginx

### 6.1 Criar Configuração do Site

```bash
sudo nano /etc/nginx/sites-available/techmesh
```

Adicionar:
```nginx
server {
    listen 80;
    server_name techmesh.seudominio.com;

    # Frontend estático
    root /var/www/tech-mesh-sync/frontend/build;
    index index.html;

    # Logs
    access_log /var/log/nginx/techmesh-access.log;
    error_log /var/log/nginx/techmesh-error.log;

    # Frontend - React Router
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API - Proxy reverso
    location /api/ {
        proxy_pass http://127.0.0.1:8001/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Otimizações
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Cache de assets estáticos
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 6.2 Ativar Site

```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/techmesh /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx
```

---

## 🔐 PASSO 7: Configurar SSL (HTTPS)

### 7.1 Obter Certificado SSL

```bash
# Certbot automático
sudo certbot --nginx -d techmesh.seudominio.com

# Seguir prompts:
# - Fornecer email
# - Aceitar termos
# - Escolher "2" para redirect HTTP → HTTPS
```

**Certbot vai:**
1. Obter certificado do Let's Encrypt
2. Modificar configuração Nginx automaticamente
3. Configurar renovação automática

### 7.2 Verificar Renovação Automática

```bash
# Testar renovação
sudo certbot renew --dry-run

# Deve mostrar: "Congratulations, all simulated renewals succeeded"
```

**Renovação automática já está configurada via systemd timer.**

---

## ⏰ PASSO 8: Configurar Sincronização (CRON)

### 8.1 Script de Sincronização

```bash
cd /var/www/tech-mesh-sync
nano sync-cron.sh
```

Adicionar:
```bash
#!/bin/bash
cd /var/www/tech-mesh-sync/backend
/usr/bin/python3 seed_data.py >> /var/log/techmesh/sync.log 2>&1
```

```bash
# Dar permissão de execução
chmod +x sync-cron.sh

# Criar diretório de logs
sudo mkdir -p /var/log/techmesh
sudo chown $USER:$USER /var/log/techmesh
```

### 8.2 Configurar CRON

```bash
# Editar crontab
crontab -e
```

Adicionar:
```cron
# Sincronizar com Unopim a cada 15 minutos
*/15 * * * * /var/www/tech-mesh-sync/sync-cron.sh

# Limpar logs antigos toda semana
0 0 * * 0 find /var/log/techmesh/ -name "*.log" -mtime +30 -delete
```

---

## ✅ PASSO 9: Testes e Validação

### 9.1 Testar Backend

```bash
# Status do serviço
pm2 status

# Logs em tempo real
pm2 logs techmesh-backend --lines 50

# Testar endpoint
curl https://techmesh.seudominio.com/api/topicos | jq
```

### 9.2 Testar Frontend

**Abrir navegador:**
```
https://techmesh.seudominio.com
```

**Checklist:**
- [ ] Página carrega sem erros
- [ ] Estrelas visíveis no fundo
- [ ] 8 tópicos flutuantes aparecem
- [ ] Busca funciona
- [ ] Badges são clicáveis
- [ ] Lightboxes abrem
- [ ] SSL ativo (cadeado verde)

### 9.3 Verificar Logs

```bash
# Nginx
sudo tail -f /var/log/nginx/techmesh-access.log
sudo tail -f /var/log/nginx/techmesh-error.log

# Backend PM2
pm2 logs techmesh-backend

# MongoDB
sudo journalctl -u mongod -f
```

---

## 🔥 PASSO 10: Firewall e Segurança

### 10.1 Configurar UFW (Firewall)

```bash
# Habilitar firewall
sudo ufw enable

# Permitir SSH (IMPORTANTE!)
sudo ufw allow 22/tcp

# Permitir HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verificar status
sudo ufw status
```

### 10.2 Segurança MongoDB

```bash
# Editar configuração MongoDB
sudo nano /etc/mongod.conf
```

Verificar:
```yaml
net:
  port: 27017
  bindIp: 127.0.0.1  # Apenas local, não expor na internet

security:
  authorization: enabled  # Habilitar autenticação
```

```bash
# Reiniciar MongoDB
sudo systemctl restart mongod
```

### 10.3 Limitar Acesso SSH (Opcional)

```bash
sudo nano /etc/ssh/sshd_config
```

Ajustar:
```
PermitRootLogin no
PasswordAuthentication no  # Apenas chave SSH
```

```bash
sudo systemctl restart sshd
```

---

## 📊 PASSO 11: Monitoramento

### 11.1 PM2 Monit

```bash
# Dashboard em tempo real
pm2 monit
```

### 11.2 Status dos Serviços

```bash
# Script de verificação
nano ~/check-status.sh
```

Adicionar:
```bash
#!/bin/bash
echo "=== TECH MESH SYNC STATUS ==="
echo ""
echo "1. Backend (PM2):"
pm2 status | grep techmesh-backend
echo ""
echo "2. Nginx:"
sudo systemctl status nginx | grep Active
echo ""
echo "3. MongoDB:"
sudo systemctl status mongod | grep Active
echo ""
echo "4. Disk Space:"
df -h / | tail -1
echo ""
echo "5. Memory:"
free -h | grep Mem
echo ""
echo "6. Last Sync:"
tail -5 /var/log/techmesh/sync.log
```

```bash
chmod +x ~/check-status.sh
./check-status.sh
```

---

## 🆘 Troubleshooting Comum

### Problema: Backend não inicia

```bash
# Verificar logs detalhados
pm2 logs techmesh-backend --lines 100

# Verificar porta 8001
sudo lsof -i :8001

# Testar manualmente
cd /var/www/tech-mesh-sync/backend
python3 -m uvicorn server:app --host 0.0.0.0 --port 8001
```

### Problema: Frontend mostra página branca

```bash
# Verificar build
ls -la /var/www/tech-mesh-sync/frontend/build/

# Verificar permissões
sudo chown -R www-data:www-data /var/www/tech-mesh-sync/frontend/build/

# Verificar logs Nginx
sudo tail -50 /var/log/nginx/techmesh-error.log

# Rebuildar
cd /var/www/tech-mesh-sync/frontend
rm -rf build/
npm run build
```

### Problema: Tópicos não aparecem

```bash
# Testar API diretamente
curl http://localhost:8001/api/topicos | jq

# Verificar CORS no backend
# Arquivo: backend/.env
CORS_ORIGINS=https://techmesh.seudominio.com

# Verificar console do navegador (F12)
```

### Problema: MongoDB não conecta

```bash
# Verificar se está rodando
sudo systemctl status mongod

# Ver logs
sudo journalctl -u mongod -n 50

# Testar conexão
mongosh

# Verificar configuração
sudo nano /etc/mongod.conf
```

### Problema: SSL não renova

```bash
# Renovar manualmente
sudo certbot renew

# Verificar timer systemd
sudo systemctl status certbot.timer

# Ver próxima renovação
sudo certbot certificates
```

---

## 📋 Checklist Final

Antes de considerar instalação completa:

- [ ] Backend rodando (PM2)
- [ ] MongoDB ativo e populado
- [ ] Frontend buildado e servido pelo Nginx
- [ ] SSL configurado (HTTPS)
- [ ] Firewall configurado
- [ ] CRON de sincronização ativo
- [ ] Logs sendo gravados
- [ ] Site acessível publicamente
- [ ] Todos os tópicos aparecem
- [ ] Busca funcional
- [ ] Badges clicáveis
- [ ] Lightboxes abrem
- [ ] Sem erros no console

---

## 🔄 Atualizações Futuras

Para atualizar o sistema:

```bash
cd /var/www/tech-mesh-sync

# Pull novo código
git pull origin main

# Backend
cd backend
pip3 install -r requirements.txt
pm2 restart techmesh-backend

# Frontend
cd ../frontend
npm ci
npm run build
sudo systemctl reload nginx
```

---

## 📞 Suporte

**Documentação Adicional:**
- `/app/TECH_MESH_SYNC_PT.md` - Documentação completa em português
- `/app/COMPLETUDE_DOS_DADOS.md` - Explicação de completude
- `/app/CORRECOES_URGENTES_APLICADAS.md` - Últimas correções

**Comandos Úteis:**
```bash
# Ver status completo
pm2 status && sudo systemctl status nginx && sudo systemctl status mongod

# Ver todos os logs
pm2 logs --lines 100

# Reiniciar tudo
pm2 restart all && sudo systemctl reload nginx
```

---

**Fim do Guia de Instalação**

Desenvolvido por: E1 Agent (Emergent Labs)
Última Atualização: 2025-01-19
Versão do Guia: 1.0
