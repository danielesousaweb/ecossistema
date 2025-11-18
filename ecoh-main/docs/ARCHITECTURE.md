# CAS Tecnologia Ecosystem - System Architecture

## Overview

This document provides a complete architectural overview of the Unopim-to-WordPress synchronization system with real-time 3D visualization.

## System Components

```
┌───────────────────┐
│   Unopim Source   │
│   (MySQL/Postgres) │
│   products table   │
│   + JSON values    │
└───────┬───────────┘
        │ SQL/API
        │
        │ Real-time
        │ Webhook
        │
        ↓
┌───────┴──────────────────────────┐
│   Unopim Connector (Python)         │
│   - Reads Unopim DB                 │
│   - Extracts JSON from values col   │
│   - Calculates checksums            │
└────────────┬─────────────────────┘
              │
              ↓
┌────────────┴─────────────────────────────────┐
│   Sync Engine (Python)                            │
│   - Normalizes JSON structure                     │
│   - Detects relationships (comma-separated, etc)  │
│   - Auto-creates ACF field definitions            │
│   - Handles discontinued products                 │
│   - Validates schema changes                      │
└──────────────────┬─────────────────────────────┘
                    │
                    ↓
┌───────────────────┴──────────────────────────┐
│   MongoDB (WordPress-compatible storage)          │
│   Collections:                                    │
│   - hemera_products (transformed data)            │
│   - acf_schema (dynamic field definitions)        │
│   - sync_logs (audit trail)                       │
│   - webhook_events (change history)               │
└───────────────────┬──────────────────────────┘
                    │
                    ↓
┌───────────────────┴──────────────────────────┐
│   Graph Builder (Python)                          │
│   - Force-directed 3D layout algorithm            │
│   - Identifies clusters by type                   │
│   - Creates virtual nodes for references          │
│   - Builds nodes + edges structure                │
└───────────────────┬──────────────────────────┘
                    │
                    ↓
┌───────────────────┴──────────────────────────┐
│   FastAPI REST API (WordPress-compatible)         │
│   Endpoints:                                      │
│   - /api/products (CRUD operations)               │
│   - /api/graph/complete (3D data)                 │
│   - /api/webhooks/unopim (real-time sync)         │
│   - WebSocket /api/graph/ws (live updates)        │
└───────────────────┬──────────────────────────┘
                    │ HTTP/WebSocket
                    │
                    ↓
┌───────────────────┴──────────────────────────┐
│   React Frontend (Three.js Visualization)         │
│   Components:                                     │
│   - EcosystemGraph (3D neural network style)      │
│   - ProductList (catalog view)                    │
│   - Real-time updates via WebSocket               │
│   - Interactive node exploration                  │
└───────────────────────────────────────────────┘
```

## Data Flow

### 1. Initial Sync Flow

```
Unopim DB
    ↓
    ↓ SELECT * FROM products
    ↓
[Connector] Extract JSON from "values" column
    ↓
    ↓ Raw product data
    ↓
[Sync Engine]
    │
    ├───> Parse JSON structure
    │
    ├───> Identify relationships
    │     (comma-separated, arrays, "compativel_" prefix)
    │
    ├───> Calculate checksum (MD5 of JSON)
    │
    ├───> Detect new fields (schema evolution)
    │
    ├───> Create ACF field definitions
    │
    └───> Transform to WordPress structure
    ↓
    ↓ Normalized product data
    ↓
[MongoDB] Store in hemera_products collection
    ↓
[Graph Builder]
    │
    ├───> Create nodes for products
    │
    ├───> Create virtual nodes for relationships
    │
    ├───> Build edges from relationships
    │
    ├───> Run force-directed layout (3D positions)
    │
    └───> Identify clusters
    ↓
    ↓ Complete graph data
    ↓
[API] Expose via /api/graph/complete
    ↓
[Frontend] Render with Three.js
```

### 2. Real-time Webhook Flow

