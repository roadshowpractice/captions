
# Configuración del Proyecto de Subtítulos

Este proyecto implica procesamiento de video, subtitulado y marca de agua con componentes en Perl y Python. Sigue las instrucciones a continuación para configurar el entorno de desarrollo y poner en marcha el proyecto.

## Requisitos Previos

Asegúrate de tener instalado el siguiente software en tu sistema:
- **Perl** (con los módulos requeridos)
- **Python** (para tareas de subtitulado y marca de agua)
- **Git** (para control de versiones)

### Perl
El proyecto utiliza Perl para algunas tareas principales de procesamiento de video. Necesitarás instalar primero las dependencias necesarias de Perl.

#### Configuración del entorno Perl

1. **Instalar los módulos Perl requeridos**:  
   Este proyecto utiliza `cpan` para gestionar las dependencias de Perl. Ejecuta el siguiente comando para instalar los módulos necesarios:

   ```bash
   cpanm --installdeps .
   ```

   Si no tienes `cpanm` instalado, puedes instalarlo con:

   ```bash
   curl -L https://cpanmin.us | perl - App::cpanminus
   ```

2. **Makefile.PL**:  
   El entorno Perl usa `Makefile.PL` para compilar dependencias. Si es la primera vez que configuras el entorno, ejecuta:

   ```bash
   perl Makefile.PL
   make
   ```

   Esto compilará las dependencias necesarias y configurará todo.

#### Ejecutar Scripts Perl

Para ejecutar los scripts Perl, ejecuta:

```
prove -lv t/17.download.t
perl -Ilib bin/4.driver.pl
perl -Ilib t/18.download.t 
python bin/call_captions.py /media/fritz/9766-DD0B/2025-06-18/Tim_Ballard_20250618_watermarked.mp4
```

Esto iniciará el proceso de procesamiento de video y generación de subtítulos.

---

### Python
El entorno Python gestiona la generación de subtítulos y la inserción de marca de agua en los videos. Necesitarás configurar el entorno y las dependencias necesarias.

#### Configuración del entorno Python

1. **Crear un entorno virtual**:

   Crea un nuevo entorno virtual para aislar las dependencias:

   ```bash
   python3 -m venv new-env
   ```

   Activa el entorno virtual:

   En **macOS/Linux**:
   ```bash
   source new-env/bin/activate
   ```

   En **Windows**:
   ```bash
   new-env\Scripts\activate
   ```

2. **Instalar dependencias de Python**:

   Una vez activado el entorno virtual, instala los paquetes necesarios:

   ```bash
   pip install -r requirements.txt
   ```

   Si no tienes un `requirements.txt`, puedes generarlo desde tu entorno actual con:

   ```bash
   pip freeze > requirements.txt
   ```

3. **Configuración de Python**:
   Los scripts Python utilizan archivos de configuración para su personalización:
   - `conf/config.json` (Modifica rutas, claves API u otras configuraciones específicas del proyecto)
   - `conf/app_config.json` (Personaliza rutas para distintos entornos, registros y otras configuraciones del sistema)

   Busca secciones marcadas con `# CUSTOMIZE` para ingresar tus propios valores.

#### Ejecutar Scripts Python

Para ejecutar los scripts Python, ejecuta:

```
python bin/call_captions.py /media/fritz/9766-DD0B/2025-06-18/Tim_Ballard_20250618_watermarked.mp4
```

Este script generará subtítulos para los videos en el directorio de entrada especificado.

---

## Archivos de Configuración

### **conf/config.json**:

Este archivo contiene la configuración principal para el procesamiento de video, incluyendo marca de agua, subtítulos y efectos Ken Burns.

- **video_download**: Configuración para descargar contenido de video.
- **watermark_config**: Configuración de la apariencia de la marca de agua: fuente, colores y posiciones.
- **ken_burns**: Configuración del efecto Ken Burns: duración de las diapositivas y brillo.
- **captions**: Configuración de los subtítulos: apariencia, posiciones y tiempos.

### **conf/app_config.json**:

Este archivo contiene configuraciones específicas del entorno para distintos sistemas operativos (Darwin para macOS y Linux). Modifica los siguientes campos según tu entorno:

- **python_path**: Ruta al intérprete de Python (asegúrate de que sea el de tu entorno virtual).
- **base_dir**: Directorio base del proyecto.
- **log_dir**: Directorio para los archivos de registro.
- **image_dir**: Directorio donde se almacenan las imágenes (usado para marcas de agua).
- **logging**: Configuración de registros: nivel, rutas de archivos y salida por consola.

### Valores Personalizables

- **Rutas**: Muchos scripts dependen de rutas específicas para archivos de entrada y salida. Estas pueden ajustarse en `config.json` y `app_config.json`.
  - Ejemplo: `source_path`, `cookie_path`, `image_dir`.
- **Registro**: Personaliza los niveles de log (DEBUG, INFO, etc.) y rutas para monitoreo.
- **Marca de Agua**: Ajusta opciones como `font`, `font_size`, y `position` en `watermark_config`.

---

## Control de Versiones

Este proyecto está gestionado con Git. Para clonar el repositorio, ejecuta:

```bash
git clone https://github.com/Perl72/captions.git
```

Para actualizar tu copia local:

```bash
git pull origin main
```

Para subir tus cambios:

```bash
git add .
git commit -m "Tu mensaje de commit"
git push origin main
```

---

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
