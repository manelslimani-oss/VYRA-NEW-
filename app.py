
from flask import Flask, request, jsonify, send_from_directory
import os
import re
import unicodedata

app = Flask(__name__)

# ==========================================================
# 1. REPONSES PRINCIPALES : FRANCAIS, ANGLAIS ET ARABE
# ==========================================================

REPONSES = {
    "fr": {
        "bonjour": "Bonjour ! 😊 Je suis VYRA, ton assistant d’information sur le VIH. Je suis là pour répondre à tes questions avec bienveillance et sans jugement. Que souhaites-tu savoir sur le VIH ?",
        "merci": "Avec plaisir ! ❤️ N’hésite pas à poser d’autres questions.",
        "femme": "Être une femme ne signifie absolument pas être porteuse du VIH. Le VIH ne dépend pas du sexe ou du genre. Seul un test permet de connaître son statut.",
        "transmission": "Le VIH peut se transmettre lors de certaines expositions au sang, au sperme, aux sécrétions vaginales ou rectales et au lait maternel. Les principales situations sont certains rapports sexuels sans protection adaptée, le partage de matériel d’injection contaminé et la transmission de la mère à l’enfant sans prévention adaptée.",
        "non_transmission": "Le VIH ne se transmet pas par les câlins, les poignées de main, les baisers sociaux, le partage de vaisselle ou de repas, les toilettes, les piscines, la sueur, les larmes ou les moustiques.",
        "baiser": "Le VIH ne se transmet pas par un baiser ordinaire ou la salive.",
        "symptomes": "Certaines personnes peuvent avoir des symptômes ressemblant à ceux de la grippe quelques semaines après l’infection, tandis que d’autres n’ont aucun symptôme. Seul un dépistage permet de connaître son statut.",
        "depistage": "Le dépistage est le seul moyen de connaître son statut VIH. Les délais de détection varient selon les tests. Un centre de dépistage ou un professionnel de santé pourra conseiller le test adapté.",
        "urgence": "⚠️ Si une exposition possible au VIH a eu lieu au cours des dernières 72 heures, consulte immédiatement un service d’urgence ou un professionnel de santé pour évaluer la nécessité d’un traitement post-exposition (TPE/PPE). Il doit être commencé le plus tôt possible et au plus tard dans les 72 heures.",
        "prep": "La PrEP est un traitement préventif destiné aux personnes séronégatives qui peuvent être exposées au VIH. Elle doit être prescrite et suivie par un professionnel de santé.",
        "traitement": "Les traitements antirétroviraux permettent de contrôler le VIH. Avec un traitement efficace et un suivi médical régulier, les personnes vivant avec le VIH peuvent vivre longtemps et en bonne santé. Lorsque la charge virale reste durablement indétectable, le VIH ne se transmet pas par voie sexuelle : c’est le principe I=I.",
        "difference": "Le VIH est le virus de l’immunodéficience humaine. Le sida est le stade avancé de l’infection par le VIH. Avoir le VIH ne signifie donc pas forcément avoir le sida.",
        "preservatif": "L’utilisation correcte d’un préservatif externe ou interne réduit fortement le risque de transmission du VIH et d’autres infections sexuellement transmissibles.",
        "grossesse": "Avec un dépistage, un traitement antirétroviral et un suivi médical adaptés, le risque de transmission du VIH de la mère à l’enfant peut être fortement réduit.",
        "hors_sujet": "Je peux répondre aux questions générales sur le VIH, le sida, la transmission, la prévention, le dépistage et les traitements. 😊",
        "inconnu": "Je n’ai pas trouvé de réponse assez précise dans ma base d’informations. Je préfère ne pas inventer une réponse médicale. Tu peux reformuler ta question ou demander conseil à un professionnel de santé."
    },

    "en": {
        "bonjour": "Hello! 😊 I’m VYRA, your HIV information assistant. What would you like to know about HIV?",
        "merci": "You’re welcome! ❤️ Feel free to ask another question.",
        "femme": "Being a woman does not mean that you have HIV. Only an HIV test can determine your status.",
        "transmission": "HIV can be transmitted through specific exposure to blood, semen, vaginal or rectal fluids, and breast milk.",
        "non_transmission": "HIV is not transmitted through hugging, handshakes, sharing food or dishes, toilets, swimming pools, sweat, tears or mosquitoes.",
        "baiser": "HIV is not transmitted through ordinary kissing or saliva.",
        "symptomes": "Some people experience flu-like symptoms a few weeks after infection, while others have no symptoms. Only a test can determine HIV status.",
        "depistage": "Testing is the only way to know your HIV status. Different tests have different window periods.",
        "urgence": "⚠️ If a possible HIV exposure happened within the last 72 hours, seek urgent medical care now to assess whether post-exposure prophylaxis (PEP) is appropriate.",
        "prep": "PrEP is preventive medication for HIV-negative people who may be exposed to HIV. It requires medical follow-up.",
        "traitement": "Antiretroviral treatment controls HIV. With effective treatment and regular medical care, people living with HIV can live long, healthy lives.",
        "difference": "HIV is the virus that attacks the immune system. AIDS is the advanced stage of HIV infection.",
        "preservatif": "Using condoms correctly greatly reduces the risk of HIV and other sexually transmitted infections.",
        "grossesse": "With testing, treatment and appropriate medical care, the risk of transmission from parent to child can be greatly reduced.",
        "hors_sujet": "I can help with general information about HIV, AIDS, transmission, prevention, testing and treatment.",
        "inconnu": "I could not find a sufficiently precise answer. Please rephrase your question or ask a healthcare professional."
    },

    "ar": {
        "bonjour": "مرحباً! 😊 أنا VYRA، مساعدك للمعلومات حول فيروس نقص المناعة البشرية. ماذا تريد أن تعرف؟",
        "merci": "على الرحب والسعة! ❤️ يمكنك طرح المزيد من الأسئلة.",
        "femme": "كونك امرأة لا يعني أنك مصابة بفيروس نقص المناعة البشرية. الفحص وحده يحدد الحالة.",
        "transmission": "يمكن أن ينتقل الفيروس عبر الدم والسائل المنوي والإفرازات المهبلية أو الشرجية وحليب الأم في حالات محددة.",
        "non_transmission": "لا ينتقل الفيروس عن طريق العناق أو المصافحة أو مشاركة الطعام أو المراحيض أو المسابح أو العرق أو الدموع أو البعوض.",
        "baiser": "لا ينتقل فيروس نقص المناعة البشرية عن طريق اللعاب أو التقبيل العادي.",
        "symptomes": "قد تظهر أعراض تشبه الإنفلونزا بعد أسابيع من العدوى، وقد لا تظهر أي أعراض. الفحص وحده يحدد الحالة.",
        "depistage": "الفحص هو الطريقة الوحيدة لمعرفة حالة الإصابة. تختلف فترة الكشف حسب نوع الاختبار.",
        "urgence": "⚠️ إذا حدث تعرض محتمل للفيروس خلال آخر 72 ساعة، توجّه فوراً إلى الاستعجالات لتقييم الحاجة إلى العلاج الوقائي بعد التعرض.",
        "prep": "PrEP هو علاج وقائي للأشخاص غير المصابين الذين قد يتعرضون للفيروس. يحتاج إلى متابعة طبية.",
        "traitement": "تساعد العلاجات المضادة للفيروسات على السيطرة على الفيروس. مع العلاج والمتابعة الطبية يمكن للمتعايشين مع الفيروس العيش بصحة جيدة.",
        "difference": "فيروس نقص المناعة البشرية هو الفيروس الذي يهاجم جهاز المناعة. أما الإيدز فهو مرحلة متقدمة من العدوى.",
        "preservatif": "يساعد الاستعمال الصحيح للواقي على تقليل خطر انتقال الفيروس والأمراض المنقولة جنسياً.",
        "grossesse": "يمكن تقليل انتقال الفيروس من الأم إلى الطفل بشكل كبير بفضل الفحص والعلاج والمتابعة الطبية.",
        "hors_sujet": "يمكنني مساعدتك بمعلومات عامة حول فيروس نقص المناعة والإيدز وطرق الانتقال والوقاية والفحص والعلاج.",
        "inconnu": "لم أجد إجابة دقيقة بما يكفي في قاعدة معلوماتي. يمكنك إعادة صياغة السؤال أو استشارة مختص صحي."
    }
}


