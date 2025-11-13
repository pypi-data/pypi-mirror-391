# Zephyr Admin UI Component Example

This document provides a complete example of a dashboard component implementation using Zephyrix.

## Dashboard Component

### 1. Component Implementation

```typescript
// src/components/dashboard/Dashboard.tsx
import { Component, signal } from '@zephyrix/core';
import { 
  Layout, 
  Grid, 
  Card, 
  Chart 
} from '@zephyrix/ui';
import { useMetrics } from '../../hooks/useMetrics';
import { useServices } from '../../hooks/useServices';
import { useAlerts } from '../../hooks/useAlerts';

export class Dashboard extends Component {
  // Real-time metrics using signals
  metrics = signal({
    cpu: 0,
    memory: 0,
    requests: 0
  });

  // Service status
  services = signal([]);

  // System alerts
  alerts = signal([]);

  onMount() {
    // Initialize real-time data streams
    this.initializeMetrics();
    this.initializeServices();
    this.initializeAlerts();
  }

  async initializeMetrics() {
    const socket = useMetrics();
    socket.on('metrics.update', (data) => {
      this.metrics.set(data);
    });
  }

  async initializeServices() {
    const { services, subscribe } = useServices();
    this.services.set(services);
    subscribe((updates) => {
      this.services.update(updates);
    });
  }

  async initializeAlerts() {
    const { alerts, subscribe } = useAlerts();
    this.alerts.set(alerts);
    subscribe((newAlert) => {
      this.alerts.update([newAlert, ...this.alerts()]);
    });
  }

  render() {
    return (
      <Layout type="admin">
        <Grid columns={12} gap={2}>
          {/* System Metrics */}
          <Grid.Item span={8}>
            <Card title="System Metrics">
              <Chart
                data={this.metrics()}
                type="real-time"
                options={{
                  animations: true,
                  responsive: true
                }}
              />
            </Card>
          </Grid.Item>

          {/* Alerts Panel */}
          <Grid.Item span={4}>
            <Card title="System Alerts">
              <AlertsList 
                alerts={this.alerts()} 
                maxItems={5}
              />
            </Card>
          </Grid.Item>

          {/* Services Status */}
          <Grid.Item span={12}>
            <Card title="Services">
              <ServiceGrid 
                services={this.services()}
                onAction={this.handleServiceAction}
              />
            </Card>
          </Grid.Item>
        </Grid>
      </Layout>
    );
  }

  handleServiceAction = async (serviceId: string, action: string) => {
    try {
      await api.services.executeAction(serviceId, action);
      // Service status will be updated via WebSocket
    } catch (error) {
      this.showError('Failed to execute service action');
    }
  };
}
```

### 2. Supporting Components

```typescript
// src/components/dashboard/AlertsList.tsx
export class AlertsList extends Component {
  static props = {
    alerts: Array,
    maxItems: Number
  };

  render() {
    const alerts = this.props.alerts
      .slice(0, this.props.maxItems);

    return (
      <List>
        {alerts.map(alert => (
          <ListItem key={alert.id}>
            <AlertIcon type={alert.severity} />
            <Text>{alert.message}</Text>
            <TimeAgo date={alert.timestamp} />
          </ListItem>
        ))}
      </List>
    );
  }
}

// src/components/dashboard/ServiceGrid.tsx
export class ServiceGrid extends Component {
  static props = {
    services: Array,
    onAction: Function
  };

  render() {
    return (
      <DataGrid
        data={this.props.services}
        columns={[
          {
            field: 'name',
            header: 'Service Name',
            sortable: true
          },
          {
            field: 'status',
            header: 'Status',
            renderer: (status) => (
              <StatusBadge status={status} />
            )
          },
          {
            field: 'actions',
            header: 'Actions',
            renderer: (_, service) => (
              <ActionButtons
                service={service}
                onAction={this.props.onAction}
              />
            )
          }
        ]}
        features={{
          sorting: true,
          filtering: true,
          pagination: true
        }}
      />
    );
  }
}
```

### 3. Hooks Implementation

```typescript
// src/hooks/useMetrics.ts
export function useMetrics() {
  return createSocket({
    endpoint: '/metrics',
    options: {
      reconnect: true,
      reconnectInterval: 1000
    }
  });
}

// src/hooks/useServices.ts
export function useServices() {
  const store = servicesStore();
  
  async function loadServices() {
    const services = await api.services.list();
    store.set(services);
  }

  function subscribe(callback) {
    return store.subscribe(callback);
  }

  onMount(() => {
    loadServices();
  });

  return {
    services: store.value,
    subscribe
  };
}

// src/hooks/useAlerts.ts
export function useAlerts() {
  const store = alertsStore();
  const socket = createSocket({ endpoint: '/alerts' });

  socket.on('alert.new', (alert) => {
    store.update([alert, ...store.value]);
  });

  return {
    alerts: store.value,
    subscribe: store.subscribe
  };
}
```

### 4. API Integration

```typescript
// src/api/services.ts
export const servicesApi = {
  async list() {
    return api.get('/services');
  },

  async executeAction(serviceId: string, action: string) {
    return api.post(`/services/${serviceId}/actions`, {
      action
    });
  },

  async getMetrics(serviceId: string) {
    return api.get(`/services/${serviceId}/metrics`);
  }
};

// src/api/metrics.ts
export const metricsApi = {
  async getCurrent() {
    return api.get('/metrics/current');
  },

  async getHistory(params) {
    return api.get('/metrics/history', { params });
  }
};
```

### 5. Usage Example

```typescript
// src/pages/admin/index.tsx
import { Dashboard } from '../../components/dashboard/Dashboard';

export default function AdminPage() {
  return (
    <AdminLayout>
      <Dashboard />
    </AdminLayout>
  );
}
```

## Integration with Zephyr Backend

The dashboard components integrate with Zephyr's backend through:

1. REST API endpoints
2. WebSocket connections for real-time updates
3. GraphQL queries for complex data requirements

### Backend Routes

```python
# zephyr/admin/routes.py
@admin_route
class AdminAPI:
    @get("/metrics/current")
    async def get_current_metrics(self):
        return await self.metrics_service.get_current()

    @get("/services")
    async def list_services(self):
        return await self.service_manager.list_all()

    @post("/services/{service_id}/actions")
    async def execute_service_action(
        self, 
        service_id: str, 
        action: ServiceAction
    ):
        return await self.service_manager.execute_action(
            service_id, 
            action
        )
```

This example demonstrates:
1. Real-time data handling
2. Responsive UI updates
3. Backend integration
4. Error handling
5. Performance optimization
