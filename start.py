import socket
import subprocess
import sys
import time

HOST = "127.0.0.1"
PORT = 8000


def esperar_backend(host: str, port: int, timeout: int = 60) -> bool:
    """🔌 Verifica si el puerto del Backend (FastAPI) está listo."""
    start_time = time.time()
    print(f"⏳ Esperando a que el backend (FastAPI) se active en el puerto {port}...")

    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            if s.connect_ex((host, port)) == 0:
                print("✅ ¡Backend listo y respondiendo!")
                return True
        time.sleep(0.5)

    print("❌ El backend no respondió dentro del tiempo de espera.")
    return False


def iniciar_aplicacion():
    print("=" * 60)
    print("🚀 INICIANDO ASISTENTE ACADÉMICO RAG")
    print("=" * 60)

    # 1. 🚀 Iniciar FastAPI (sin la opción --reload)
    print("🔥 Lanzando servidor Backend FastAPI...")
    backend_process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            HOST,
            "--port",
            str(PORT),
        ]
    )

    # 2. 🔌 Esperar respuesta del backend
    if esperar_backend(HOST, PORT):
        # 3. 🎨 Iniciar Streamlit UI
        print("🎨 Lanzando interfaz gráfica de Streamlit...")
        frontend_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "app_ui.py",
                "--server.port",
                "8501",
            ]
        )

        print("\n✨ ¡APLICACIÓN INICIADA CON ÉXITO!")
        print("👉 Abre en tu navegador: http://localhost:8501")
        print("💡 Presiona Ctrl+C en esta terminal para detener todo.\n")

        try:
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo aplicación...")
            backend_process.terminate()
            frontend_process.terminate()
            print("✅ Servidores detenidos correctamente.")
    else:
        print("⚠️ Cancelando inicio de Streamlit debido a un error en el backend.")
        backend_process.terminate()


if __name__ == "__main__":
    iniciar_aplicacion()
