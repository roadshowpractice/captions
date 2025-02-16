
# Captions Project Setup

This project involves video processing, captioning, and watermarking with Perl and Python components. Follow the instructions below to set up the development environment and get the project running.

## Prerequisites

Ensure the following software is installed on your system:
- **Perl** (with required modules)
- **Python** (for captioning and watermarking tasks)
- **Git** (for version control)

### Perl
The project uses Perl for some core video processing tasks. You will need to install the required Perl dependencies first.

#### Setting up Perl environment

1. **Install required Perl modules**:
   This project uses `cpan` for managing Perl dependencies. Run the following command to install the necessary modules:

   ```bash
   cpanm --installdeps .
   ```

   If you don't have `cpanm` installed, you can install it via:

   ```bash
   curl -L https://cpanmin.us | perl - App::cpanminus
   ```

2. **Makefile.PL**:
   The Perl environment uses `Makefile.PL` for building dependencies. If you're setting up the environment for the first time, run:

   ```bash
   perl Makefile.PL
   make
   ```

   This will compile any necessary dependencies and get everything set up.

3. **Perl Configuration**:
   Some configurations need to be set in the `conf/` directory:
   - `config.pl` (Modify paths or settings specific to your environment)
   - `watermark_config.pl` (Adjust watermark settings)

   Look for sections marked with `# CUSTOMIZE` for where you should input your own values.

#### Running Perl Scripts

To run the Perl scripts, execute:

```bash
perl bin/4.driver.pl
```

This will initiate the video processing and captioning process.

---

### Python
The Python environment handles caption generation and video watermarking. You will need to set up the Python environment and install necessary dependencies.

#### Setting up the Python environment

1. **Create a virtual environment**:
   
   Create a new virtual environment to isolate the Python dependencies:

   ```bash
   python3 -m venv new-env
   ```

   Activate the virtual environment:
   
   On **macOS/Linux**:
   ```bash
   source new-env/bin/activate
   ```

   On **Windows**:
   ```bash
   new-env\Scripts\activate
   ```

2. **Install Python dependencies**:

   Once the virtual environment is activated, install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

   If you don't have a `requirements.txt`, generate it from your existing environment with:

   ```bash
   pip freeze > requirements.txt
   ```

3. **Python Configuration**:
   The Python scripts use configuration files for customization:
   - `conf/config.json` (Modify paths, API keys, or other project-specific settings)
   - `conf/app_config.json` (Customize paths for different environments, logging, and other system-specific settings)

   Look for sections marked with `# CUSTOMIZE` in these files to input your own values.

#### Running Python Scripts

To run the Python scripts, execute:

```bash
python bin/call_captions.py
```

This script will generate captions for the videos in the specified input directory.

---

## Configuration Files

### **conf/config.json**:

This file contains the main configuration for video processing, including watermarking, captions, and Ken Burns effects.

- **video_download**: Settings for downloading video content.
- **watermark_config**: Settings for watermark appearance, including font, colors, and positions.
- **ken_burns**: Settings for the Ken Burns effect, including slide length and brightness.
- **captions**: Configuration for caption appearance, positions, and timing.

### **conf/app_config.json**:

This file contains environment-specific settings for different operating systems (Darwin for macOS and Linux). Modify the following fields to suit your local environment:

- **python_path**: Path to the Python interpreter (make sure it's the one in your virtual environment).
- **base_dir**: Base directory where the project is located.
- **log_dir**: Directory for log files.
- **image_dir**: Directory where images are stored (used for watermarks).
- **resize_dir**: Directory for resized images (if applicable).
- **cookie_path**: Path to the cookies file for video downloads.
- **logging**: Log settings, including logging level, log file paths, and console output.

### Customizable Values

- **Paths**: Many scripts rely on specific paths for input and output files. These can be adjusted in the `config.json` and `app_config.json` files.
  - Example: `source_path`, `cookie_path`, `image_dir`.
- **Logging**: Customize log levels (DEBUG, INFO, etc.) and log file paths for debugging and monitoring.
- **Watermark Settings**: Adjust watermark options such as `font`, `font_size`, and `position` in `watermark_config`.

---

## Troubleshooting

- **Permission errors**: Ensure all files in the project directory are readable and writable by the user executing the scripts.
- **Missing modules**: If you encounter errors about missing Perl or Python modules, run the installation commands mentioned above for each respective environment.
- **Git Issues**: Make sure your Git configuration is set up globally (e.g., with `git config --global credential.helper cache`), especially if pushing/pulling from a remote repository.

---

## Version Control

This project is managed using Git. To clone the repository, run:

```bash
git clone https://github.com/Perl72/captions.git
```

To update your local copy, run:

```bash
git pull origin main
```

To commit your changes, use:

```bash
git add .
git commit -m "Your commit message"
git push origin main
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
