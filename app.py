from flask import Flask, render_template, request, jsonify, send_from_directory
from groq import Groq
from dotenv import load_dotenv
import os
import time
from functools import wraps
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)

CORS(app,
    origins=[
        "https://brewcode.vercel.app",
        "https://brewcode.netlify.app",
        "http://localhost:3000",
        "http://localhost:5000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
    ],
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    supports_credentials=False
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

INFO = """
Eres el asistente virtual de "Brew Code" (antes conocido como DCWB — Diseño y Creación Web Bijagua).

SOBRE NOSOTROS:
Christopher Lamberti Chavarría y Atilio Benavides Arana, estudiantes de Ingeniería en Sistemas desde hace 3 años, basados en Bijagua, Costa Rica.
Nos especializamos en crear páginas web modernas, rápidas y adaptadas a cualquier dispositivo.
Ofrecemos nuestros servicios para emprendedores, negocios locales y cualquier persona que quiera destacar en internet.
Sitio web: https://brewcode.vercel.app/

CONTACTO DIRECTO:
- Christopher: WhatsApp +506 7024-1641
- Atilio: WhatsApp +506 7266-0260
- Email: bijaguadisenoycreacionweb@gmail.com
- Facebook: https://www.facebook.com/profile.php?id=61575006702777
- Instagram: https://www.instagram.com/brewcodes/

SERVICIOS QUE OFRECEMOS:
✔ Diseño 100% personalizado
✔ Adaptable a todos los dispositivos (responsive)
✔ Rendimiento optimizado — carga rápida y animaciones suaves
✔ SEO incluido en todos los proyectos
✔ Hosting gratuito en Vercel con certificado SSL
✔ Aplicaciones web complejas (sistemas, dashboards, integraciones con APIs)

IDEAL PARA:
- Emprendedores
- Portafolios personales
- Eventos y negocios locales
- Pequeñas tiendas

QUÉ PODEMOS HACER:
Páginas informativas: sitios de presentación empresarial, portafolios, landing pages, páginas de eventos.
Sitios con funcionalidades: formularios de contacto, catálogos de productos, sistemas de reservas, galerías interactivas.
Aplicaciones web: sistemas de gestión, dashboards administrativos, plataformas personalizadas, integraciones con APIs.
Servicios adicionales: optimización SEO, mantenimiento mensual, hosting y dominio, capacitación de uso.

RANGO DE PRECIOS ORIENTATIVO:
- Proyectos simples (1–5 páginas): desde ₡50,000 hasta ₡100,000
- Proyectos intermedios (múltiples secciones, formularios, catálogos): desde ₡150,000 hasta ₡350,000
- Proyectos avanzados (apps web, sistemas, integraciones complejas): desde ₡400,000 hasta ₡600,000

IMPORTANTE: Estos son rangos de referencia. El precio final depende de las funcionalidades específicas, el tiempo de desarrollo y los servicios adicionales. Siempre recomendá solicitar una cotización personalizada.

PROCESO DE TRABAJO (4 PASOS):
1. Contacto inicial: el cliente nos contacta por WhatsApp, email o redes. Se agenda una reunión.
2. Reunión de requerimientos: escuchamos las ideas, definimos funcionalidades, alcance, presupuesto y expectativas de diseño.
3. Elaboración de cotización: en promedio 2 días hábiles se entrega una cotización detallada con precio, tiempo estimado y opciones de pago.
4. Inicio del proyecto: una vez aprobada la cotización y recibido el primer pago, comenzamos con comunicación constante.

MODALIDADES DE PAGO:
- Pago único al inicio con descuento especial.
- Pagos fraccionados durante el desarrollo (semanal o mensual) para mayor accesibilidad.
- Pago mensual con mantenimiento: incluye desarrollo + mantenimiento continuo, actualizaciones, soporte técnico, optimización SEO mensual, Google Analytics y Google Search Console.
- La entrega final se realiza solo con el pago completo (excepto en la modalidad mensual con mantenimiento).

MANTENIMIENTO MENSUAL (servicio opcional) INCLUYE:
- Soporte técnico continuo
- Actualizaciones y mejoras del sitio
- Optimización SEO mensual
- Monitoreo con Google Analytics y Search Console
- Reportes mensuales de rendimiento y tráfico
- Corrección de errores sin costo adicional
- Respaldo de seguridad

REVISIONES:
- Revisiones periódicas durante el desarrollo (semanales o según lo acordado).
- Ajustes razonables incluidos durante las revisiones.
- Revisión final antes de la entrega.
- Cambios después de la entrega final tienen costo adicional.
- Con pago mensual con mantenimiento, los cambios están incluidos.

TIEMPOS DE ENTREGA:
- Sitios simples: hasta 90 días hábiles.
- Sitios complejos: hasta 210 días hábiles.
- Los plazos pueden extenderse si el cliente retrasa contenido o retroalimentación.
- Si la entrega se retrasa sin justificación, se aplica un rebajo del 10% del monto total.

CANCELACIONES:
- Si el cliente cancela antes de la entrega final, se retiene el 50% del pago como compensación.

PROPIEDAD DEL CÓDIGO:
- Tras el pago completo, el cliente obtiene derechos de uso totales del sitio web.
- El código fuente se entrega si el cliente lo solicita.
- La documentación técnica tiene costo adicional.

INSTRUCCIONES PARA TI COMO ASISTENTE:
- SIEMPRE respondé en español de Costa Rica. Si el cliente escribe en inglés, respondé en inglés.
- Sé amable, profesional y conciso. Ve al punto, sin redundancias.
- No repitas información que el cliente ya mencionó.
- Siempre recomendá solicitar una cotización personalizada, ya que el precio depende de cada proyecto.
- Si preguntan por precios, mencioná los rangos orientativos y explicá que el costo final se define en la cotización.
- Si tienen un proyecto específico, invitalos a contactar por WhatsApp o usar el formulario en https://brewcode.vercel.app/contacto
- Usá emojis ocasionalmente pero sin exceso.
- Si no sabés algo específico, invitá al cliente a contactar directamente.
- Destacá que son estudiantes comprometidos que ofrecen calidad y dedicación.
- Mencioná que aceptan pagos fraccionados para hacer los servicios más accesibles.
"""

RATE_LIMIT_MESSAGE = "Por favor, esperá un momento antes de enviar otro mensaje. 😊"
ERROR_MESSAGE = "Lo siento, ocurrió un error. Por favor, visitá https://brewcode.vercel.app/ o intentá de nuevo."

last_request_time = {}

def rate_limit(max_per_minute=10):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            now = time.time()
            ip = request.remote_addr
            if ip in last_request_time:
                time_passed = now - last_request_time[ip]
                if time_passed < 60 / max_per_minute:
                    return jsonify({"reply": RATE_LIMIT_MESSAGE}), 429
            last_request_time[ip] = now
            return f(*args, **kwargs)
        return wrapped
    return decorator

@app.route("/")
def index():
    return render_template("widget.html")

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route("/chat", methods=["OPTIONS"])
def chat_preflight():
    # Render necesita un handler explicito para OPTIONS
    return '', 204

@app.route("/chat", methods=["POST"])
@rate_limit(max_per_minute=10)
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Por favor, escribí un mensaje válido."}), 400

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": INFO},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=500
        )

        reply = chat_completion.choices[0].message.content
        return jsonify({"reply": reply}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"reply": ERROR_MESSAGE}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)