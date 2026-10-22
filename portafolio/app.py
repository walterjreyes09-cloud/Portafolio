"""
Portafolio personal en Flask.
Ejecutar:  python app.py   ->  http://127.0.0.1:5000
Panel de administración:  http://127.0.0.1:5000/admin
"""
import json
import os
import re
import shutil
import time
import uuid
from functools import wraps
from pathlib import Path

from flask import (Flask, abort, flash, redirect, render_template, request,
                   session, url_for)
from werkzeug.utils import secure_filename

BASE = Path(__file__).parent
DATA_FILE = BASE / "data" / "site.json"
UPLOADS = BASE / "static" / "uploads"

# Cambia la contraseña con una variable de entorno:  set ADMIN_PASSWORD=tuClave
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

IMAGES = {"png", "jpg", "jpeg", "gif", "webp"}
VIDEOS = {"mp4", "webm", "mov"}
DOCS = {"pdf"}
ALLOWED = IMAGES | VIDEOS | DOCS

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cambia-esta-clave-secreta")
app.config["MAX_CONTENT_LENGTH"] = 300 * 1024 * 1024  # 300 MB por envío

DEFAULT_DATA = {
    "name": "Tu Nombre",
    "role": "Desarrollador y creador digital",
    "tagline": "Construyo proyectos con código limpio y diseño sólido.",
    "about": (
        "Escribe aquí quién eres, qué te apasiona y cómo trabajas.\n\n"
        "Puedes separar párrafos con una línea en blanco."
    ),
    "photo": "img/perfil.jpg",
    "photo_v": "1",
    "services": [
        {"title": "Desarrollo web", "text": "Sitios y aplicaciones a la medida, rápidos y fáciles de mantener."},
        {"title": "Automatización con Python", "text": "Scripts y herramientas que ahorran horas de trabajo repetitivo."},
        {"title": "Diseño de interfaces", "text": "Pantallas claras y con carácter, pensadas para quien las usa."},
    ],
    "skills": [
        {"name": "Python", "level": 85},
        {"name": "HTML y CSS", "level": 80},
        {"name": "JavaScript", "level": 65},
        {"name": "Diseño gráfico", "level": 70},
    ],
    "contact": {"email": "", "whatsapp": "", "instagram": "", "github": "", "linkedin": ""},
    "folders": [
        {"slug": "carpeta-1", "name": "Carpeta 1", "description": "Describe qué trabajos van en esta carpeta.", "works": []},
        {"slug": "carpeta-2", "name": "Carpeta 2", "description": "Describe qué trabajos van en esta carpeta.", "works": []},
    ],
}