# ==========================================================
# 2. BASE DE CONNAISSANCES DETAILLEE EN FRANCAIS
# ==========================================================

REPONSES_DETAILLEES_FR = {

    "definition": """Le VIH signifie virus de l’immunodéficience humaine.
C’est un virus qui attaque progressivement certaines cellules du système immunitaire.
Sans traitement, l’infection peut évoluer vers le sida.
Avec un traitement antirétroviral et un suivi régulier, une personne vivant avec le VIH peut généralement vivre longtemps et en bonne santé.""",

    "causes": """Le VIH est causé par le virus de l’immunodéficience humaine.
On ne l’attrape pas en étant simplement proche d’une personne séropositive.
La transmission nécessite une exposition à certains liquides biologiques dans des circonstances précises.""",

    "symptomes_precoces": """Certaines personnes peuvent présenter des symptômes ressemblant à la grippe quelques semaines après l’infection : fièvre, fatigue, maux de gorge, ganglions gonflés, maux de tête ou éruption cutanée.
D’autres personnes ne présentent aucun symptôme.
Ces signes ne prouvent pas une infection par le VIH. Seul un test adapté permet de connaître son statut.""",

    "delai_symptomes": """Lorsqu’ils apparaissent, les premiers symptômes peuvent survenir quelques semaines après l’infection. Certaines personnes n’en ont aucun pendant longtemps.
Il est impossible de confirmer une infection à partir des symptômes.""",

    "stades": """L’infection par le VIH peut évoluer en plusieurs phases : une phase précoce, une phase chronique parfois sans symptômes, puis, sans traitement, un stade avancé appelé sida.
Le traitement antirétroviral permet de contrôler le virus et de prévenir cette évolution.""",

    "sida_avance": """Le sida est le stade le plus avancé de l’infection par le VIH, lorsque le système immunitaire est très affaibli.
Toute personne vivant avec le VIH n’a pas le sida.""",

    "test_delai": """Aucun test ne détecte le VIH immédiatement après une exposition.
Le délai dépend du test utilisé.
À titre indicatif, les tests NAT peuvent détecter généralement entre 10 et 33 jours, les tests antigène/anticorps en laboratoire entre 18 et 45 jours, les tests rapides entre 18 et 90 jours et les tests d’anticorps entre 23 et 90 jours.
Demande au centre de dépistage quand faire le test et s’il faut le répéter.""",

    "resultat_positif": """Un résultat de dépistage réactif ou positif doit être confirmé selon les procédures recommandées.
Contacte rapidement un professionnel de santé. Des traitements efficaces existent.
Un résultat positif ne signifie pas automatiquement que tu es au stade sida.""",

    "traitement_guerison": """Il n’existe pas actuellement de traitement courant qui élimine définitivement le VIH.
Les traitements antirétroviraux bloquent la multiplication du virus et permettent de protéger le système immunitaire.
N’arrête jamais un traitement sans avis médical.""",

    "vie_normale": """Oui. Avec un traitement efficace et un suivi médical régulier, les personnes vivant avec le VIH peuvent étudier, travailler, avoir des relations, fonder une famille et mener une vie active.""",

    "indetectable": """I=I signifie Indétectable = Intransmissible.
Une personne vivant avec le VIH qui prend son traitement et maintient durablement une charge virale indétectable ne transmet pas le VIH par voie sexuelle.""",

    "rapport_sexuel": """Le VIH peut se transmettre lors de rapports vaginaux ou anaux lorsqu’il y a exposition à des liquides biologiques contenant le virus et qu’aucune prévention efficace ne protège.
Le préservatif, la PrEP et une charge virale durablement indétectable sont des moyens importants de prévention.""",

    "sexe_oral": """Le risque de transmission du VIH lors du sexe oral est généralement très faible.
La présence de sang ou de plaies peut modifier l’évaluation.
Le sexe oral peut transmettre d’autres infections sexuellement transmissibles.""",

    "sang": """Le VIH peut se transmettre si du sang contenant le virus entre dans l’organisme, par exemple par le partage de seringues ou de matériel d’injection.
En cas de piqûre accidentelle ou de contact avec une plaie ou une muqueuse, demande immédiatement un avis médical.""",

    "moustique": """Non. Le VIH ne se transmet pas par les moustiques ni par les piqûres d’insectes.""",

    "objets": """Le VIH ne se transmet pas en partageant des toilettes, une douche, une piscine, des vêtements, des couverts, des verres ou de la nourriture.
Les contacts habituels sont sans risque.""",

    "salive": """Non. La salive ne transmet pas le VIH.
Les baisers ordinaires, les câlins et les poignées de main ne transmettent pas le VIH.""",

    "don_sang": """Le don de sang ne transmet pas le VIH au donneur lorsque le matériel et les procédures sont stériles et à usage unique.""",

    "prevention": """La prévention repose sur plusieurs moyens : utiliser correctement un préservatif, envisager la PrEP si nécessaire, recourir rapidement au TPE/PPE après une exposition possible, ne jamais partager le matériel d’injection et réaliser des dépistages adaptés.""",

    "ist": """Le VIH n’est pas la seule infection sexuellement transmissible.
D’autres IST, comme la syphilis, la gonorrhée, la chlamydia ou l’hépatite B, peuvent se transmettre lors de rapports sexuels.""",

    "discrimination": """Une personne vivant avec le VIH mérite le même respect que toute autre personne.
Le VIH ne se transmet pas par les contacts de la vie quotidienne.
La confidentialité et l’absence de jugement sont essentielles.""",

    "enfant": """Le VIH peut être transmis de la mère à l’enfant pendant la grossesse, l’accouchement ou l’allaitement.
Un dépistage, un traitement et un suivi médical adaptés réduisent fortement ce risque.""",

    "transmission_mere": """La transmission mère-enfant peut survenir pendant la grossesse, l’accouchement ou l’allaitement.
Avec le dépistage, le traitement et les soins adaptés, le risque peut être fortement réduit.""",

    "test_maison": """Il existe des autotests VIH dans certains pays.
Ils doivent être utilisés exactement selon leur notice et respectent une période fenêtre.
Un résultat réactif doit être confirmé par un service de santé.""",

    "peur": """Je comprends que cette question puisse inquiéter.
On ne peut pas savoir si une personne a le VIH à partir de son apparence ou de symptômes.
Le risque dépend de ce qui s’est réellement passé.
Seul un professionnel et un test adapté peuvent évaluer et confirmer la situation."""
}


