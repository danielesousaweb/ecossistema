# Implementation Guide

## Quick Start

### 1. Database Seeding (Development)

```bash
cd /app/backend
python seed_data.py
```

This will:
- Clear existing data
- Load 5 mock products from Unopim connector
- Transform and store in MongoDB
- Build initial 3D graph structure
- Create dynamic ACF field definitions

### 2. Access the Application

- **3D Ecosystem Graph**: http://localhost:3000/
- **Product List**: http://localhost:3000/products
- **API Documentation**: http://localhost:8001/api/

### 3. API Endpoints

#### Products

**Get All Products**
```bash
curl http://localhost:8001/api/products
```

**Get Single Product**
```bash
curl http://localhost:8001/api/products/E750G2
```

**Get Product Relationships**
```bash
curl http://localhost:8001/api/products/E750G2/relationships
```

**Get Categories**
```bash
curl http://localhost:8001/api/products/categories/list
```

#### Graph

**Get Complete Graph**
```bash
curl http://localhost:8001/api/graph/complete
```

Response:
```json
{
  "success": true,
  "data": {
    "nodes": [
      {
        "id": "E750G2",
        "label": "E750G2",
        "type": "medidores",
        "x": 10.5,
        "y": 5.2,
        "z": -3.1,
        "size": 1.4,
        "color": "#00ff88",
        "metadata": {...}
      }
    ],
    "edges": [
      {
        "source": "E750G2",
        "target": "mdc_iris",
        "relationship_type": "mdcs",
        "strength": 1.0
      }
    ],
    "clusters": [...],
    "stats": {
      "total_nodes": 54,
      "total_edges": 77,
      "total_clusters": 9
    }
  }
}
```

**Get Node Details**
```bash
curl http://localhost:8001/api/graph/node/E750G2
```

#### Webhooks

**Trigger Manual Sync**
```bash
curl -X POST http://localhost:8001/api/webhooks/trigger-sync
```

**Get Sync Status**
```bash
curl http://localhost:8001/api/webhooks/sync-status
```

**Unopim Webhook (Production)**
```bash
curl -X POST http://localhost:8001/api/webhooks/unopim \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "update",
    "entity_type": "product",
    "entity_id": 123,
    "data": {...product data...},
    "timestamp": "2025-01-18T12:00:00Z"
  }'
```

## Connecting to Real Unopim Database

### Step 1: Update Environment Variables

Edit `/app/backend/.env`:

```bash
# Unopim Database Connection
UNOPIM_DB_TYPE=mysql  # or postgresql
UNOPIM_DB_HOST=your-unopim-db-host.com
UNOPIM_DB_PORT=3306
UNOPIM_DB_NAME=unopim_database
UNOPIM_DB_USER=unopim_user
UNOPIM_DB_PASSWORD=your_secure_password
```

### Step 2: Update Unopim Connector

Edit `/app/backend/services/unopim_connector.py`:

```python
import aiomysql  # or asyncpg for PostgreSQL

class UopimConnector:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.pool = None
        
    async def connect(self):
        """Establish database connection pool"""
        if self.db_config['type'] == 'mysql':
            self.pool = await aiomysql.create_pool(
                host=self.db_config['host'],
                port=int(self.db_config['port']),
                user=self.db_config['user'],
                password=self.db_config['password'],
                db=self.db_config['database'],
                maxsize=10
            )
        # For PostgreSQL, use asyncpg
        
    async def fetch_products(self, filters: Optional[Dict] = None):
        """Fetch products from Unopim database"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = """
                    SELECT 
                        id, sku, status, type, parent_id, 
                        attribute_family_id, values, additional,
                        avg_completeness_score, created_at, updated_at
                    FROM products
                    WHERE status = 1
                """
                
                await cursor.execute(query)
                rows = await cursor.fetchall()
                
                products = []
                for row in rows:
                    products.append({
                        'id': row[0],
                        'sku': row[1],
                        'status': row[2],
                        'type': row[3],
                        'parent_id': row[4],
                        'attribute_family_id': row[5],
                        'values': json.loads(row[6]),  # Parse JSON column
                        'additional': json.loads(row[7]) if row[7] else None,
                        'avg_completeness_score': row[8],
                        'created_at': row[9],
                        'updated_at': row[10]
                    })
                
                return products
```