# ---------- datos ----------
def load():
    if not DATA_FILE.exists():
        save(DEFAULT_DATA)
        for f in DEFAULT_DATA["folders"]:
            (UPLOADS / f["slug"]).mkdir(parents=True, exist_ok=True)
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save(data):
    DATA_FILE.parent.mkdir(exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def slugify(text):
    text = re.sub(r"[^a-z0-9]+", "-", text.lower().strip())
    return text.strip("-") or "carpeta"


def kind_of(filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    return "image" if ext in IMAGES else "video" if ext in VIDEOS else "pdf"


def ext_ok(filename, allowed=ALLOWED):
    return "." in filename and filename.rsplit(".", 1)[-1].lower() in allowed


def get_folder(data, slug):
    return next((f for f in data["folders"] if f["slug"] == slug), None)


def login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not session.get("admin"):
            return redirect(url_for("login", next=request.path))
        return view(*a, **kw)
    return wrapped


@app.context_processor
def inject():
    return {"site": load(), "is_admin": bool(session.get("admin")), "kind_of": kind_of}


# ---------- páginas públicas ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/carpeta/<slug>")
def carpeta(slug):
    folder = get_folder(load(), slug)
    if not folder:
        abort(404)
    return render_template("carpeta.html", folder=folder)


# ---------- acceso ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            nxt = request.args.get("next", "")
            return redirect(nxt if nxt.startswith("/") and not nxt.startswith("//") else url_for("admin"))
        flash("Contraseña incorrecta.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ---------- administración ----------
@app.route("/admin")
@login_required
def admin():
    data = load()
    services = "\n".join(f"{s['title']} | {s['text']}" for s in data["services"])
    skills = "\n".join(f"{s['name']}:{s['level']}" for s in data["skills"])
    return render_template("admin.html", services_text=services, skills_text=skills)


@app.post("/admin/perfil")
@login_required
def guardar_perfil():
    data = load()
    for key in ("name", "role", "tagline", "about"):
        data[key] = request.form.get(key, "").strip()

    data["services"] = []
    for line in request.form.get("services", "").splitlines():
        if line.strip():
            title, _, text = line.partition("|")
            data["services"].append({"title": title.strip(), "text": text.strip()})

    data["skills"] = []
    for line in request.form.get("skills", "").splitlines():
        if line.strip():
            name, _, lvl = line.partition(":")
            try:
                level = max(0, min(100, int(lvl.strip())))
            except ValueError:
                level = 50
            data["skills"].append({"name": name.strip(), "level": level})

    for key in data["contact"]:
        data["contact"][key] = request.form.get(f"c_{key}", "").strip()

    save(data)
    flash("Perfil guardado.", "ok")
    return redirect(url_for("admin"))


@app.post("/admin/foto")
@login_required
def cambiar_foto():
    file = request.files.get("photo")
    if not file or not file.filename or not ext_ok(file.filename, IMAGES):
        flash("Sube una imagen JPG, PNG o WEBP.", "error")
        return redirect(url_for("admin"))
    ext = file.filename.rsplit(".", 1)[-1].lower()
    name = f"perfil.{ext}"
    file.save(BASE / "static" / "img" / name)
    data = load()
    data["photo"] = f"img/{name}"
    data["photo_v"] = str(int(time.time()))
    save(data)
    flash("Foto de perfil actualizada.", "ok")
    return redirect(url_for("admin"))


@app.post("/admin/carpeta/crear")
@login_required
def crear_carpeta():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Escribe un nombre para la carpeta.", "error")
        return redirect(url_for("admin"))
    data = load()
    base = slugify(name)
    slug, n = base, 2
    while get_folder(data, slug):
        slug, n = f"{base}-{n}", n + 1
    data["folders"].append({
        "slug": slug, "name": name,
        "description": request.form.get("description", "").strip(), "works": [],
    })
    (UPLOADS / slug).mkdir(parents=True, exist_ok=True)
    save(data)
    flash(f"Carpeta «{name}» creada.", "ok")
    return redirect(url_for("admin") + f"#f-{slug}")


@app.post("/admin/carpeta/<slug>/editar")
@login_required
def editar_carpeta(slug):
    data = load()
    folder = get_folder(data, slug) or abort(404)
    folder["name"] = request.form.get("name", "").strip() or folder["name"]
    folder["description"] = request.form.get("description", "").strip()
    save(data)
    flash("Carpeta actualizada.", "ok")
    return redirect(url_for("admin") + f"#f-{slug}")


@app.post("/admin/carpeta/<slug>/eliminar")
@login_required
def eliminar_carpeta(slug):
    data = load()
    folder = get_folder(data, slug) or abort(404)
    data["folders"].remove(folder)
    shutil.rmtree(UPLOADS / slug, ignore_errors=True)
    save(data)
    flash("Carpeta eliminada.", "ok")
    return redirect(url_for("admin"))


@app.post("/admin/carpeta/<slug>/subir")
@login_required
def subir_trabajos(slug):
    data = load()
    folder = get_folder(data, slug) or abort(404)
    (UPLOADS / slug).mkdir(parents=True, exist_ok=True)
    title = request.form.get("title", "").strip()
    count = 0
    for file in request.files.getlist("files"):
        if not file or not file.filename:
            continue
        if not ext_ok(file.filename):
            flash(f"«{file.filename}» no es un formato permitido.", "error")
            continue
        safe = secure_filename(file.filename) or "archivo"
        stored = f"{uuid.uuid4().hex[:8]}_{safe}"
        file.save(UPLOADS / slug / stored)
        folder["works"].append({
            "id": uuid.uuid4().hex[:10],
            "title": title or Path(safe).stem.replace("_", " "),
            "file": stored,
        })
        count += 1
    save(data)
    if count:
        flash(f"{count} archivo(s) subido(s) a «{folder['name']}».", "ok")
    return redirect(url_for("admin") + f"#f-{slug}")


@app.post("/admin/carpeta/<slug>/trabajo/<work_id>/eliminar")
@login_required
def eliminar_trabajo(slug, work_id):
    data = load()
    folder = get_folder(data, slug) or abort(404)
    work = next((w for w in folder["works"] if w["id"] == work_id), None) or abort(404)
    folder["works"].remove(work)
    (UPLOADS / slug / work["file"]).unlink(missing_ok=True)
    save(data)
    flash("Trabajo eliminado.", "ok")
    return redirect(url_for("admin") + f"#f-{slug}")


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


@app.errorhandler(413)
def too_big(_):
    flash("El envío supera los 300 MB. Sube menos archivos a la vez.", "error")
    return redirect(url_for("admin"))


if __name__ == "__main__":
    load()  # crea data/site.json y las carpetas iniciales la primera vez
    app.run(debug=True, port=5000)
