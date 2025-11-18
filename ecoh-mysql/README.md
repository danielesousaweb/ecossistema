# CAS Tecnologia Ecosystem - MySQL Edition

🚀 **Sistema de sincronização Unopim → WordPress com backend MySQL 8.0**

## 📋 Migração MongoDB → MySQL

Este projeto é uma migração completa do sistema ECOH original (MongoDB) para MySQL 8.0.

### Principais Mudanças

- ✅ **Motor → aiomysql**: Substituído driver MongoDB por MySQL async
- ✅ **Collections → Tables**: 5 tabelas SQL estruturadas
- ✅ **JSON Columns**: Mantém flexibilidade para dados dinâmicos
- ✅ **Queries SQL**: Todas as operações adaptadas para SQL
- ✅ **100% Compatível**: Frontend não precisa mudar

## 🗄️ Estrutura do Banco

### Tabelas Principais

1. **hemera_products**: Produtos transformados do Unopim
2. **acf_schema**: Definições de campos dinâmicos (ACF)
3. **webhook_events**: Eventos de sincronização
4. **sync_logs**: Logs de operações
5. **status_checks**: Verificações de status

### JSON Columns

- `attributes`: Atributos do produto (JSON)
- `relationships`: Relacionamentos (JSON)
- `categories`: Categorias (JSON Array)
- `graph_node`: Dados do nó 3D (JSON)
- `graph_edges`: Conexões do grafo (JSON Array)

## 🚀 Instalação

### 1. Instalar MySQL 8.0

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server-8.0

# Iniciar serviço
sudo systemctl start mysql
sudo systemctl enable mysql

# Configurar senha root
sudo mysql_secure_installation
```

### 2. Criar Banco de Dados

```bash
mysql -u root -p

CREATE DATABASE ecoh_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ecoh_user'@'localhost' IDENTIFIED BY 'senha_segura';
GRANT ALL PRIVILEGES ON ecoh_db.* TO 'ecoh_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Configurar Ambiente

Edite `/app/ecoh-mysql/backend/.env`:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=ecoh_user
MYSQL_PASSWORD=senha_segura
MYSQL_DATABASE=ecoh_db

CORS_ORIGINS=*
API_PORT=8001
```

### 4. Instalar Dependências

```bash
cd /app/ecoh-mysql/backend
pip install -r requirements.txt
```

### 5. Popular Banco de Dados

```bash
cd /app/ecoh-mysql/backend
python seed_data.py
```

### 6. Iniciar Servidor

```bash
cd /app/ecoh-mysql/backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

## 📡 API Endpoints

### Produtos
- `GET /api/products` - Listar produtos
- `GET /api/products/{sku}` - Detalhes do produto
- `GET /api/products/{sku}/relationships` - Relacionamentos
- `GET /api/products/categories/list` - Categorias

### Grafo 3D
- `GET /api/graph/complete` - Grafo completo
- `GET /api/graph/node/{node_id}` - Detalhes do nó
- `GET /api/graph/clusters` - Clusters
- `WS /api/graph/ws` - WebSocket updates

### Webhooks
- `POST /api/webhooks/unopim` - Webhook Unopim
- `POST /api/webhooks/trigger-sync` - Sincronização manual
- `GET /api/webhooks/sync-status` - Status da sincronização

## 🔧 Configuração de Produção

### Performance

```sql
-- Ajustar parâmetros MySQL
SET GLOBAL max_connections = 200;
SET GLOBAL innodb_buffer_pool_size = 1G;
SET GLOBAL innodb_log_file_size = 256M;
```

### Backups

```bash
# Backup completo
mysqldump -u ecoh_user -p ecoh_db > backup_$(date +%Y%m%d).sql

# Restaurar
mysql -u ecoh_user -p ecoh_db < backup_20250118.sql
```

### Índices

```sql
-- Verificar índices
SHOW INDEX FROM hemera_products;

-- Análise de performance
EXPLAIN SELECT * FROM hemera_products WHERE status = 'active';
```

## 📊 Comparação MongoDB vs MySQL

| Aspecto | MongoDB | MySQL 8.0 |
|---------|---------|-----------|
| Schema | Flexível (schemaless) | Estruturado + JSON |
| Queries | find(), aggregate() | SQL SELECT, JOIN |
| Transactions | Multi-doc (4.0+) | ACID completo |
| Indexes | Automáticos | Definidos manualmente |
| JSON | Nativo | JSON columns (8.0+) |
| Performance | Alta leitura | Alta escrita + leitura |

## 🐛 Troubleshooting

### Erro: "Access denied for user"
```bash
mysql -u root -p
GRANT ALL PRIVILEGES ON ecoh_db.* TO 'ecoh_user'@'localhost';
FLUSH PRIVILEGES;
```

### Erro: "Table doesn't exist"
```bash
cd /app/ecoh-mysql/backend
mysql -u ecoh_user -p ecoh_db < schema.sql
```

### Erro: "Lost connection to MySQL server"
```sql
SET GLOBAL max_allowed_packet=64M;
SET GLOBAL wait_timeout=600;
```

## 📝 Logs

```bash
# Backend logs
tail -f /var/log/supervisor/backend.*.log

# MySQL logs
sudo tail -f /var/log/mysql/error.log

# Query log (desenvolvimento)
SET GLOBAL general_log = 'ON';
tail -f /var/log/mysql/query.log
```

## 🔐 Segurança

### Produção

1. **Mudar senhas padrão**
2. **Usar SSL/TLS** para conexões MySQL
3. **Firewall**: Bloquear porta 3306 externamente
4. **Backup regular** automático
5. **Monitorar logs** de acesso

## 📚 Documentação

- [Documentação Completa](./docs/COMPLETE_SYSTEM_DOCUMENTATION.md)
- [Guia de Instalação](./docs/GUIA_INSTALACAO_SERVIDOR.md)
- [MySQL 8.0 JSON](https://dev.mysql.com/doc/refman/8.0/en/json.html)

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verifique os logs
2. Consulte a documentação
3. Revise as configurações do .env

---

**Versão**: 2.0.0-mysql  
**Migrado de**: MongoDB 4.4 → MySQL 8.0  
**Data**: 2025-01-18