### Step 3: Install Database Drivers

```bash
cd /app/backend

# For MySQL
pip install aiomysql

# For PostgreSQL
pip install asyncpg

# Update requirements
pip freeze > requirements.txt
```

### Step 4: Test Connection

```bash
cd /app/backend
python -c "
import asyncio
from services.unopim_connector import UopimConnector
import os

db_config = {
    'type': os.environ['UNOPIM_DB_TYPE'],
    'host': os.environ['UNOPIM_DB_HOST'],
    'port': os.environ['UNOPIM_DB_PORT'],
    'database': os.environ['UNOPIM_DB_NAME'],
    'user': os.environ['UNOPIM_DB_USER'],
    'password': os.environ['UNOPIM_DB_PASSWORD']
}

async def test():
    connector = UopimConnector(db_config)
    await connector.connect()
    products = await connector.fetch_products()
    print(f'Fetched {len(products)} products')

asyncio.run(test())
"
```

### Step 5: Run Initial Sync

```bash
cd /app/backend
python seed_data.py
```

This will now pull real data from Unopim!

## Setting Up Real-time Webhooks

### In Unopim Admin Panel

1. Navigate to: **Settings > Webhooks > Add New**

2. Configure webhook:
   ```
   Name: WordPress Sync
   URL: https://your-domain.com/api/webhooks/unopim
   Method: POST
   Events:
     - product.created
     - product.updated
     - product.deleted
     - attribute.created
   Secret: <generate-random-secret>
   ```

3. Save and test

### In Your Backend

Update `/app/backend/.env`:
```bash
UNOPIM_WEBHOOK_SECRET=your-generated-secret
```

### Webhook Payload Format

Unopim should send:
```json
{
  "event_type": "update",
  "entity_type": "product",
  "entity_id": 123,
  "data": {
    "id": 123,
    "sku": "E750G2",
    "values": {...},
    "updated_at": "2025-01-18T12:00:00Z"
  },
  "timestamp": "2025-01-18T12:00:01Z",
  "checksum": "abc123..."
}
```

## WordPress ACF Implementation

If you want to migrate this to actual WordPress:

### Step 1: Install Required Plugins

```bash
# In WordPress admin
Plugins > Add New

Install:
- Advanced Custom Fields (ACF) Pro
- Custom Post Type UI
```

### Step 2: Register Custom Post Type

Add to `functions.php` or create plugin:

```php
<?php
function register_hemera_products() {
    register_post_type('hemera_product', array(
        'labels' => array(
            'name' => 'Hemera Products',
            'singular_name' => 'Product'
        ),
        'public' => true,
        'has_archive' => true,
        'show_in_rest' => true,
        'supports' => array('title', 'editor', 'custom-fields'),
        'taxonomies' => array('product_category')
    ));
}
add_action('init', 'register_hemera_products');
```

### Step 3: Register ACF Fields Dynamically

```php
<?php
function create_acf_fields_from_unopim() {
    // Fetch field definitions from MongoDB
    $api_url = 'http://your-backend/api/acf-schema';
    $fields = json_decode(file_get_contents($api_url), true);
    
    $acf_fields = array();
    
    foreach ($fields as $field) {
        $acf_fields[] = array(
            'key' => 'field_' . $field['code'],
            'label' => ucwords(str_replace('_', ' ', $field['code'])),
            'name' => $field['code'],
            'type' => convert_unopim_type_to_acf($field['type']),
            'required' => $field['is_required'] ?? false
        );
    }
    
    acf_add_local_field_group(array(
        'key' => 'group_hemera_products',
        'title' => 'Product Attributes',
        'fields' => $acf_fields,
        'location' => array(
            array(
                array(
                    'param' => 'post_type',
                    'operator' => '==',
                    'value' => 'hemera_product'
                )
            )
        )
    ));
}
add_action('acf/init', 'create_acf_fields_from_unopim');

function convert_unopim_type_to_acf($unopim_type) {
    $map = array(
        'text' => 'text',
        'select' => 'select',
        'multiselect' => 'select',  // with 'multiple' => 1
        'boolean' => 'true_false',
        'number' => 'number'
    );
    return $map[$unopim_type] ?? 'text';
}
```