```
Unopim Change Event (Product Updated)
    ↓
    ↓ POST /api/webhooks/unopim
    ↓ {
    ↓   "event_type": "update",
    ↓   "entity_type": "product",
    ↓   "entity_id": 123,
    ↓   "data": {...product...},
    ↓   "checksum": "abc123..."
    ↓ }
    ↓
[Webhook Handler]
    │
    ├───> Compare checksum with stored version
    │
    ├───> If different: trigger re-sync
    │
    ├───> Update MongoDB
    │
    ├───> Rebuild affected graph nodes/edges
    │
    └───> Broadcast to WebSocket clients
    ↓
[WebSocket] Notify connected frontends
    ↓
[Frontend] Update 3D visualization in real-time
```

### 3. Discontinued Product Handling

```
Unopim Product Deleted/Removed
    ↓
[Webhook] event_type: "delete"
    ↓
[Sync Engine]
    │
    ├───> Find product in MongoDB
    │
    ├───> Set status: "discontinued"
    │
    ├───> DO NOT DELETE (preserve history)
    │
    └───> Log event in audit trail
    ↓
[Graph Builder] Exclude discontinued from active graph
    ↓
[Frontend] Node fades out / marked inactive
```

## Dynamic Schema Handling

### Field Type Detection

The system automatically infers field types from values:

```python
# Detection Rules:
"true" / "false"  →  boolean
"value1,value2"  →  multiselect (relationship)
["arr", "ay"]    →  multiselect
Integer/Float     →  number
String            →  text

# Relationship Detection:
1. Field name in known list (mdcs, nics, Remotas, etc.)
2. Comma-separated string
3. Array value
4. Field name starts with "compativel_"
```

### Schema Evolution Process

```
1. New product arrives with unknown field "novo_campo"
   ↓
2. Sync Engine detects field not in acf_schema collection
   ↓
3. Infer type from value
   ↓
4. Create ACF field definition:
   {
     "code": "novo_campo",
     "type": "text",
     "is_relationship": false,
     "detected_at": "2025-01-01T00:00:00Z"
   }
   ↓
5. Store in acf_schema collection
   ↓
6. Field now available for all future products
   ↓
7. If relationship-type: automatically added to graph
```

## MongoDB Schema

### hemera_products Collection

```json
{
  "unopim_id": 123,
  "sku": "E750G2",
  "status": "active",
  "product_type": "simple",
  "title": "E750G2 - 8721",
  "attributes": {
    "fabricante_medidor": "ladisgyr",
    "modelo_medidor": "8721",
    "senha_medidor": "true"
  },
  "relationships": {
    "mdcs": ["mdc_iris"],
    "nics": ["nic_cas"],
    "Remotas": ["rs2000"],
    "protocolo": ["abnt"],
    "comunicacao": ["4g"]
  },
  "categories": ["medidores"],
  "checksum": "abc123def456",
  "completeness_score": 95,
  "created_at": "2025-11-05T22:59:58Z",
  "updated_at": "2025-11-05T23:18:58Z",
  "synced_at": "2025-11-18T18:00:00Z",
  "graph_node": {
    "id": "E750G2",
    "label": "E750G2",
    "type": "medidores",
    "x": 10.5,
    "y": 5.2,
    "z": -3.1,
    "size": 1.4,
    "color": "#00ff88",
    "metadata": {}
  },
  "graph_edges": [
    {
      "source": "E750G2",
      "target": "mdc_iris",
      "relationship_type": "mdcs",
      "strength": 1.0
    }
  ]
}
```

### acf_schema Collection

```json
{
  "code": "protocolo",
  "type": "multiselect",
  "is_relationship": true,
  "detected_at": "2025-11-18T17:59:51Z"
}
```

### sync_logs Collection

```json
{
  "started_at": "2025-11-18T18:00:00Z",
  "completed_at": "2025-11-18T18:00:15Z",
  "duration_seconds": 15,
  "status": "completed",
  "results": {
    "synced": 5,
    "unchanged": 0,
    "errors": 0,
    "new_fields": {}
  }
}
```