# ==========================================================
# 3. MOTS-CLES POUR LA BASE DETAILLEE
# ==========================================================

MOTS_DETAILLES = {
    "definition": ["c est quoi le vih", "qu est ce que le vih", "que signifie vih", "definition du vih", "definir le vih", "virus vih", "vih c est quoi"],
    "causes": ["cause du vih", "causes du vih", "origine du vih", "comment attrape t on le vih", "d ou vient le vih"],
    "symptomes_precoces": ["premiers symptomes", "premiers signes", "symptomes du vih", "signes du vih", "symptome vih", "comment savoir si on a le vih", "comment reconnaitre le vih"],
    "delai_symptomes": ["quand apparaissent", "au bout de combien de temps", "combien de temps apres", "delai des symptomes", "apres combien de jours", "symptomes apres rapport"],
    "stades": ["stades du vih", "phases du vih", "evolution du vih", "comment evolue le vih", "combien de temps pour evoluer"],
    "sida_avance": ["c est quoi le sida", "qu est ce que le sida", "definition du sida", "stade sida", "avoir le sida"],
    "test_delai": ["periode fenetre", "delai du test", "quand faire le test", "combien de temps pour depister", "test apres rapport", "quand le vih est detectable", "test negatif trop tot"],
    "resultat_positif": ["test positif", "resultat positif", "je suis seropositif", "je suis seropositive", "que faire si positif", "depistage reactif"],
    "traitement_guerison": ["peut on guerir", "est ce que ca se guerit", "guerison du vih", "traitement pour guerir", "medicament contre le vih", "existe t il un vaccin", "vaccin contre le vih"],
    "vie_normale": ["vivre normalement", "vivre avec le vih", "peut on travailler", "peut on avoir des enfants", "esperance de vie", "vie quotidienne"],
    "indetectable": ["indetectable", "intransmissible", "i=i", "charge virale indetectable", "peut il transmettre si"],
    "rapport_sexuel": ["rapport sexuel", "rapport vaginal", "rapport anal", "relation sexuelle", "sans preservatif", "rapport non protege", "sexe sans protection"],
    "sexe_oral": ["sexe oral", "fellation", "cunnilingus", "rapport oral", "faire une pipe"],
    "sang": ["contact avec le sang", "sang infecte", "piqure", "seringue", "aiguille", "tatouage", "piercing", "materiel non sterile"],
    "moustique": ["moustique", "piqure de moustique", "insecte", "mouche"],
    "objets": ["toilettes", "piscine", "vaisselle", "partager un verre", "partager un repas", "vetement", "douche", "objet", "poignee de main", "calin", "etre proche"],
    "salive": ["salive", "embrasser", "bisou", "baiser", "bouche", "crachat"],
    "don_sang": ["donner son sang", "don de sang", "transfusion", "donneur de sang"],
    "prevention": ["comment eviter", "comment prevenir", "moyen de prevention", "se proteger", "protection contre le vih", "eviter le vih"],
    "ist": ["autres ist", "maladie sexuellement", "infection sexuellement", "mst", "syphilis", "chlamydia", "gonorrhee"],
    "discrimination": ["peur des personnes", "toucher une personne", "vivre avec une personne", "travailler avec", "contagieux au quotidien", "discrimination", "serophobie"],
    "enfant": ["enfant", "bebe", "allaitement", "grossesse", "enceinte", "mere et enfant"],
    "transmission_mere": ["transmission mere enfant", "mere au bebe", "mere a l enfant", "accouchement"],
    "test_maison": ["autotest", "test a la maison", "test maison", "test rapide chez soi"],
    "peur": ["j ai peur", "je suis inquiet", "je suis inquiete", "suis je infecte", "suis je infectee", "est ce que je suis menace", "est ce que je suis malade"]
}


