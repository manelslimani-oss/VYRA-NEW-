from flask import Flask, request, jsonify, send_from_directory
import os
import re
import unicodedata

app = Flask(__name__)

# VYRA fonctionne entièrement en local : aucune clé API, aucun appel externe.
REPONSES = {
    "fr": {
        "bonjour": "Bonjour ! 😊 Je suis VYRA, ton assistant d’information sur le VIH. Je suis là pour répondre à tes questions avec bienveillance et sans jugement. Que souhaites-tu savoir sur le VIH ?",
        "merci": "Avec plaisir ! ❤️ N’hésite pas à poser d’autres questions. S’informer est déjà un pas important.",
        "femme": "Être une femme ne signifie absolument pas être porteuse du VIH. Le VIH ne dépend pas du sexe ou du genre : le risque éventuel dépend d’une exposition précise (par exemple certains rapports sexuels sans protection adaptée ou un contact avec du sang contaminé). On ne peut pas déterminer son statut à partir du sexe, de l’apparence ou de symptômes. Seul un test permet de connaître son statut. Si tu crains une exposition récente, je peux t’indiquer les démarches générales à suivre.",
        "transmission": "Le VIH peut se transmettre lors de certaines expositions au sang, au sperme, aux sécrétions vaginales ou rectales et au lait maternel. Les principales situations sont certains rapports sexuels sans protection adaptée, le partage de matériel d’injection contaminé et, sans prévention/prise en charge, la transmission de la mère à l’enfant. Le risque dépend de la situation. Le VIH ne se transmet pas par les contacts ordinaires comme les câlins ou les poignées de main.",
        "non_transmission": "Non. Le VIH ne se transmet pas par les câlins, les poignées de main, les baisers sociaux, le partage de vaisselle ou de repas, les toilettes, les piscines, la sueur, les larmes ou les moustiques. Tu peux partager les activités quotidiennes avec une personne vivant avec le VIH sans risque de transmission.",
        "baiser": "Le VIH ne se transmet pas par un baiser ordinaire ou la salive. Les baisers ne constituent pas une voie de transmission du VIH. Il n’y a pas de risque lors d’un contact social habituel.",
        "symptomes": "Certaines personnes peuvent avoir des symptômes ressemblant à ceux de la grippe quelques semaines après l’infection, tandis que d’autres n’ont aucun symptôme. Ces signes ne sont pas spécifiques au VIH et ne permettent pas de poser un diagnostic. Seul un dépistage permet de connaître son statut.",
        "depistage": "Le dépistage est le seul moyen de connaître son statut VIH. Il existe différents tests et leurs délais de détection (périodes fenêtres) varient. Un centre de dépistage ou un professionnel de santé pourra conseiller le test adapté et préciser si un contrôle ultérieur est nécessaire. Le dépistage est une démarche de santé, sans jugement.",
        "urgence": "⚠️ Si une exposition possible au VIH a eu lieu au cours des dernières 72 heures, consulte immédiatement un service d’urgence ou un professionnel de santé pour évaluer la nécessité d’un traitement post-exposition (TPE/PPE). Il doit être commencé le plus tôt possible et au plus tard dans les 72 heures. N’attends pas une réponse en ligne.",
        "prep": "La PrEP (prophylaxie pré-exposition) est un traitement préventif destiné aux personnes séronégatives qui peuvent être exposées au VIH. Elle doit être prescrite et suivie par un professionnel de santé, avec des tests et un suivi adaptés. Elle ne protège pas des autres infections sexuellement transmissibles.",
        "traitement": "Les traitements antirétroviraux permettent de contrôler le VIH. Avec un traitement efficace et un suivi médical régulier, les personnes vivant avec le VIH peuvent vivre longtemps et en bonne santé. Lorsque la charge virale reste durablement indétectable grâce au traitement, le VIH ne se transmet pas par voie sexuelle : c’est le principe I=I (indétectable = intransmissible).",
        "difference": "Le VIH est le virus de l’immunodéficience humaine. Le sida est le stade avancé de l’infection par le VIH, lorsque le système immunitaire est fortement affaibli. Avoir le VIH ne signifie donc pas forcément avoir le sida. Les traitements permettent souvent d’éviter l’évolution vers ce stade.",
        "preservatif": "L’utilisation correcte d’un préservatif externe ou interne réduit fortement le risque de transmission du VIH et d’autres infections sexuellement transmissibles. La PrEP peut aussi prévenir le VIH pour certaines personnes. Un professionnel de santé peut aider à choisir les moyens de prévention adaptés.",
        "grossesse": "Avec un dépistage, un traitement antirétroviral et un suivi médical adaptés, le risque de transmission du VIH de la mère à l’enfant peut être fortement réduit. Une personne enceinte vivant avec le VIH doit être accompagnée par une équipe médicale. Ne modifie jamais un traitement sans avis médical.",
        "hors_sujet": "Je peux répondre aux questions générales sur le VIH, le sida, la transmission, la prévention, le dépistage et les traitements. 😊 Pour un autre sujet, je ne suis pas l’assistant le mieux adapté, mais je peux toujours t’orienter vers une information générale.",
        "inconnu": "Je n’ai pas trouvé de réponse assez précise dans ma base d’informations. Je préfère ne pas inventer une réponse médicale. Tu peux reformuler ta question ou demander conseil à un professionnel de santé / centre de dépistage."
    },
    "en": {
        "bonjour": "Hello! 😊 I’m VYRA, your HIV information assistant. I’m here to answer your questions kindly and without judgment. What would you like to know about HIV?",
        "merci": "You’re welcome! ❤️ Feel free to ask another question. Learning about HIV is an important step.",
        "femme": "Being a woman does not mean that you have HIV. HIV status cannot be determined from sex, gender, appearance or symptoms. Possible risk depends on a specific exposure. Only an HIV test can tell you your status. If you may have been exposed recently, seek medical advice promptly.",
        "transmission": "HIV can be transmitted through specific exposure to blood, semen, vaginal or rectal fluids, and breast milk. Main situations include certain sexual exposures without effective protection, sharing contaminated injecting equipment, and transmission during pregnancy, birth or breastfeeding without appropriate prevention and care.",
        "non_transmission": "HIV is not transmitted through hugging, handshakes, sharing food or dishes, toilets, swimming pools, sweat, tears or mosquitoes. Everyday contact with a person living with HIV is safe.",
        "baiser": "HIV is not transmitted through ordinary kissing or saliva. Social kissing is not a route of HIV transmission.",
        "symptomes": "Some people experience flu-like symptoms a few weeks after infection, while others have no symptoms. These signs are not specific to HIV and cannot diagnose it. Only a test can determine HIV status.",
        "depistage": "Testing is the only way to know your HIV status. Different tests have different window periods. A testing center or healthcare professional can recommend the right test and explain whether follow-up testing is needed.",
        "urgence": "⚠️ If a possible HIV exposure happened within the last 72 hours, seek urgent medical care now to assess whether post-exposure prophylaxis (PEP) is appropriate. It should start as soon as possible and no later than 72 hours. Do not wait for an online answer.",
        "prep": "PrEP is preventive medication for HIV-negative people who may be exposed to HIV. It requires a prescription and medical follow-up. It does not prevent other sexually transmitted infections.",
        "traitement": "Antiretroviral treatment controls HIV. With effective treatment and regular medical care, people living with HIV can live long, healthy lives. When viral load remains undetectable, HIV is not sexually transmitted (U=U).",
        "difference": "HIV is the virus that attacks the immune system. AIDS is the advanced stage of HIV infection. Having HIV does not automatically mean having AIDS. Treatment can prevent progression to this stage.",
        "preservatif": "Using condoms correctly greatly reduces the risk of HIV and other sexually transmitted infections. PrEP is another prevention option for some people. A healthcare professional can help you choose suitable prevention methods.",
        "grossesse": "With testing, antiretroviral treatment and appropriate medical care, the risk of transmission from parent to child can be greatly reduced. A pregnant person living with HIV should receive specialist medical support.",
        "hors_sujet": "I can help with general information about HIV, AIDS, transmission, prevention, testing and treatment. 😊 For other topics, I may not be the right assistant.",
        "inconnu": "I could not find a sufficiently precise answer in my information base, and I do not want to invent medical advice. Please rephrase your question or ask a healthcare professional or testing center."
    },
    "ar": {
        "bonjour": "مرحباً! 😊 أنا VYRA، مساعدك للمعلومات حول فيروس نقص المناعة البشرية. أنا هنا للإجابة عن أسئلتك بلطف ودون أحكام. ماذا تريد أن تعرف عن فيروس نقص المناعة البشرية؟",
        "merci": "على الرحب والسعة! ❤️ يمكنك طرح المزيد من الأسئلة في أي وقت. المعرفة خطوة مهمة للوقاية.",
        "femme": "كونك امرأة لا يعني إطلاقاً أنك مصابة بفيروس نقص المناعة البشرية. لا يمكن معرفة الحالة من الجنس أو المظهر أو الأعراض. يعتمد احتمال العدوى على نوع التعرض، والفحص وحده يحدد الحالة. إذا كنت تعتقدين أنك تعرضتِ للفيروس مؤخراً، اطلبي المشورة الطبية بسرعة.",
        "transmission": "يمكن أن ينتقل الفيروس عبر الدم والسائل المنوي والإفرازات المهبلية أو الشرجية وحليب الأم في حالات محددة. من الحالات الممكنة بعض العلاقات الجنسية دون حماية مناسبة، ومشاركة أدوات الحقن الملوثة، والانتقال من الأم إلى الطفل دون الوقاية والرعاية الطبية المناسبة.",
        "non_transmission": "لا ينتقل الفيروس عن طريق العناق أو المصافحة أو مشاركة الطعام والأواني أو المراحيض أو المسابح أو العرق أو الدموع أو البعوض. التعامل اليومي مع شخص متعايش مع الفيروس آمن.",
        "baiser": "لا ينتقل فيروس نقص المناعة البشرية عن طريق اللعاب أو التقبيل العادي.",
        "symptomes": "قد تظهر لدى بعض الأشخاص أعراض تشبه الإنفلونزا بعد أسابيع من العدوى، وقد لا تظهر أي أعراض لدى آخرين. هذه العلامات لا تثبت الإصابة. الفحص وحده يحدد الحالة.",
        "depistage": "الفحص هو الطريقة الوحيدة لمعرفة حالة الإصابة. تختلف فترة الكشف حسب نوع الاختبار. يمكن لمركز الفحص أو المختص الصحي إرشادك إلى الاختبار المناسب وموعد إعادته عند الحاجة.",
        "urgence": "⚠️ إذا حدث تعرض محتمل للفيروس خلال آخر 72 ساعة، توجّه فوراً إلى الاستعجالات أو مختص صحي لتقييم الحاجة إلى العلاج الوقائي بعد التعرض (PEP). يجب البدء به بأسرع وقت ممكن وخلال 72 ساعة كحد أقصى. لا تنتظر إجابة عبر الإنترنت.",
        "prep": "PrEP هو علاج وقائي للأشخاص غير المصابين الذين قد يتعرضون للفيروس. يحتاج إلى وصفة ومتابعة طبية، ولا يحمي من بقية الأمراض المنقولة جنسياً.",
        "traitement": "تساعد العلاجات المضادة للفيروسات على السيطرة على فيروس نقص المناعة. مع العلاج الفعال والمتابعة الطبية يمكن للمتعايشين مع الفيروس العيش بصحة جيدة. وعندما يصبح الحمل الفيروسي غير قابل للكشف بشكل مستمر، لا ينتقل الفيروس جنسياً.",
        "difference": "فيروس نقص المناعة البشرية هو الفيروس الذي يهاجم جهاز المناعة. أما الإيدز فهو مرحلة متقدمة من العدوى. الإصابة بالفيروس لا تعني بالضرورة الإصابة بالإيدز، فالعلاج يساعد على منع تطور المرض.",
        "preservatif": "يساعد الاستعمال الصحيح للواقي الذكري أو الأنثوي على تقليل خطر انتقال الفيروس والأمراض المنقولة جنسياً. ويمكن أن تكون PrEP وسيلة وقاية إضافية لبعض الأشخاص بعد استشارة مختص.",
        "grossesse": "يمكن تقليل انتقال الفيروس من الأم إلى الطفل بشكل كبير بفضل الفحص والعلاج والمتابعة الطبية المناسبة. يجب أن تحصل الحامل المتعايشة مع الفيروس على رعاية فريق طبي مختص.",
        "hors_sujet": "يمكنني مساعدتك بمعلومات عامة حول فيروس نقص المناعة والإيدز وطرق الانتقال والوقاية والفحص والعلاج. 😊",
        "inconnu": "لم أجد إجابة دقيقة بما يكفي في قاعدة معلوماتي، ولا أريد تقديم معلومة طبية غير مؤكدة. يمكنك إعادة صياغة السؤال أو استشارة مختص صحي أو مركز فحص."
    }
}

