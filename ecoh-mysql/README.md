# CAS Tecnologia Ecosystem - Direct Unopim Connection

🚀 **Frontend React conectado diretamente às tabelas do Unopim**

## 📋 Versão 3.0.0 - Direct Unopim

Esta versão elimina as tabelas intermediárias e conecta diretamente às tabelas padrão do Unopim:
- `unopim_products`
- `unopim_attributes`
- `unopim_categories`

### ✅ Vantagens
- **Dados sempre atualizados**: Lê diretamente do Unopim
- **Sem sincronização**: Não precisa de processos de sync
- **Menos complexidade**: Sem tabelas intermediárias
- **Manutenção simplificada**: Menos código para manter

## 🗄️ Estrutura do Banco

### Tabelas do Unopim Utilizadas

| Tabela | Uso |
|--------|-----|
| `unopim_products` | Produtos com campo `values` (JSON) |
| `unopim_attributes` | Definições de atributos filtráveis |
| `unopim_categories` | Categorias de produtos |

### Estrutura do Campo `values` (JSON)

```json
{
  "common": {
    "sku": "E750G2",
    "nome_medidor": "E750G2 (COM NIC CAS)",
    "fabricante_medidor": "landis",
    "modelo_medidor": "8721",
    "medidor_senha": "true",
    "protocolo_comunicao": "abnt,dlms",
    "tipo_medicao": "mci",
    "caractersticas_medidor": "registrador,fasorial,memoria_massa"
  },
  "categories": ["medidores"]
}
```

## 🚀 Instalação

### 1. Configurar Conexão com o Banco

Edite o arquivo `/app/ecoh-mysql/backend/.env`:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=seu_usuario
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=unopim

CORS_ORIGINS=*
```

### 2. Instalar Dependências Backend

```bash
cd /app/ecoh-mysql/backend
pip install -r requirements.txt
```

### 3. Instalar Dependências Frontend

```bash
cd /app/ecoh-mysql/frontend
yarn install
```

### 4. Build do Frontend

```bash
cd /app/ecoh-mysql/frontend
yarn build
```

### 5. Iniciar Backend

```bash
cd /app/ecoh-mysql/backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

## 📡 API Endpoints

### Tópicos (Filtros Dinâmicos)
- `GET /api/topicos` - Lista tópicos dinâmicos do Unopim
- `GET /api/topicos/produtos-por-topico?campo=X&valor=Y` - Produtos por tópico
- `GET /api/topicos/busca-global?q=termo` - Busca global

### Produtos
- `GET /api/products` - Listar produtos
- `GET /api/products/{sku}` - Detalhes do produto
- `GET /api/products/{sku}/relationships` - Relacionamentos
- `GET /api/products/categories/list` - Categorias

### Grafo 3D
- `GET /api/graph/complete` - Grafo completo para visualização
- `GET /api/graph/node/{node_id}` - Detalhes do nó

### Status
- `GET /api/health` - Health check
- `GET /api/webhooks/sync-status` - Status da conexão

## 📝 Cadastro de Atributos no Unopim

### Atributos Recomendados (multiselect)

| Código | Label | Tipo |
|--------|-------|------|
| `fabricante_medidor` | Fabricante | select |
| `modelo_medidor` | Modelo | text |
| `nome_medidor` | Nome | text |
| `medidor_senha` | Senha | boolean |
| `protocolo_comunicao` | Protocolos | multiselect |
| `tipo_medicao` | Tipo de Medição | multiselect |
| `nics` | NICs | multiselect |
| `remotas` | Remotas | multiselect |
| `comunicacao` | Mídia Comunicação | multiselect |
| `mdcs` | MDCs | multiselect |
| `tipo_integracao` | Tipo Integração | multiselect |
| `hemera` | Hemera | multiselect |
| `caractersticas_medidor` | Características | multiselect |

### Valores para Campos Multiselect

**Protocolos:** `abnt, modbus, ansi, dlms, ion, iec, pima, irda`

**Tipo de Medição:** `smi, smc, mci, smlc`

**NICs:** `cas, weg`

**Remotas:** `cas, star_measure, zaruc, deshtec`

**Comunicação:** `3g, 4g, nb, ethernet, satelite, wisun, gridstream`

**MDCs:** `iris, sanplat, orca, command_center, ims, sade`

**Tipo Integração:** `cas, cas_appia_json, iec_61698, terceiros`

**Hemera:** `ci, residencial, residencial_smart, fronteira`

**Características:** `registrador, fasorial, memoria_massa, eventos, tarifa_branca, qualidade, gd, parametrizacao, corte_religue, comandos_smc`

## 🎨 Frontend - Alterações Visuais

### Ícones
- Todos os ícones dos tópicos foram substituídos por 🔵 (bola azul)

### Posicionamento das Bolhas (≤ 8 tópicos)
```
pos1: left 10%  top 12%  (canto superior esquerdo)
pos2: left 50%  top 8%   (centro superior)
pos3: left 83%  top 14%  (canto superior direito)
pos4: left 16%  top 52%  (meio esquerdo)
pos5: left 40%  top 68%  (centro inferior esquerdo)
pos6: left 72%  top 62%  (centro inferior direito)
pos7: left 86%  top 46%  (meio direito)
pos8: left 32%  top 86%  (inferior esquerdo)
```

## 📁 Arquivos Modificados

### Backend
- `database.py` - Conexão direta com tabelas Unopim
- `routes/topicos.py` - Tópicos dinâmicos do Unopim
- `routes/products.py` - Produtos do Unopim
- `routes/webhooks.py` - Simplificado (sem sync)
- `services/graph_builder.py` - Grafo do Unopim
- `server.py` - Inicialização atualizada

### Frontend
- `components/FloatingTopicHTML.js` - Ícone 🔵
- `pages/Home.js` - Posições fixas das bolhas

## 🔧 Ativação no Servidor (via mRemoteNG)

1. **Upload dos arquivos via FTP**
2. **Conectar via SSH (mRemoteNG)**
3. **Executar comandos:**

```bash
# Navegar para o diretório
cd /home/daniele.sousa/ecoh-mysql

# Instalar dependências backend
cd backend
pip install -r requirements.txt

# Configurar .env (editar com seus dados)
cp .env.example .env
nano .env

# Build do frontend
cd ../frontend
yarn install
yarn build

# Reiniciar serviços (ajustar conforme seu servidor)
sudo systemctl restart ecoh-backend
# ou
pm2 restart ecoh-backend
```

## 🐛 Troubleshooting

### Erro: "Access denied for user"
Verifique as credenciais no arquivo `.env`

### Erro: "Table 'unopim_products' doesn't exist"
Confirme que o prefixo das tabelas é `unopim_`

### Tópicos não aparecem
Verifique se há produtos com `status = 1` no Unopim

### Logs de Debug
Os logs indicam a fonte dos dados:
```
[SOURCE: unopim_products] Found 10 products
[SOURCE: unopim_attributes] Found 15 filterable attributes
```

---

**Versão**: 3.0.0-direct  
**Conexão**: Direta com tabelas Unopim  
**Data**: 2025-01