# ==========================================================
# 4. LES 40 QUESTIONS FREQUENTES SUPPLEMENTAIRES
# ==========================================================

FAQ_FREQUENTES_FR = [

    (["t es qui", "t'es qui", "tu es qui", "qui es tu", "qui es-tu", "vous etes qui", "vous êtes qui"],
     "Je suis VYRA 😊, ton assistant virtuel de sensibilisation au VIH et au sida."),

    (["comment tu t appelles", "comment tu t'appelles", "ton nom", "quel est ton nom"],
     "Je m'appelle VYRA. Je suis là pour informer et sensibiliser sur le VIH."),

    (["tu fais quoi", "quel est ton role", "a quoi tu sers"],
     "Je réponds aux questions concernant le VIH, le sida, les symptômes, la transmission, le dépistage et la prévention."),

    (["qui t a cree", "qui t'a cree", "qui a cree vyra"],
     "Je suis le chatbot VYRA, conçu pour faciliter l'accès aux informations sur le VIH."),

    (["tu es un robot", "tu es humain"],
     "Je suis un chatbot informatique, pas une personne humaine."),

    (["tu es medecin", "tu es docteur"],
     "Non, je ne suis pas médecin. Je fournis des informations générales et je ne remplace pas un professionnel de santé."),

    (["tu peux me diagnostiquer", "peux tu faire un diagnostic"],
     "Non. Seul un dépistage adapté permet de connaître son statut VIH."),

    (["comment attrape t on le vih", "comment on attrape le vih"],
     REPONSES_DETAILLEES_FR["causes"]),

    (["quels sont les premiers symptomes", "premiers signes du vih"],
     REPONSES_DETAILLEES_FR["symptomes_precoces"]),

    (["est ce que le vih se voit", "peut on reconnaitre une personne seropositive"],
     "Non. On ne peut pas reconnaître une personne vivant avec le VIH à son apparence."),

    (["peut on avoir le vih sans symptome", "sans symptome"],
     "Oui. Une personne peut vivre avec le VIH pendant longtemps sans présenter de symptômes."),

    (["le vih se transmet par un bisou", "peut on attraper le vih en embrassant"],
     REPONSES["fr"]["baiser"]),

    (["le vih se transmet par la salive"],
     REPONSES_DETAILLEES_FR["salive"]),

    (["peut on attraper le vih par les moustiques", "moustique vih"],
     REPONSES_DETAILLEES_FR["moustique"]),

    (["peut on partager un verre", "partager les couverts"],
     "Oui, tu peux partager un verre, des couverts ou un repas avec une personne vivant avec le VIH sans risque de transmission."),

    (["peut on vivre avec un seropositif", "vivre avec une personne seropositive"],
     "Oui. Les contacts quotidiens, les repas partagés et la vie sous le même toit ne transmettent pas le VIH."),

    (["quelle difference entre vih et sida"],
     REPONSES["fr"]["difference"]),

    (["est ce que le vih se guerit", "peut on guerir du vih"],
     REPONSES_DETAILLEES_FR["traitement_guerison"]),

    (["existe t il un vaccin contre le vih", "vaccin vih"],
     "Il n'existe pas actuellement de vaccin largement disponible qui protège efficacement contre le VIH."),

    (["comment faire un test vih", "comment se faire depister"],
     "Tu peux réaliser un dépistage auprès d'un centre de santé ou d'un centre de dépistage. Un professionnel pourra te conseiller le test adapté."),

    (["le test vih est il fiable", "test vih fiable"],
     "Les tests sont fiables lorsqu'ils sont réalisés au bon moment et selon leurs consignes. La période fenêtre dépend du type de test."),

    (["combien de temps attendre pour faire un test"],
     REPONSES_DETAILLEES_FR["test_delai"]),

    (["que faire apres un test positif", "mon test vih est positif"],
     REPONSES_DETAILLEES_FR["resultat_positif"]),

    (["comment eviter le vih", "comment se proteger du vih"],
     REPONSES_DETAILLEES_FR["prevention"]),

    (["c est quoi la prep", "a quoi sert la prep"],
     REPONSES["fr"]["prep"]),

    (["c est quoi le tpe", "c est quoi la pep"],
     "Le TPE ou PPE est un traitement d'urgence qui peut être proposé après une exposition possible au VIH. Il doit commencer le plus rapidement possible, au plus tard dans les 72 heures."),

    (["j ai eu un rapport a risque", "rapport a risque hier"],
     REPONSES["fr"]["urgence"]),

    (["une femme peut elle avoir le vih", "les femmes peuvent elles attraper le vih"],
     "Oui. Le VIH peut toucher les femmes comme les hommes. Le risque dépend d'une exposition, pas du sexe de la personne."),

    (["une personne seropositive peut elle avoir des enfants"],
     "Oui. Avec un traitement et un suivi médical adaptés, une personne vivant avec le VIH peut avoir un enfant en réduisant fortement le risque de transmission."),

    (["peut on travailler avec une personne seropositive"],
     "Oui. Le VIH ne se transmet pas par les contacts professionnels ordinaires."),

    (["peut on faire du sport avec une personne seropositive"],
     "Oui. Faire du sport ensemble ne transmet pas le VIH."),

    (["une personne seropositive peut elle se marier"],
     "Oui. Une personne vivant avec le VIH peut se marier et avoir une vie affective. Un suivi médical adapté est important."),

    (["est ce que le vih est mortel"],
     "Sans traitement, le VIH peut évoluer vers une maladie grave. Avec un traitement efficace, les personnes vivant avec le VIH peuvent généralement vivre longtemps."),

    (["que signifie indetectable"],
     REPONSES_DETAILLEES_FR["indetectable"]),

    (["pourquoi faire un depistage"],
     "Le dépistage permet de connaître son statut, de commencer rapidement un traitement si nécessaire et de protéger sa santé."),

    (["est ce que je dois avoir peur du vih"],
     "Il est normal de se poser des questions. Le plus important est de connaître les véritables modes de transmission et de faire un dépistage adapté en cas d'exposition possible."),

    (["comment aider une personne seropositive"],
     "Écoute-la, respecte sa confidentialité et évite les jugements. Une personne vivant avec le VIH mérite le même respect que tout le monde."),

    (["est ce que le vih est contagieux au quotidien"],
     "Non. Le VIH ne se transmet pas par les câlins, les poignées de main, les repas partagés ou les contacts quotidiens."),

    (["tu comprends l arabe", "parles tu arabe"],
     "نعم، يمكنك طرح أسئلتك باللغة العربية حول فيروس نقص المناعة البشرية والوقاية والفحص والعلاج."),

    (["tu parles anglais", "do you speak english"],
     "Yes! You can ask me questions about HIV transmission, symptoms, testing, prevention and treatment.")
]


