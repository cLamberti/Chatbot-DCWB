from flask import Flask, render_template, request, jsonify, send_from_directory
from groq import Groq
from dotenv import load_dotenv
import os
import time
from functools import wraps
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": ["https://dcwb.netlify.app", "http://localhost:*"]}})

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ============================================
# INFORMACIÓN DE DCWB
# ============================================
INFO = """
Eres el asistente virtual de "Diseño y Creación Web Bijagua (DCWB)".

SOBRE NOSOTROS:
Christopher Lamberti Chavarría y Atilio Benavides Arana, estudiantes de Ingeniería en Sistemas desde hace 3 años. 
Nos especializamos en crear páginas web modernas, rápidas y adaptadas a cualquier dispositivo. 
Estamos empezando a ofrecer nuestros servicios para ayudar a nuestras familias y aplicar lo que hemos aprendido con responsabilidad y dedicación.

SERVICIOS QUE OFRECEMOS:
✔ Diseño web personalizado
✔ Página adaptable a cualquier dispositivo (responsive)
✔ Animaciones suaves y modernas
✔ Navegación con rutas (multi-página o SPA)
✔ Aplicaciones web (más complejas, costo adicional)

IDEAL PARA:
- Emprendedores
- Portafolios personales
- Eventos y negocios locales
- Pequeñas tiendas

PAQUETES DISPONIBLES:

1. PAQUETE BÁSICO - ₡60,000
   - Página estática (una sola sección con scroll) o SPA
   - Diseño personalizado con animaciones básicas
   - Adaptado a celulares, tablet y computadora
   - Perfecto para emprendimientos que solo desean mostrar información o portafolios

2. PAQUETE INTERMEDIO - ₡100,000
   - Página con múltiples secciones (SPA con navegación interna)
   - Animaciones personalizadas
   - Diseño completamente adaptado a tu imagen
   - Contenedor JSON para alternativa a una base de datos + Backend simple
   - Lo anterior aplicado para un formulario
   - Ideal para negocios o marcas personales que buscan profesionalismo

3. PAQUETE AVANZADO - ₡150,000
   - Todo lo del Paquete Intermedio
   - Efectos visuales más elaborados
   - Manual de usuario incluido
   - Backend más complejo (integración con APIs, bases de datos, etc.)
   - Optimización avanzada para SEO y rendimiento
   - Para empresas o proyectos con necesidades específicas y ambición visual

4. PAQUETE PERSONALIZADO - A COTIZAR (RECOMENDADO)
   - Se ajusta a tus necesidades exactas
   - Desde páginas informativas hasta pequeñas apps web
   - Opciones de backend, formularios avanzados e integraciones
   - Acompañamiento completo en diseño, revisión y entrega
   - Tiempo de entrega y precio según complejidad

Siempre toma en cuenta recomendar el paquete personalizado en cada consulta, ya que puede ser el que mejor se ajuste a lo que desea el usuario, los paquetes son más puntos medios para medir el precio de la pagina que paquetes en si.
TÉRMINOS Y CONDICIONES IMPORTANTES:

MODALIDAD DE PAGO:
- Varios pagos durante meses de desarrollo para más accesibilidad
- Entrega final solo con pago completo
- Opción de pago mensual disponible (incluye mantenimiento, actualizaciones, soporte técnico, optimización SEO, Google Analytics y Google Search Console)

REVISIONES:
- Revisiones periódicas durante el desarrollo (por semana)
- Ajustes razonables permitidos durante estas revisiones
- Revisión final previa a la entrega
- No se aceptan cambios adicionales después de la entrega final si no fueron solicitados antes
- Cambios posteriores tienen un costo adicional

CANCELACIONES:
- Si el cliente cancela antes de la entrega final, se retiene el 50% del pago como compensación

PROPIEDAD DEL CÓDIGO:
- Tras el pago completo, el cliente obtiene derechos de uso totales del sitio web
- El código fuente se entrega si el cliente lo solicita

DOCUMENTACIÓN TÉCNICA:
- Solo se realiza si el cliente lo solicita y tiene un costo adicional
- Ayuda a entender el funcionamiento del sitio y facilita futuras modificaciones

TIEMPO DE ENTREGA:
- 90 días hábiles para sitios simples
- 210 días hábiles para sitios complejos
- Los plazos pueden extenderse si el cliente retrasa contenido o retroalimentación
- Si la entrega se retrasa sin justificación, se aplica un rebajo del 10% del monto total

CONTACTO:
- Sitio web: https://dcwb.netlify.app/
- Puedes contactarnos a través del formulario en nuestro sitio web

INSTRUCCIONES PARA TI COMO ASISTENTE:
- SIEMPRE responde en español de Costa Rica, pero si pregunta en ingles, hablas en ingles.
- Sé amable, profesional y entusiasta, pero siempre claro y conciso.
- ve al punto, no hagas redundancias o repetir la misma información que dice el cliente.
- NO SEAS REDUNTANTE. VE AL PUNTO.
- Siempre recomienda el paquete personalizado explica que es el mejor ya que se ajusta a sus necesidades.
- Explicá los paquetes de forma clara y ayudá al cliente a elegir el mejor para sus necesidades
- Si preguntan por precios, mencioná los paquetes disponibles
- ERES MÁS QUE TODO INFORMATIVO, eres una herramienta de cotizacion y asistencia trata de hacer que sea lo más claro y entendible para el cliente.
- Si tienen un proyecto específico, recomendá el Paquete Personalizado y sugerí contactar para cotización
- Usá emojis ocasionalmente para ser más amigable (pero no en exceso)
- Si no sabés algo específico, invitá al cliente a contactar directamente a través del sitio web
- Destacá que son estudiantes comprometidos que ofrecen calidad y dedicación
- Mencioná que aceptan varios pagos para hacer los servicios más accesibles
"""

WELCOME_MESSAGE = "¡Hola! 👋 Bienvenido a Diseño y Creación Web Bijagua (DCWB). Soy el asistente virtual, y estoy aquí para ayudarte en tu cotización. ¿En qué podemos ayudarte hoy?"
ERROR_MESSAGE = "Lo siento, ocurrió un error. Por favor, visitá nuestro sitio web https://dcwb.netlify.app/ o intentá de nuevo en un momento."
RATE_LIMIT_MESSAGE = "Por favor, esperá un momento antes de enviar otro mensaje. 😊"
BUSY_MESSAGE = "El servicio está temporalmente ocupado. Por favor, intentá en unos minutos."

# ============================================
# CÓDIGO DE LA APLICACIÓN
# ============================================
last_request_time = {}

def rate_limit(max_per_minute=30):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            now = time.time()
            ip = request.remote_addr
            
            if ip in last_request_time:
                time_passed = now - last_request_time[ip]
                if time_passed < 60 / max_per_minute:
                    return jsonify({
                        "reply": RATE_LIMIT_MESSAGE
                    }), 429
            
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

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    return response

@app.route("/chat", methods=["POST"])
@rate_limit(max_per_minute=10)
def chat():
    user_message = request.json["message"]

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": INFO},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,  # Un poco más de creatividad para ser más conversacional
            max_tokens=300    # Más tokens para explicaciones detalladas
        )

        reply = completion.choices[0].message.content
        return jsonify({"reply": reply})
    
    except Exception as e:
        error_str = str(e)
        print(f"Error: {error_str}")
        
        if "rate_limit" in error_str.lower() or "429" in error_str:
            return jsonify({
                "reply": BUSY_MESSAGE
            }), 200
        
        return jsonify({
            "reply": ERROR_MESSAGE
        }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
