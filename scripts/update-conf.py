import os
import re
import sys
from pathlib import Path

def ask_input(prompt, default):
    respuesta = input(f"{prompt} [{default}]: ").strip()
    return respuesta if respuesta else default

def normalizar_ruta(ruta):
    return str(Path(ruta).expanduser().resolve())

def main():
    # Obtener rutas desde argumentos o entrada del usuario
    if len(sys.argv) >= 3:
        config_path, addons_dir = sys.argv[1], sys.argv[2]
    else:
        config_path = ask_input("Ruta del archivo de configuración", "./odoo.conf")
        addons_dir = ask_input("Ruta del directorio de addons", "./addons")

    addons_dir = normalizar_ruta(addons_dir)
    config_path = normalizar_ruta(config_path)

    print(f"\n📂 Archivo de configuración: {config_path}")
    print(f"📂 Directorio de addons: {addons_dir}\n")

    # Validar directorio de addons
    if not Path(addons_dir).is_dir():
        print(f"❌ Error: El directorio de addons no existe: {addons_dir}")
        sys.exit(1)

    # Crear archivo de configuración si no existe
    config = Path(config_path)
    if not config.exists():
        print(f"⚙️ Creando nuevo archivo de configuración en: {config_path}")
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text("[options]\naddons_path = \n")

    # Buscar módulos en el directorio de addons
    print("🔍 Buscando módulos...")
    modulos_encontrados = set()
    
    for manifest in Path(addons_dir).rglob("__manifest__.py"):
        directorio_modulo = manifest.parent
        directorio_addons = directorio_modulo.parent
        modulos_encontrados.add(directorio_addons.resolve())

    if not modulos_encontrados:
        print("\n⚠️ No se encontraron módulos válidos")
        print("   Verifica que existan subdirectorios con __manifest__.py")
        sys.exit(0)

    # Procesar rutas existentes en la configuración
    with config.open("r") as f:
        contenido = f.read()

    rutas_existentes = set()
    if match := re.search(r"^addons_path\s*=\s*(.*)$", contenido, flags=re.M):
        for ruta in match.group(1).split(","):
            if ruta.strip():
                try:
                    rutas_existentes.add(Path(ruta.strip()).resolve())
                except Exception as e:
                    print(f"⚠️ Advertencia: Ruta inválida '{ruta}' - {e}")

    # Combinar rutas y actualizar configuración
    todas_rutas = rutas_existentes.union(modulos_encontrados)
    nueva_configuracion = f"addons_path = {','.join(str(p) for p in todas_rutas)}"

    nuevo_contenido = re.sub(
        r"^addons_path\s*=.*$",
        nueva_configuracion,
        contenido,
        flags=re.M,
        count=1
    )

    if nuevo_contenido == contenido:
        nuevo_contenido += f"\n{nueva_configuracion}\n"

    with config.open("w") as f:
        f.write(nuevo_contenido)

    print("\n✔️ Configuración actualizada exitosamente!")
    print(f"📍 Nuevas rutas registradas: {len(todas_rutas)}")
    print("\n".join(f"  → {p}" for p in todas_rutas))

if __name__ == "__main__":
    main()