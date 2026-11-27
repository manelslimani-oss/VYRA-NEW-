# VYRA — information VIH, chatbot sans API

Version du projet avec VYRA fonctionnant entièrement en local, sans Gemini, sans clé API et sans appel à un service d'intelligence artificielle externe.

## Lancer en local

```bash
python -m pip install -r requirements.txt
python app.py
```

Ouvrir ensuite http://127.0.0.1:5000.

## Déploiement

Le projet conserve le lancement Gunicorn prévu pour l'hébergement :

```bash
gunicorn app:app
```

Aucune variable `GEMINI_API_KEY`, aucun secret et aucun compte Google AI Studio ne sont nécessaires. Le chatbot répond à partir de règles et d'une base de réponses intégrée au serveur.

## Fonctionnement et limites

- Réponses en français, anglais et arabe selon la langue détectée.
- Salutations, questions fréquentes sur la transmission, les situations sans risque, les symptômes, le dépistage, la PrEP, la PPE/TPE, les traitements, la grossesse et la différence entre VIH et sida.
- Les questions non reconnues reçoivent une réponse prudente plutôt qu'une information médicale inventée.
- Ce chatbot n'est pas une IA générative : il sélectionne des réponses préparées. Il ne pose aucun diagnostic et ne remplace pas un professionnel de santé.
- En cas d'exposition possible dans les 72 dernières heures, il recommande une évaluation médicale urgente pour la PPE/TPE.
