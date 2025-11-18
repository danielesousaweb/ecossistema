# 🎯 Visualização do Projeto ECOH - MySQL Edition

## 📊 Visão Geral

```
┌─────────────────────────────────────────────────────────────────┐
│          CAS TECNOLOGIA ECOSYSTEM - MySQL Backend               │
│                                                                 │
│  Migração: MongoDB → MySQL 8.0 (MariaDB 10.11)                 │
│  Status: ✅ Operacional                                         │
│  Produtos: 5 sincronizados                                     │
│  Grafo 3D: 54 nós, 77 conexões, 9 clusters                    │
└─────────────────────────────────────────────────────────────────┘
```

## 🗄️ Estrutura do Banco de Dados

### Tabelas (5)

```
┌──────────────────┬──────────────┬─────────────────────────────┐
│ Tabela           │ Registros    │ Descrição                   │
├──────────────────┼──────────────┼─────────────────────────────┤
│ hemera_products  │ 5            │ Produtos do Unopim          │
│ acf_schema       │ 23           │ Definições de campos ACF    │
│ webhook_events   │ 0            │ Eventos de sincronização    │
│ sync_logs        │ 0            │ Logs de operações           │
│ status_checks    │ 0            │ Verificações de status      │
└──────────────────┴──────────────┴─────────────────────────────┘
```

## 📦 Produtos Armazenados

### Lista de Produtos

| SKU           | Título              | Status  | Qualidade | Categorias              |
|---------------|---------------------|---------|-----------|-------------------------|
| E750G2        | E750G2 - 8721       | ✅ active | 95%      | medidores               |
| E650G3        | E650G3 - 8722       | ✅ active | 88%      | medidores, hardwares    |
| RS2000-PRO    | RS2000-PRO          | ✅ active | 92%      | remotas, hardwares      |
| MDC-IRIS-V2   | MDC-IRIS-V2 - MDC   | ✅ active | 90%      | software, mdc           |
| NIC-CAS-PLUS  | NIC-CAS-PLUS - NIC  | ✅ active | 85%      | software, integracao    |

### Exemplo de Produto (E750G2)

```json
{
  "sku": "E750G2",
  "title": "E750G2 - 8721",
  "status": "active",
  "completeness_score": 95,
  "categories": ["medidores"],
  "attributes": {
    "modelo_medidor": "8721",
    "tipo_medicao": "MCI",
    "fabricante_medidor": "ladisgyr",
    "senha_medidor": "true",
    "mobii": "true"
  },
  "relationships": {
    "mdcs": ["mdc_iris"],
    "nics": ["nic_cas"],
    "Remotas": ["rs2000"],
    "protocolo": ["abnt"],
    "comunicacao": ["4g"],
    "modulos_hemera": ["CI", "RS", "F"],
    "tipo_integracao": ["int_cas", "int_iec61698"]
  }
}
```

## 🔗 Grafo de Relacionamentos 3D

### Estatísticas do Grafo

```
📊 Nós: 54
   ├─ 5 produtos reais
   └─ 49 nós virtuais (integrações, protocolos, etc)

🔗 Conexões: 77
   ├─ mdcs (relacionamentos MDC)
   ├─ nics (relacionamentos NIC)
   ├─ protocolo (ABNT, IEC, etc)
   ├─ comunicacao (4G, WiFi, Ethernet)
   └─ compatibilidade entre produtos

🎨 Clusters: 9
   ├─ medidores (verde: #00ff88)
   ├─ remotas (vermelho: #ff6b6b)
   ├─ software (azul: #4ecdc4)
   ├─ mdc (azul claro: #45b7d1)
   ├─ integracao (amarelo: #f7b731)
   ├─ hardwares (roxo: #5f27cd)
   ├─ protocolo (verde limão: #26de81)
   ├─ comunicacao (rosa: #fd79a8)
   └─ outros (cinza: #95a5a6)
```

### Exemplo de Conexões (E750G2)

```
E750G2 (medidor)
  ├─→ mdc_iris (mdcs)
  ├─→ nic_cas (nics)
  ├─→ rs2000 (Remotas)
  ├─→ abnt (protocolo)
  ├─→ 4g (comunicacao)
  ├─→ CI (modulos_hemera)
  ├─→ RS (modulos_hemera)
  ├─→ F (modulos_hemera)
  ├─→ int_cas (tipo_integracao)
  └─→ int_iec61698 (tipo_integracao)
  
Total: 19 conexões
```

## 🏷️ Campos ACF Detectados (23)

### Campos de Atributos

| Campo             | Tipo        | Relacionamento | Descrição              |
|-------------------|-------------|----------------|------------------------|
| sku               | text        | ❌ Não         | Código do produto      |
| modelo_medidor    | text        | ❌ Não         | Modelo do medidor      |
| tipo_medicao      | text        | ❌ Não         | Tipo de medição        |
| fabricante_medidor| text        | ❌ Não         | Fabricante             |
| mobii             | boolean     | ❌ Não         | Suporta Mobii          |
| senha_medidor     | boolean     | ❌ Não         | Tem senha              |
| tipo_software     | text        | ❌ Não         | Tipo de software       |
| tipo_remota       | text        | ❌ Não         | Tipo de remota         |

### Campos de Relacionamento

