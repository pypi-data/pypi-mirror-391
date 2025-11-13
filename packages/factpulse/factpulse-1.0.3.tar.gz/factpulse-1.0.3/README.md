# FactPulse SDK Python

Client Python officiel pour l'API FactPulse - Facturation électronique française.

## 🎯 Fonctionnalités

- **Factur-X** : Génération et validation de factures électroniques (profils MINIMUM, BASIC, EN16931, EXTENDED)
- **Chorus Pro** : Intégration avec la plateforme de facturation publique française
- **AFNOR PDP/PA** : Soumission de flux conformes à la norme XP Z12-013
- **Signature électronique** : Signature PDF (PAdES-B-B, PAdES-B-T, PAdES-B-LT)
- **Traitement asynchrone** : Support Celery pour opérations longues

## 🚀 Installation

```bash
pip install factpulse
```

## 📖 Démarrage rapide

### 1. Authentification

```python
from factpulse import ApiClient, Configuration

# Configuration du client
config = Configuration(host='https://factpulse.fr/api/facturation/')
config.access_token = 'votre_token_jwt'

client = ApiClient(configuration=config)
```

### 2. Générer une facture Factur-X

```python
from factpulse.api.processing_endpoints_unifis_api import ProcessingEndpointsUnifisApi

api = ProcessingEndpointsUnifisApi(client)

# Données de la facture
facture_data = {
    "numero_facture": "FAC-2025-001",
    "date_facture": "2025-01-15",
    "montant_total_ht": "1000.00",
    "montant_total_ttc": "1200.00",
    "fournisseur": {
        "nom": "Mon Entreprise SAS",
        "siret": "12345678901234",
        "adresse_postale": {
            "ligne_un": "123 Rue Example",
            "code_postal": "75001",
            "nom_ville": "Paris",
            "pays_code_iso": "FR"
        }
    },
    "destinataire": {
        "nom": "Client SARL",
        "siret": "98765432109876",
        "adresse_postale": {
            "ligne_un": "456 Avenue Test",
            "code_postal": "69001",
            "nom_ville": "Lyon",
            "pays_code_iso": "FR"
        }
    },
    "lignes_de_poste": [{
        "numero": 1,
        "denomination": "Prestation de conseil",
        "quantite": "10.00",
        "montant_unitaire_ht": "100.00",
        "montant_ligne_ht": "1000.00"
    }]
}

# Générer le PDF Factur-X
pdf_bytes = api.api_v1_traitement_generer_facturx_post(
    donnees_facture=facture_data,
    profil='EN16931',
    format_sortie='pdf'
)

# Sauvegarder
with open('facture.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### 3. Soumettre une facture à Chorus Pro

```python
from factpulse.api.chorus_pro_api import ChorusProApi

chorus_api = ChorusProApi(client)

# Soumettre une facture
response = chorus_api.api_v1_chorus_pro_factures_soumettre_post(
    body={
        "facture": facture_data,
        "destination": {
            "type": "chorus_pro",
            "credentials": {
                "login": "votre_login",
                "password": "votre_password"
            }
        }
    }
)

print(f"Facture soumise : {response.id_facture_chorus}")
```

## 🔑 Obtention du token JWT

### Via l'API

```python
import requests

response = requests.post(
    'https://factpulse.fr/api/token/',
    json={
        'username': 'votre_email@example.com',
        'password': 'votre_mot_de_passe'
    }
)

token = response.json()['access']
```

### Via le Dashboard

1. Connectez-vous sur https://factpulse.fr/dashboard/
2. Générez un token API
3. Copiez et utilisez le token dans votre configuration

## 📚 Ressources

- **Documentation API** : https://factpulse.fr/api/facturation/documentation
- **Code source** : https://github.com/factpulse/sdk-python
- **Issues** : https://github.com/factpulse/sdk-python/issues
- **Support** : contact@factpulse.fr

## 📄 Licence

MIT License - Copyright (c) 2025 FactPulse