# ==========================================================
# 5. MOTS-CLES GENERAUX
# ==========================================================

MOTS = {
    "urgence": [
        "72h", "72 h", "72 heures", "24h", "24 heures",
        "il y a 24", "hier", "exposition recente",
        "exposition possible", "rapport a risque",
        "rapport non protege", "accident", "pep", "ppe",
        "tpe", "post exposition", "تعرض", "آخر 72", "72 ساعة"
    ],

    "femme": [
        "je suis une femme", "je suis femme", "une femme",
        "femme", "est ce que je suis menace", "suis je menace",
        "انا امرأة", "هل المرأة"
    ],

    "non_transmission": [
        "calin", "câlin", "poignee de main",
        "toilette", "piscine", "moustique", "repas",
        "vaisselle", "salive", "sueur", "larmes",
        "transmettre par", "contamine par"
    ],

    "baiser": [
        "baiser", "embrasser", "bisou", "embrasse",
        "kissing", "kiss", "تقبيل"
    ],

    "transmission": [
        "transmission", "transmettre", "comment attrape",
        "comment se transmet", "contamination", "contaminer",
        "sang", "rapport sexuel", "sexuel", "aiguille",
        "allaitement", "ينتقل", "انتقال", "الدم"
    ],

    "depistage": [
        "depistage", "dépistage", "test", "tester",
        "analyse", "resultat", "résultat",
        "seropositif", "séropositif", "seronegatif"
    ],

    "symptomes": [
        "symptome", "symptômes", "symptom", "signe",
        "fievre", "fièvre", "fatigue", "eruption",
        "طفح", "أعراض", "اعراض"
    ],

    "prep": [
        "prep", "prép", "prophylaxie pre",
        "prophylaxie pré"
    ],

    "traitement": [
        "traitement", "medicament", "médicament",
        "guerir", "guérir", "soigner", "charge virale",
        "indetectable", "indétectable", "antiretroviral"
    ],

    "difference": [
        "difference", "différence", "vih et sida",
        "vih ou sida", "sida", "aids", "ما الفرق"
    ],

    "preservatif": [
        "preservatif", "préservatif", "capote",
        "condom", "protection", "واقي"
    ],

    "grossesse": [
        "grossesse", "enceinte", "maman", "mere",
        "mère", "enfant", "bébé", "bebe"
    ]
}


