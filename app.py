from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json, os, uuid
from datetime import datetime
import pandas as pd
import numpy as np
from collections import Counter

app = Flask(__name__)
app.secret_key = "dataflow_inf232_secret_2024"

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ─── Schemas des 3 domaines ───────────────────────────────────────────────────

DOMAINS = {
    "sante": {
        "label": "🏥 Santé",
        "color": "#e74c3c",
        "description": "Collecte de données épidémiologiques et cliniques",
        "fields": [
            {"name": "age", "label": "Âge (années)", "type": "number", "required": True},
            {"name": "sexe", "label": "Sexe", "type": "select", "options": ["Masculin", "Féminin"], "required": True},
            {"name": "region", "label": "Région", "type": "select", "options": ["Centre", "Littoral", "Ouest", "Nord", "Adamaoua", "Est", "Sud", "Nord-Ouest", "Sud-Ouest", "Extrême-Nord"], "required": True},
            {"name": "poids", "label": "Poids (kg)", "type": "number", "required": True},
            {"name": "taille", "label": "Taille (cm)", "type": "number", "required": True},
            {"name": "tension_sys", "label": "Tension systolique (mmHg)", "type": "number", "required": False},
            {"name": "tension_dia", "label": "Tension diastolique (mmHg)", "type": "number", "required": False},
            {"name": "pathologie", "label": "Pathologie déclarée", "type": "select", "options": ["Paludisme", "Hypertension", "Diabète", "Tuberculose", "VIH/SIDA", "Diarrhée", "Malnutrition", "Autre", "Aucune"], "required": True},
            {"name": "acces_soin", "label": "Accès aux soins", "type": "select", "options": ["Excellent", "Bon", "Moyen", "Difficile", "Très difficile"], "required": True},
            {"name": "assurance", "label": "Couverture maladie", "type": "select", "options": ["CNPS", "Privée", "Mutuelle", "Aucune"], "required": True},
        ]
    },
    "education": {
        "label": "🎓 Éducation",
        "color": "#3498db",
        "description": "Suivi des performances et conditions d'apprentissage",
        "fields": [
            {"name": "age_eleve", "label": "Âge de l'élève", "type": "number", "required": True},
            {"name": "sexe", "label": "Sexe", "type": "select", "options": ["Masculin", "Féminin"], "required": True},
            {"name": "niveau", "label": "Niveau scolaire", "type": "select", "options": ["Primaire", "Collège", "Lycée", "Université"], "required": True},
            {"name": "region", "label": "Région", "type": "select", "options": ["Centre", "Littoral", "Ouest", "Nord", "Adamaoua", "Est", "Sud", "Nord-Ouest", "Sud-Ouest", "Extrême-Nord"], "required": True},
            {"name": "type_ecole", "label": "Type d'établissement", "type": "select", "options": ["Public", "Privé laïc", "Privé confessionnel"], "required": True},
            {"name": "note_maths", "label": "Note Mathématiques /20", "type": "number", "required": True},
            {"name": "note_francais", "label": "Note Français /20", "type": "number", "required": True},
            {"name": "note_sciences", "label": "Note Sciences /20", "type": "number", "required": True},
            {"name": "absences", "label": "Nombre d'absences (mois)", "type": "number", "required": True},
            {"name": "acces_internet", "label": "Accès à Internet", "type": "select", "options": ["Oui à domicile", "Oui cybercafé", "Non"], "required": True},
        ]
    },
    "agriculture": {
        "label": "🌾 Agriculture",
        "color": "#27ae60",
        "description": "Données agro-climatiques et rendements agricoles",
        "fields": [
            {"name": "region", "label": "Région", "type": "select", "options": ["Centre", "Littoral", "Ouest", "Nord", "Adamaoua", "Est", "Sud", "Nord-Ouest", "Sud-Ouest", "Extrême-Nord"], "required": True},
            {"name": "superficie", "label": "Superficie cultivée (ha)", "type": "number", "required": True},
            {"name": "culture", "label": "Type de culture principale", "type": "select", "options": ["Maïs", "Cacao", "Café", "Manioc", "Plantain", "Arachide", "Sorgho", "Riz", "Coton", "Autre"], "required": True},
            {"name": "rendement", "label": "Rendement (tonnes/ha)", "type": "number", "required": True},
            {"name": "pluviometrie", "label": "Pluviométrie perçue", "type": "select", "options": ["Très bonne", "Bonne", "Normale", "Insuffisante", "Très insuffisante"], "required": True},
            {"name": "irrigation", "label": "Système d'irrigation", "type": "select", "options": ["Oui moderne", "Oui traditionnel", "Non"], "required": True},
            {"name": "engrais", "label": "Utilisation d'engrais", "type": "select", "options": ["Chimique", "Organique", "Mixte", "Aucun"], "required": True},
            {"name": "revenu_mensuel", "label": "Revenu mensuel estimé (FCFA)", "type": "number", "required": True},
            {"name": "appartenance_coop", "label": "Membre d'une coopérative", "type": "select", "options": ["Oui", "Non"], "required": True},
            {"name": "formation_agri", "label": "Formation agricole reçue", "type": "select", "options": ["Oui formelle", "Oui informelle", "Non"], "required": True},
        ]
    }
}

