# 🎨 Instalação do Frontend - ECOH MySQL Edition

## 📋 O que você tem

Frontend React completo com:
- ✅ React 19
- ✅ Three.js (visualização 3D)
- ✅ shadcn/ui components
- ✅ TailwindCSS
- ✅ React Router

---

## 🚀 Instalação no Servidor

### Passo 1: Fazer Upload do Frontend

**Usando FileZilla/WinSCP:**

1. Conectar no servidor
2. Navegar até: `/home/daniele.sousa/`
3. Fazer upload da pasta `frontend` (do seu PC)

**Ou via SCP:**

```bash
# No seu PC, dentro da pasta ecoh-mysql/
scp -r frontend daniele.sousa@[IP_SERVIDOR]:/home/daniele.sousa/
```

---

### Passo 2: Configurar Frontend no Servidor

**2.1. Conectar via SSH:**

```bash
ssh daniele.sousa@[IP_SERVIDOR]
cd /home/daniele.sousa/frontend
```

**2.2. Verificar/Criar arquivo .env:**

```bash
nano .env
```

**Conteúdo:**

```env
# URL do backend (ajustar para seu servidor)
REACT_APP_BACKEND_URL=http://[IP_OU_DOMINIO_SERVIDOR]/api

# Exemplo:
# REACT_APP_BACKEND_URL=http://192.168.1.50/api
# ou
# REACT_APP_BACKEND_URL=https://meudominio.com.br/api
```

**Salvar:** Ctrl+X → Y → Enter

**2.3. Instalar Node.js (se não tiver):**

```bash
# Verificar se Node.js está instalado
node --version

# Se não estiver, instalar:
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# Ou para Ubuntu/Debian:
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**2.4. Instalar Yarn:**

```bash
npm install -g yarn
```

**2.5. Instalar dependências do projeto:**

```bash
cd /home/daniele.sousa/frontend
yarn install
```

⏱️ **Isso vai demorar 3-5 minutos**

**2.6. Build do frontend:**

```bash
yarn build
```

⏱️ **Isso vai demorar 2-3 minutos**

Será criada a pasta `build/` com os arquivos otimizados.

---

### Passo 3: Configurar Apache para Servir o Frontend

**3.1. Editar configuração do Apache:**

```bash
sudo nano /etc/httpd/conf.d/ecoh.conf
```

**3.2. Substituir TODO o conteúdo por:**

```apache
<VirtualHost *:80>
    ServerName [SEU_IP_OU_DOMINIO]
    
    # Logs
    ErrorLog /var/log/httpd/ecoh_error.log
    CustomLog /var/log/httpd/ecoh_access.log combined
    
    # ========================================
    # BACKEND API (FastAPI via WSGI)
    # ========================================
    WSGIDaemonProcess ecoh python-home=/home/daniele.sousa/backend/venv python-path=/home/daniele.sousa/backend
    WSGIProcessGroup ecoh
    WSGIScriptAlias /api /home/daniele.sousa/backend/wsgi.py
    
    <Directory /home/daniele.sousa/backend>
        Require all granted
    </Directory>
    
    # Variáveis de ambiente do backend
    SetEnv MYSQL_HOST [IP_DO_BANCO]
    SetEnv MYSQL_PORT 3306
    SetEnv MYSQL_USER [USUARIO]
    SetEnv MYSQL_PASSWORD [SENHA]
    SetEnv MYSQL_DATABASE [DATABASE]
    
    # ========================================
    # FRONTEND (React Build)
    # ========================================
    DocumentRoot /home/daniele.sousa/frontend/build
    
    <Directory /home/daniele.sousa/frontend/build>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
        
        # React Router - todas as rotas vão para index.html
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </Directory>
    
    # Cache para arquivos estáticos
    <FilesMatch "\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$">
        Header set Cache-Control "max-age=31536000, public"
    </FilesMatch>
