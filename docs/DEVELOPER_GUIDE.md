# Guide Développeur - Suivre mes Calories

## 🚀 Architecture

### Stack Technique
- **Frontend** : React Native
- **Backend** : Python/Flask
- **Base de données** : PostgreSQL
- **Cache** : Redis
- **Monitoring** : Prometheus
- **CI/CD** : GitHub Actions

### Structure du Projet
```
suivre-mes-calories/
├── backend/
│   ├── api/
│   ├── models/
│   ├── services/
│   ├── tests/
│   └── utils/
├── frontend/
│   ├── components/
│   ├── screens/
│   ├── services/
│   └── utils/
├── docs/
└── tests/
```

## 💻 Installation

### Prérequis
- Python 3.8+
- Node.js 14+
- PostgreSQL 13+
- Redis 6+
- Docker

### Configuration Développement
```bash
# Clone du repo
git clone https://github.com/votre-repo/suivre-mes-calories.git

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sous Windows
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install

# Base de données
docker-compose up -d
```

## 🔧 Configuration

### Variables d'Environnement
```env
# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secret-key
ENV=development

# Frontend
API_URL=http://localhost:5000
```

### Base de Données
```sql
-- Création de la base
CREATE DATABASE nutrition_tracker;

-- Migration
flask db upgrade
```

## 🏗️ Architecture API

### Endpoints Principaux
```yaml
/api/v1:
  /auth:
    /login: POST
    /register: POST
  /meals:
    /: GET, POST
    /{id}: GET, PUT, DELETE
  /users:
    /profile: GET, PUT
    /stats: GET
```

### Modèles de Données
```python
class User:
    id: int
    email: str
    password_hash: str
    profile: UserProfile

class Meal:
    id: int
    user_id: int
    name: str
    calories: float
    date: datetime
```

## 🧪 Tests

### Tests Unitaires
```bash
# Backend
pytest tests/

# Frontend
npm test
```

### Tests d'Intégration
```bash
# API
pytest tests/integration/

# E2E
npm run cypress
```

## 📊 Monitoring

### Métriques
- Temps de réponse API
- Utilisation mémoire/CPU
- Erreurs
- Requêtes/seconde

### Alertes
- Latence > 500ms
- Erreurs > 1%
- CPU > 80%
- Mémoire > 90%

## 🚀 Déploiement

### Production
```bash
# Build
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Staging
```bash
# Deploy to staging
./deploy.sh staging
```

## 📝 Guidelines

### Code Style
- PEP 8 pour Python
- ESLint pour JavaScript
- Tests obligatoires
- Documentation requise

### Git Flow
1. Feature branch
2. Pull Request
3. Code Review
4. Tests CI
5. Merge

## 🔒 Sécurité

### Bonnes Pratiques
- Validation des entrées
- Sanitization des données
- Rate limiting
- CORS configuré

### Auth & Auth
- JWT tokens
- Refresh tokens
- Rôles utilisateurs
- 2FA support

## 🔍 Debugging

### Logs
```python
# Configuration
import logging
logging.basicConfig(level=logging.INFO)

# Usage
logger.info("Action effectuée")
logger.error("Erreur survenue", exc_info=True)
```

### Monitoring
- Prometheus metrics
- Grafana dashboards
- Error tracking
- Performance monitoring

## 📚 Documentation API

### Swagger/OpenAPI
- URL: `/api/docs`
- Format: OpenAPI 3.0
- Authentication: Bearer token

### Exemples
```bash
# Auth
curl -X POST /api/auth/login \
  -d '{"email": "user@example.com", "password": "secret"}'

# Create Meal
curl -X POST /api/meals \
  -H "Authorization: Bearer token" \
  -d '{"name": "Déjeuner", "calories": 500}'
```

## 🔧 Maintenance

### Base de Données
```sql
-- Optimisation
VACUUM ANALYZE;

-- Index
CREATE INDEX idx_meals_user_date ON meals(user_id, date);
```

### Cache
```python
# Invalidation
cache.delete_pattern('user:*')

# Refresh
cache.set_many(new_data, timeout=3600)
```

## 📈 Performance

### Optimisations
- Query optimization
- Cache strategies
- Lazy loading
- Connection pooling

### Benchmarks
```bash
# API Load Test
locust -f tests/load/locustfile.py

# Frontend
lighthouse report
```

## 🤝 Contribution

### Process
1. Fork repository
2. Create feature branch
3. Write tests
4. Update documentation
5. Submit PR

### Standards
- Commit conventions
- Code review process
- Test coverage > 80%
- Documentation à jour