# ─── Utilitaires ──────────────────────────────────────────────────────────────

def get_data_file(domain):
    return os.path.join(DATA_DIR, f"{domain}.json")

def load_data(domain):
    f = get_data_file(domain)
    if os.path.exists(f):
        with open(f) as fp:
            return json.load(fp)
    return []

def save_entry(domain, entry):
    data = load_data(domain)
    entry["id"] = str(uuid.uuid4())[:8]
    entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data.append(entry)
    with open(get_data_file(domain), "w") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)
    return entry

def compute_stats(domain):
    data = load_data(domain)
    if not data:
        return None
    df = pd.DataFrame(data)
    stats = {"total": len(df), "numeric": {}, "categorical": {}}

    numeric_cols = [f["name"] for f in DOMAINS[domain]["fields"] if f["type"] == "number"]
    cat_cols = [f["name"] for f in DOMAINS[domain]["fields"] if f["type"] == "select"]

    for col in numeric_cols:
        if col in df.columns:
            s = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(s) > 0:
                stats["numeric"][col] = {
                    "mean": round(float(s.mean()), 2),
                    "median": round(float(s.median()), 2),
                    "std": round(float(s.std()), 2),
                    "min": round(float(s.min()), 2),
                    "max": round(float(s.max()), 2),
                    "q1": round(float(s.quantile(0.25)), 2),
                    "q3": round(float(s.quantile(0.75)), 2),
                }

    for col in cat_cols:
        if col in df.columns:
            counts = df[col].value_counts().to_dict()
            total = sum(counts.values())
            stats["categorical"][col] = {
                k: {"count": int(v), "pct": round(100 * v / total, 1)}
                for k, v in counts.items()
            }

    # Série temporelle
    if "timestamp" in df.columns:
        df["date"] = pd.to_datetime(df["timestamp"]).dt.date.astype(str)
        daily = df.groupby("date").size().to_dict()
        stats["daily"] = daily

    return stats

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    counts = {d: len(load_data(d)) for d in DOMAINS}
    return render_template("index.html", domains=DOMAINS, counts=counts)

@app.route("/collect/<domain>")
def collect(domain):
    if domain not in DOMAINS:
        return redirect(url_for("index"))
    return render_template("collect.html", domain=domain, info=DOMAINS[domain])

@app.route("/submit/<domain>", methods=["POST"])
def submit(domain):
    if domain not in DOMAINS:
        return jsonify({"error": "Domaine invalide"}), 400
    entry = {f["name"]: request.form.get(f["name"], "").strip()
             for f in DOMAINS[domain]["fields"]}
    # Validation
    missing = [f["label"] for f in DOMAINS[domain]["fields"]
               if f.get("required") and not entry.get(f["name"])]
    if missing:
        return jsonify({"error": f"Champs manquants: {', '.join(missing)}"}), 400
    saved = save_entry(domain, entry)
    return jsonify({"success": True, "id": saved["id"], "total": len(load_data(domain))})

@app.route("/analyse/<domain>")
def analyse(domain):
    if domain not in DOMAINS:
        return redirect(url_for("index"))
    stats = compute_stats(domain)
    data = load_data(domain)
    return render_template("analyse.html", domain=domain, info=DOMAINS[domain],
                           stats=stats, fields=DOMAINS[domain]["fields"], data=data[-10:])

@app.route("/api/stats/<domain>")
def api_stats(domain):
    return jsonify(compute_stats(domain) or {})

@app.route("/api/data/<domain>")
def api_data(domain):
    return jsonify(load_data(domain))

@app.route("/api/export/<domain>")
def export_csv(domain):
    data = load_data(domain)
    if not data:
        return jsonify({"error": "Aucune donnée"}), 404
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    from flask import Response
    return Response(csv, mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment;filename={domain}_data.csv"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