### Step 4: Sync Products via CRON

```php
<?php
function sync_unopim_products() {
    $api_url = 'http://your-backend/api/products';
    $response = wp_remote_get($api_url);
    $products = json_decode(wp_remote_retrieve_body($response), true);
    
    foreach ($products['data'] as $product) {
        // Check if post exists
        $existing = get_posts(array(
            'post_type' => 'hemera_product',
            'meta_key' => 'unopim_id',
            'meta_value' => $product['unopim_id'],
            'posts_per_page' => 1
        ));
        
        if ($existing) {
            // Update
            $post_id = $existing[0]->ID;
            wp_update_post(array(
                'ID' => $post_id,
                'post_title' => $product['title'],
                'post_status' => $product['status'] === 'active' ? 'publish' : 'draft'
            ));
        } else {
            // Create
            $post_id = wp_insert_post(array(
                'post_type' => 'hemera_product',
                'post_title' => $product['title'],
                'post_status' => $product['status'] === 'active' ? 'publish' : 'draft'
            ));
        }
        
        // Update ACF fields
        foreach ($product['attributes'] as $key => $value) {
            update_field($key, $value, $post_id);
        }
        
        // Update meta
        update_post_meta($post_id, 'unopim_id', $product['unopim_id']);
        update_post_meta($post_id, 'sku', $product['sku']);
    }
}

// Schedule CRON
if (!wp_next_scheduled('sync_unopim_products_cron')) {
    wp_schedule_event(time(), 'hourly', 'sync_unopim_products_cron');
}
add_action('sync_unopim_products_cron', 'sync_unopim_products');
```

## Three.js Visualization Customization

### Changing Node Colors

Edit `/app/frontend/src/components/EcosystemGraph.js`:

```javascript
const color_map = {
  'medidores': '#00ff88',      // Bright green
  'remotas': '#ff6b6b',        // Coral red
  'software': '#4ecdc4',       // Turquoise
  'mdc': '#45b7d1',            // Sky blue
  'integracao': '#f7b731',     // Gold
  'hardwares': '#5f27cd'       // Purple
};
```

### Adjusting Force-Directed Layout

Edit `/app/backend/services/graph_builder.py`:

```python
# Increase repulsion for more spacing
repulsion = 25.0  # default: 15.0

# Decrease attraction for looser connections
attraction = 0.05  # default: 0.1

# More iterations for better layout
iterations = 200  # default: 100
```

### Adding Custom Node Types

In `_create_virtual_node()` method:

```python
if node_id.startswith('custom_prefix_'):
    node_type = 'custom_type'
    color = '#custom_color'
```

## Performance Monitoring

### Backend Metrics

Add Prometheus endpoint:

```python
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response

sync_counter = Counter('sync_operations_total', 'Total sync operations')
sync_duration = Histogram('sync_duration_seconds', 'Sync duration')

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Frontend Performance

Monitor Three.js FPS:

```javascript
import Stats from 'three/examples/jsm/libs/stats.module';

const stats = Stats();
document.body.appendChild(stats.dom);

useFrame(() => {
  stats.update();
});
```

## Troubleshooting

### Issue: Products not syncing

```bash
# Check backend logs
tail -f /var/log/supervisor/backend.out.log

# Check sync status
curl http://localhost:8001/api/webhooks/sync-status

# Manual trigger
curl -X POST http://localhost:8001/api/webhooks/trigger-sync
```

### Issue: Graph not rendering

```bash
# Check frontend console
# Open browser DevTools > Console

# Verify API response
curl http://localhost:8001/api/graph/complete | jq

# Check if nodes have positions
curl http://localhost:8001/api/graph/complete | jq '.data.nodes[0]'
```

### Issue: Webhook not receiving events

```bash
# Test webhook endpoint
curl -X POST http://localhost:8001/api/webhooks/unopim \
  -H "Content-Type: application/json" \
  -d '{"event_type":"test","entity_type":"product","entity_id":1,"data":{},"timestamp":"2025-01-18T12:00:00Z"}'

# Check webhook events log
mongo
use test_database
db.webhook_events.find().sort({processed_at: -1}).limit(10)
```