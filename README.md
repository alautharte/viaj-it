# 🇮🇹 Italia & Zurich 2026 — Luna de Miel

Webapp compartida para seguimiento del viaje. Construida con Streamlit + Google Sheets.

## Deploy en 5 minutos

### 1. Subir a GitHub

```bash
git init
git add .
git commit -m "Italia 2026 - viaje app"
git remote add origin https://github.com/TU_USUARIO/viaje-italia-2026.git
git push -u origin main
```

**IMPORTANTE:** El archivo `.streamlit/secrets.toml` NO debe subirse a GitHub.
Verificar que `.gitignore` lo excluya.

### 2. Configurar secrets en Streamlit Cloud

En tu app de Streamlit Cloud → **Settings → Secrets**, pegar el mismo contenido
que ya tenés configurado en el screener:

```toml
spreadsheet_id = "ID_DE_TU_GOOGLE_SHEET"

[gcp_service_account]
# ... mismas credenciales que el screener
```

### 3. Google Sheets

Usar el **mismo** Google Sheet del screener. La app crea automáticamente
estas hojas nuevas si no existen:

- `viaje_reservas` — estado de cada reserva, URLs, confirmaciones
- `viaje_gastos` — tracker de gastos en tiempo real
- `viaje_notas` — notas compartidas entre los dos

Asegurarse de que la Service Account tenga acceso al Spreadsheet
(ya debería tenerlo si es el mismo del screener).

### 4. Deploy en Streamlit Cloud

1. Ir a share.streamlit.io
2. "New app" → seleccionar el repo `viaje-italia-2026`
3. Main file: `app.py`
4. Deploy → obtener URL pública

### Uso

- **Reservas**: cargar URL de Airbnb/Booking, número de confirmación y monto.
  El otro lo ve al instante.
- **Itinerario**: cronograma hora por hora con botones directos a Google Maps.
- **Gastos**: tracker de gastos reales vs presupuesto estimado (€4.350).
- **Notas**: notas compartidas entre los dos con categorías.

## Estructura

```
viaje-italia/
├── app.py                          # App principal
├── requirements.txt                # Dependencias
└── .streamlit/
    ├── secrets.toml                # NO subir a GitHub
    └── secrets.toml.example        # Plantilla (sin datos reales)
```
