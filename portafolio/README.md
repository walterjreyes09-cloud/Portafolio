# Mi portafolio (Flask)

## Cómo ejecutarlo
1. Instala Python 3.9 o superior.
2. En esta carpeta:
   ```
   pip install -r requirements.txt
   python app.py
   ```
3. Abre http://127.0.0.1:5000

## Panel de administración
- Entra en http://127.0.0.1:5000/login (o el enlace «Administrar» del pie de página).
- Contraseña inicial: `admin123`. Cámbiala antes de publicar:
  - Windows (PowerShell): `$env:ADMIN_PASSWORD="tuClaveSegura"; $env:SECRET_KEY="otraClaveLarga"; python app.py`
  - Mac / Linux: `ADMIN_PASSWORD=tuClaveSegura SECRET_KEY=otraClaveLarga python app.py`
- Desde el panel puedes cambiar tu foto, editar tu información, crear carpetas
  (Carpeta 1, Carpeta 2, las que quieras) y subir imágenes, videos (mp4, webm, mov) y PDF.

## Dónde se guardan las cosas
- Textos y carpetas: `data/site.json`
- Archivos subidos: `static/uploads/<carpeta>/`
- Foto de perfil: `static/img/`