# ==========================================================
# 6. SALUTATIONS
# ==========================================================

SALUTATIONS = [
    "bonjour", "bonsoir", "salut", "coucou",
    "hello", "hi", "hey", "مرحبا",
    "السلام عليكم", "صباح الخير", "مساء الخير"
]

REMERCIEMENTS = [
    "merci", "thanks", "thank you", "شكرا", "شكراً"
]


# ==========================================================
# 7. NORMALISATION ET DETECTION DE LANGUE
# ==========================================================

def normaliser(texte):
    texte = texte.lower().strip()
    texte = "".join(
        c for c in unicodedata.normalize("NFD", texte)
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"\s+", " ", texte)


def detecter_langue(message):
    if re.search(r"[\u0600-\u06FF]", message):
        return "ar"

    n = normaliser(message)

    anglais = [
        "hello", "hi", "how", "what", "can i",
        "does", "is hiv", "thank you", "thanks",
        "symptoms", "testing", "transmitted"
    ]

    return "en" if any(x in n for x in anglais) else "fr"


# ==========================================================
# 8. FONCTION PRINCIPALE DU CHATBOT
# ==========================================================

def repondre(message):

    n = normaliser(message)
    langue = detecter_langue(message)

    # Salutations
    if any(normaliser(s) in n for s in SALUTATIONS) and len(n.split()) <= 7:
        return REPONSES[langue]["bonjour"]

    # Remerciements
    if any(normaliser(s) in n for s in REMERCIEMENTS):
        return REPONSES[langue]["merci"]

    # Priorité absolue aux situations urgentes
    urgence = [normaliser(x) for x in MOTS["urgence"]]

    if any(x in n for x in urgence):
        return REPONSES[langue]["urgence"]

    # Questions fréquentes supplémentaires
    if langue == "fr":
        for formulations, reponse in FAQ_FREQUENTES_FR:
            if any(normaliser(q) in n for q in formulations):
                return reponse

    # Questions détaillées françaises
    if langue == "fr":

        ordre_detail = [
            "test_maison", "resultat_positif", "test_delai",
            "delai_symptomes", "symptomes_precoces",
            "transmission_mere", "sexe_oral",
            "rapport_sexuel", "indetectable",
            "traitement_guerison", "vie_normale",
            "sida_avance", "definition", "stades",
            "causes", "moustique", "salive", "objets",
            "sang", "don_sang", "prevention", "ist",
            "discrimination", "enfant", "peur"
        ]

        for intention in ordre_detail:

            mots = [
                normaliser(x)
                for x in MOTS_DETAILLES[intention]
            ]

            if any(m and m in n for m in mots):
                return REPONSES_DETAILLEES_FR[intention]

    # Base principale conservée pour les trois langues
    ordre = [
        "femme", "baiser", "non_transmission",
        "depistage", "prep", "traitement",
        "difference", "symptomes", "grossesse",
        "preservatif", "transmission"
    ]

    for intention in ordre:

        mots = [
            normaliser(m)
            for m in MOTS[intention]
        ]

        if any(m and m in n for m in mots):
            return REPONSES[langue][intention]

    # Présentation de VYRA
    identite = [
        "qui es tu", "qui es-tu", "t es qui", "t'es qui",
        "tu es qui", "ton nom", "who are you",
        "your name", "comment tu t appelles"
    ]

    if any(normaliser(x) in n for x in identite):

        if langue == "fr":
            return "Je suis VYRA 😊, l’assistant virtuel de sensibilisation sur le VIH. Je peux répondre à tes questions sur le VIH, le sida, les symptômes, la transmission, la prévention, le dépistage et les traitements."

        return REPONSES[langue]["bonjour"]

    # Questions hors sujet
    if any(x in n for x in [
        "meteo", "football", "recette",
        "politique", "weather", "recipe"
    ]):
        return REPONSES[langue]["hors_sujet"]

    # Réponse par défaut
    return REPONSES[langue]["inconnu"]


# ==========================================================
# 9. ROUTES FLASK
# ==========================================================

@app.route("/")
def home():
    return send_from_directory(".", "accueil.html")


@app.route("/consultation")
def consultation():
    return send_from_directory(".", "index.html")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    if not isinstance(message, str) or not message.strip():
        return jsonify(error="Veuillez écrire une question."), 400

    message = message.strip()

    if len(message) > 1500:
        return jsonify(
            error="Votre message est trop long (maximum 1500 caractères)."
        ), 400

    return jsonify(
        response=repondre(message),
        mode="local"
    )


# ==========================================================
# 10. LANCEMENT DE L'APPLICATION
# ==========================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", "5000"))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