## Performance Optimization

### Checksum-based Change Detection

- MD5 hash of entire JSON `values` column
- Skip processing if checksum matches
- Reduces unnecessary database writes
- Enables efficient incremental sync

### Graph Layout Caching

- Force-directed layout is computationally expensive
- Store calculated (x, y, z) positions in database
- Recalculate only when:
  - New nodes added
  - Nodes removed
  - Relationships changed
  - Manual refresh triggered

### MongoDB Indexing

```javascript
// Required indexes
db.hemera_products.createIndex({ "unopim_id": 1 }, { unique: true })
db.hemera_products.createIndex({ "sku": 1 }, { unique: true })
db.hemera_products.createIndex({ "status": 1 })
db.hemera_products.createIndex({ "categories": 1 })
db.hemera_products.createIndex({ "checksum": 1 })

db.acf_schema.createIndex({ "code": 1 }, { unique: true })
```

## Security Considerations

### Webhook Authentication

For production deployment to real Unopim:

```python
# Add to /api/webhooks/unopim endpoint
@router.post("/unopim")
async def unopim_webhook(event: SyncEvent, request: Request):
    # Verify signature
    signature = request.headers.get('X-Unopim-Signature')
    secret = os.environ['UNOPIM_WEBHOOK_SECRET']
    
    expected_signature = hmac.new(
        secret.encode(),
        await request.body(),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Process webhook...
```

### JSON Injection Prevention

- All dynamic fields sanitized before MongoDB insert
- Field names validated (alphanumeric + underscore only)
- Nested objects limited to 3 levels depth
- Maximum field name length: 50 characters

```python
def sanitize_field_name(field_name: str) -> str:
    # Remove invalid characters
    clean = re.sub(r'[^a-zA-Z0-9_]', '', field_name)
    # Limit length
    return clean[:50]
```

## Scalability

### Handling Large Product Catalogs

**Current Implementation (< 1000 products)**
- In-memory force-directed layout
- Full graph rebuild on changes

**For 1000-10000 products**
- Incremental graph updates
- Cluster-based rendering
- LOD (Level of Detail) for distant nodes

**For 10000+ products**
- Partition graph by category
- Load clusters on-demand
- Server-side layout calculation
- WebGL optimization

### Database Sharding

For massive catalogs:

```
MongoDB Sharded Cluster:
- Shard key: "categories"
- Each category on separate shard
- Parallel processing of updates
```

## Deployment Architecture

### Current (Development)

```
Docker Container
    ├── FastAPI (port 8001)
    ├── React (port 3000)
    └── MongoDB (localhost:27017)
```

### Production Recommendation

```
Kubernetes Cluster
    │
    ├── Ingress (SSL termination)
    │
    ├── Backend Pod (3 replicas)
    │   └── FastAPI + Gunicorn
    │
    ├── Frontend Pod (2 replicas)
    │   └── Nginx serving React build
    │
    ├── MongoDB StatefulSet
    │   └── Replica set (3 nodes)
    │
    └── Redis (WebSocket session store)
```

## Next Steps for Production

1. **Connect to Real Unopim Database**
   - Update `UNOPIM_DB_*` environment variables
   - Test connection with real schema
   - Validate field mappings

2. **Configure Webhook URL in Unopim**
   - Set webhook endpoint: `https://yourdomain.com/api/webhooks/unopim`
   - Add authentication secret
   - Test with sample events

3. **Performance Tuning**
   - Add MongoDB indexes
   - Configure connection pooling
   - Enable query caching

4. **Monitoring**
   - Add Prometheus metrics
   - Set up Grafana dashboards
   - Configure alerts for sync failures

5. **Backup Strategy**
   - Automated MongoDB backups
   - Point-in-time recovery
   - Sync log retention policy