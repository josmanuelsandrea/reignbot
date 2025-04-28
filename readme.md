# Revs And Reigns Bot

Revs And Reigns es un bot de Discord escrito en Python que facilita la gestión de partidas de estrategia basadas en reinos y diplomacia.

## Configuración del entorno

1. **Crear y activar el entorno virtual**
   ```bash
   python3 -m venv .venv
   # Linux/macOS
   source .venv/bin/activate
   # Windows
   .venv\\Scripts\\activate
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Crear archivo `.env`** en la raíz del proyecto con el siguiente contenido (sin espacios alrededor del `=`):
   ```ini
   DISCORD_TOKEN=TOKEN
   COMMAND_PREFIX=!
   GUILD_ID=1366279954240765982
   ```

4. **Iniciar el bot**
   ```bash
   python bot.py
   ```