</VirtualHost>
```

**3.3. Habilitar mod_rewrite:**

```bash
sudo a2enmod rewrite  # Ubuntu/Debian
# ou já está ativo por padrão no CentOS/RHEL
```

**3.4. Testar configuração:**

```bash
sudo apachectl configtest
```

Deve retornar: **Syntax OK**

**3.5. Reiniciar Apache:**

```bash
sudo systemctl restart httpd
```

---

## ✅ Testar Frontend

**1. Abrir no navegador:**

```
http://[IP_SERVIDOR]/
```

**2. Deve carregar a interface React do ECOH**

**3. Verificar console do navegador (F12):**
- Não deve ter erros de conexão com API
- Requisições para `/api/` devem retornar 200 OK

---

## 🔍 Verificação

**No servidor, criar script de teste:**

```bash
cat > /tmp/check_full.sh << 'EOF'
#!/bin/bash

echo "🔍 Verificando Frontend + Backend..."
echo ""

# Backend
echo "1️⃣ Backend API:"
if curl -s http://localhost/api/ | grep -q "MySQL Edition"; then
    echo "   ✅ API respondendo"
else
    echo "   ❌ API com problema"
fi

# Frontend
echo ""
echo "2️⃣ Frontend React:"
if [ -f /home/daniele.sousa/frontend/build/index.html ]; then
    echo "   ✅ Build existe"
else
    echo "   ❌ Build não encontrado"
fi

if curl -s http://localhost/ | grep -q "root"; then
    echo "   ✅ Frontend servindo"
else
    echo "   ❌ Frontend não carrega"
fi

# Apache
echo ""
echo "3️⃣ Apache:"
if systemctl is-active --quiet httpd; then
    echo "   ✅ Apache rodando"
else
    echo "   ❌ Apache parado"
fi

echo ""
echo "✅ Verificação completa!"
EOF

chmod +x /tmp/check_full.sh
bash /tmp/check_full.sh
```

---

## 🎯 URLs Finais

Após instalação completa:

```
Frontend:       http://[IP_SERVIDOR]/
API Backend:    http://[IP_SERVIDOR]/api/
Produtos:       http://[IP_SERVIDOR]/api/products
Grafo 3D:       http://[IP_SERVIDOR]/api/graph/complete
```

---

## 🆘 Problemas Comuns

### Frontend não carrega (página em branco)

```bash
# Ver logs do Apache
sudo tail -50 /var/log/httpd/ecoh_error.log

# Verificar permissões
ls -la /home/daniele.sousa/frontend/build/

# Corrigir permissões se necessário
sudo chown -R apache:apache /home/daniele.sousa/frontend/build/
```

### Erro: "Failed to fetch" no console

```bash
# Verificar .env do frontend
cat /home/daniele.sousa/frontend/.env

# Deve ter REACT_APP_BACKEND_URL correto

# Rebuild
cd /home/daniele.sousa/frontend
yarn build
sudo systemctl restart httpd
```

### Erro 404 ao navegar no React Router

```bash
# Verificar se mod_rewrite está ativo
sudo apachectl -M | grep rewrite

# Deve mostrar: rewrite_module (shared)

# Verificar configuração do Apache
sudo nano /etc/httpd/conf.d/ecoh.conf
# Confirmar que tem AllowOverride All e RewriteEngine On
```

### Build falha por falta de memória

```bash
# Aumentar memória temporariamente
export NODE_OPTIONS="--max-old-space-size=4096"
yarn build
```

---

## 📦 Atualizar Frontend (após alterações)

```bash
cd /home/daniele.sousa/frontend
yarn build
sudo systemctl reload httpd
```

---

## 🎨 Desenvolvimento Local (opcional)

Para desenvolver localmente e testar no seu PC:

```bash
# No seu PC, dentro da pasta frontend/
yarn install
yarn start

# Abre em http://localhost:3000
# API deve apontar para servidor remoto no .env
```

---

**Frontend instalado com sucesso! 🎉**

Acesse: `http://[SEU_IP]/` para ver a interface 3D funcionando.
