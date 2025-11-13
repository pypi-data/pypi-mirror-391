# FactPulse SDK Python

Client Python officiel pour l'API FactPulse - Facturation électronique française.

## 🚀 Installation

```bash
pip install factpulse
```

## 📖 Quickstart

### Authentification

```python
from factpulse import ApiClient, Configuration

# Configuration
config = Configuration(host='https://api.factpulse.fr')
config.access_token = 'votre_token_jwt'

# Créer le client API
client = ApiClient(configuration=config)
```

### Générer une facture Factur-X

```python
from factpulse.api.traitement_facture_api import TraitementFactureApi
from factpulse.models.facture_factur_x import FactureFacturX

api = TraitementFactureApi(client)

# Préparer les données de facture
facture = {
    "numero_facture": "FAC-2025-001",
    "date_emission": "2025-01-15",
    "montant_total_ht": 1000.00,
    "montant_total_ttc": 1200.00,
    "fournisseur": {
        "nom": "Mon Entreprise",
        "siret": "12345678901234",
        "adresse": "123 Rue Example, 75001 Paris"
    },
    "client": {
        "nom": "Client SARL",
        "siret": "98765432109876",
        "adresse": "456 Avenue Test, 69001 Lyon"
    }
}

# Générer la facture Factur-X
response = api.api_v1_traitement_generer_facturx_post(
    body=facture,
    profil='EN16931',
    format='pdf'
)

# Sauvegarder le PDF
with open('facture.pdf', 'wb') as f:
    f.write(response)
```

### Soumettre une facture AFNOR PDP

```python
from factpulse.api.afnor_pdppa_flow_service_api import AFNORPDPPAFlowServiceApi

afnor_api = AFNORPDPPAFlowServiceApi(client)

# Soumettre un flux
response = afnor_api.api_v1_afnor_flow_v1_flows_post(
    body={
        "name": "Facture FAC-2025-001",
        "flow_syntax": "CII",
        "flow_profile": "EN16931",
        "flow_content_base64": "...",  # Contenu XML en base64
        "pdp_credentials": {
            "flow_service_url": "https://pdp.example.fr/flow/v1",
            "token_url": "https://auth.example.fr/oauth/token",
            "client_id": "your_client_id",
            "client_secret": "your_client_secret"
        }
    }
)

print(f"✅ Flux soumis : {response.flow_id}")
```

### Rechercher une entreprise avec Chorus Pro

```python
from factpulse.api.chorus_pro_api import ChorusProApi

chorus_api = ChorusProApi(client)

# Rechercher une entreprise
response = chorus_api.api_v1_chorus_pro_recherche_entreprise_post(
    body={
        "identifiant_structure": "12345678901234",
        "type_identifiant_structure": "SIRET"
    }
)

print(f"Entreprise trouvée : {response.nom}")
```

## 📚 Documentation complète

- **API Reference** : https://docs.factpulse.fr/sdk/python
- **Exemples** : https://github.com/factpulse/sdk-python/tree/main/examples
- **Guide Factur-X** : https://docs.factpulse.fr/facturx
- **Guide AFNOR PDP** : https://docs.factpulse.fr/afnor

## 🔑 Obtenir un token JWT

### Via API (automatisation)

```python
import requests

response = requests.post(
    'https://www.factpulse.fr/api/token/',
    json={
        'username': 'votre_email@example.com',
        'password': 'votre_mot_de_passe'
    }
)

access_token = response.json()['access']
```

### Via Dashboard (interface web)

1. Connectez-vous sur https://www.factpulse.fr/dashboard/
2. Cliquez sur "Generate Test Token" ou "Generate Production Token"
3. Copiez le token généré

## 🛠️ Configuration avancée

### Timeout personnalisé

```python
config = Configuration(host='https://api.factpulse.fr')
config.access_token = 'votre_token'

# Timeout de 60 secondes
client = ApiClient(configuration=config)
client.rest_client.pool_manager.connection_pool_kw['timeout'] = 60
```

### Proxy HTTP

```python
config = Configuration(host='https://api.factpulse.fr')
config.proxy = 'http://proxy.example.com:8080'
```

### Mode debug

```python
import logging

# Activer les logs debug
logging.basicConfig(level=logging.DEBUG)
```

## 🧪 Tests

```bash
# Installer les dépendances de test
pip install -e ".[test]"

# Lancer les tests
pytest tests/
```

## 📄 License

MIT License - voir [LICENSE](LICENSE)

## 🆘 Support

- **Documentation** : https://docs.factpulse.fr
- **Issues** : https://github.com/factpulse/sdk-python/issues
- **Discord** : https://discord.gg/factpulse
- **Email** : support@factpulse.fr