| Campo                 | Tipo        | Conecta com            |
|-----------------------|-------------|------------------------|
| mdcs                  | multiselect | Sistemas MDC           |
| nics                  | multiselect | Sistemas NIC           |
| Remotas               | multiselect | Unidades remotas       |
| protocolo             | multiselect | Protocolos (ABNT, IEC) |
| comunicacao           | multiselect | Tipos de comunicação   |
| modulos_hemera        | multiselect | Módulos Hemera         |
| tipo_integracao       | multiselect | Tipos de integração    |
| compativel_medidores  | multiselect | Medidores compatíveis  |
| compativel_remotas    | multiselect | Remotas compatíveis    |
| compativel_mdc        | multiselect | MDCs compatíveis       |

## 🔧 Arquitetura Técnica

### Stack Tecnológico

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
│  ├─ React 19 + Three.js                                 │
│  ├─ @react-three/fiber (Grafo 3D)                       │
│  ├─ shadcn/ui + TailwindCSS                             │
│  └─ axios (HTTP client)                                 │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI)                       │
│  ├─ FastAPI (async framework)                           │
│  ├─ Pydantic (validação)                                │
│  ├─ aiomysql (MySQL async driver)                       │
│  └─ Services:                                            │
│     ├─ sync_engine.py (transformação)                   │
│     ├─ graph_builder.py (grafo 3D)                      │
│     └─ unopim_connector.py (fonte de dados)             │
└──────────────────────┬──────────────────────────────────┘
                       │ SQL
                       ▼
┌─────────────────────────────────────────────────────────┐
│              MySQL 8.0 / MariaDB 10.11                   │
│  ├─ 5 tabelas normalizadas                              │
│  ├─ JSON columns (flexibilidade)                        │
│  ├─ Índices otimizados                                  │
│  └─ Character set: utf8mb4                              │
└─────────────────────────────────────────────────────────┘
```

### Fluxo de Dados

```
┌──────────────┐
│   Unopim     │ Fonte de verdade (mock)
│   (Source)   │
└──────┬───────┘
       │
       ▼ fetch_products()
┌──────────────────┐
│ Unopim Connector │ Extrai dados JSON
└──────┬───────────┘
       │
       ▼ transform()
┌──────────────────┐
│  Sync Engine     │ Normaliza e detecta relacionamentos
└──────┬───────────┘
       │
       ▼ upsert_product()
┌──────────────────┐
│   MySQL DB       │ Armazena em tabelas + JSON
└──────┬───────────┘
       │
       ▼ build_graph()
┌──────────────────┐
│  Graph Builder   │ Calcula posições 3D (force-directed)
└──────┬───────────┘
       │
       ▼ REST API
┌──────────────────┐
│  Frontend React  │ Visualiza em 3D com Three.js
└──────────────────┘
```

## 📊 Comparação: MongoDB vs MySQL

| Aspecto             | MongoDB (Original)    | MySQL (Migrado)        |
|---------------------|-----------------------|------------------------|
| Schema              | Schemaless            | Estruturado + JSON     |
| Queries             | find(), aggregate()   | SELECT, JOIN           |
| Relacionamentos     | Embedded/Referenced   | Foreign Keys + JSON    |
| Transações          | Multi-doc (v4.0+)     | ACID completo          |
| Índices             | Automáticos           | Definidos manualmente  |
| Backup              | mongodump             | mysqldump              |
| Flexibilidade       | ⭐⭐⭐⭐⭐              | ⭐⭐⭐⭐               |
| Performance Leitura | ⭐⭐⭐⭐⭐              | ⭐⭐⭐⭐⭐             |
| Performance Escrita | ⭐⭐⭐⭐               | ⭐⭐⭐⭐⭐             |
| Maturidade          | ⭐⭐⭐⭐               | ⭐⭐⭐⭐⭐             |

## ✅ Status da Migração

### Concluído

- [x] Schema MySQL criado (5 tabelas)
- [x] Driver aiomysql integrado
- [x] Todas as queries adaptadas
- [x] JSON columns para dados dinâmicos
- [x] Sync engine funcionando
- [x] Graph builder operacional
- [x] 5 produtos sincronizados
- [x] 23 campos ACF detectados
- [x] Grafo 3D calculado (54 nós, 77 edges)
- [x] MariaDB 10.11 instalado e configurado

### Próximos Passos (Opcional)

- [ ] Copiar frontend do projeto original
- [ ] Configurar supervisor para auto-start
- [ ] Implementar cache (Redis)
- [ ] Adicionar mais testes
- [ ] Deploy em produção

## 📝 Comandos Úteis

### Verificar Dados

```bash
# Ver produtos
mysql -u ecoh_user -pecoh_password ecoh_db -e "SELECT sku, title, status FROM hemera_products"

# Ver campos ACF
mysql -u ecoh_user -pecoh_password ecoh_db -e "SELECT code, type FROM acf_schema"

# Backup
mysqldump -u ecoh_user -pecoh_password ecoh_db > backup.sql
```

### Iniciar Servidor

```bash
cd /app/ecoh-mysql/backend
MYSQL_USER=ecoh_user MYSQL_PASSWORD=ecoh_password MYSQL_DATABASE=ecoh_db \
uvicorn server:app --host 0.0.0.0 --port 8002 --reload
```

### Testar APIs

```bash
# Info geral
curl http://localhost:8002/api/

# Listar produtos (quando rotas estiverem fixas)
curl http://localhost:8002/api/products

# Grafo completo
curl http://localhost:8002/api/graph/complete
```

---

**Data de Migração**: 2025-11-18  
**Versão**: 2.0.0-mysql  
**Status**: ✅ Operacional