MOTS = {
    "urgence": ["72h", "72 h", "72 heures", "24h", "24 heures", "il y a 24", "hier", "exposition recente", "exposition possible", "rapport a risque", "rapport non protege", "accident", "pep", "ppe", "tpe", "post exposition", "تعرّض", "تعرض", "آخر 72", "72 ساعة"],
    "femme": ["je suis une femme", "je suis femme", "une femme", "femme", "est ce que je suis menace", "suis je menace", "suis-je menace", "انا امرأة", "أنا امرأة", "هل المرأة"],
    "non_transmission": ["calin", "câlin", "poignee de main", "poignée de main", "toilette", "piscine", "moustique", "repas", "vaisselle", "salive", "sueur", "larmes", "transmettre par", "contamine par", "ينتقل عن طريق العناق", "المصافحة", "البعوض"],
    "baiser": ["baiser", "embrasser", "bisou", "embrasse", "kissing", "kiss", "تقبيل", "القبل"],
    "transmission": ["transmission", "transmettre", "comment attrape", "comment se transmet", "contamination", "contaminer", "sang", "rapport sexuel", "sexuel", "aiguille", "allaitement", "ينتقل", "انتقال", "الدم"],
    "depistage": ["depistage", "dépistage", "test", "tester", "analyse", "resultat", "résultat", "seropositif", "séropositif", "seronegatif", "متى افحص", "الفحص", "تحليل"],
    "symptomes": ["symptome", "symptômes", "symptom", "signe", "fievre", "fièvre", "fatigue", "eruption", "طفح", "أعراض", "اعراض"],
    "prep": ["prep", "prép", "prophylaxie pre", "prophylaxie pré", "وقاية قبل"],
    "traitement": ["traitement", "medicament", "médicament", "guerir", "guérir", "soigner", "charge virale", "indetectable", "indétectable", "antiretroviral", "علاج", "دواء", "الحمل الفيروسي"],
    "difference": ["difference", "différence", "vih et sida", "vih ou sida", "sida", "aids", "ما الفرق", "الفرق بين"],
    "preservatif": ["preservatif", "préservatif", "capote", "condom", "protection", "واقي", "الواقي"],
    "grossesse": ["grossesse", "enceinte", "maman", "mere", "mère", "enfant", "bébé", "bebe", "حامل", "الحمل", "الطفل"]
}

SALUTATIONS = ["bonjour", "bonsoir", "salut", "coucou", "hello", "hi", "hey", "مرحبا", "السلام عليكم", "صباح الخير", "مساء الخير"]
REMERCIEMENTS = ["merci", "thanks", "thank you", "شكرا", "شكراً"]


def normaliser(texte):
    texte = texte.lower().strip()
    texte = "".join(c for c in unicodedata.normalize("NFD", texte) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", texte)


def detecter_langue(message):
    if re.search(r"[\u0600-\u06FF]", message):
        return "ar"
    n = normaliser(message)
    anglais = ["hello", "hi", "how", "what", "can i", "does", "is hiv", "thank you", "thanks", "symptoms", "testing", "transmitted"]
    return "en" if any(x in n for x in anglais) else "fr"


def repondre(message):
    n = normaliser(message)
    langue = detecter_langue(message)
    if any(x in n for x in [normaliser(s) for s in SALUTATIONS]) and len(n.split()) <= 7:
        return REPONSES[langue]["bonjour"]
    if any(x in n for x in [normaliser(s) for s in REMERCIEMENTS]):
        return REPONSES[langue]["merci"]

    # Priorité absolue aux situations nécessitant une prise en charge urgente.
    ordre = ["urgence", "femme", "baiser", "non_transmission", "depistage", "prep", "traitement", "difference", "symptomes", "grossesse", "preservatif", "transmission"]
    for intention in ordre:
        mots = [normaliser(m) for m in MOTS[intention]]
        if any(m in n for m in mots):
            return REPONSES[langue][intention]

    if any(x in n for x in ["comment vas tu", "comment ca va", "how are you", "ça va", "ca va"]):
        return REPONSES[langue]["bonjour"]
    if any(x in n for x in ["qui es tu", "qui es-tu", "ton nom", "who are you", "your name"]):
        return "Je suis VYRA, l’assistant virtuel de sensibilisation sur le VIH. Je peux t’aider à comprendre le VIH, le sida, la prévention, le dépistage et les traitements. 😊" if langue == "fr" else REPONSES[langue]["bonjour"]

    # Question clairement hors domaine : réponse courte plutôt qu'une information médicale inventée.
    if any(x in n for x in ["meteo", "météo", "football", "recette", "politique", "weather", "football", "recipe"]):
        return REPONSES[langue]["hors_sujet"]
    return REPONSES[langue]["inconnu"]


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
        return jsonify(error="Votre message est trop long (maximum 1500 caractères)."), 400
    return jsonify(response=repondre(message), mode="local")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
